"""Métricas del radar: impulso (0-100), horizonte ajustado por señales y cambios.

Sin red. Todo se calcula con los datos que deja radar.py; así se puede probar.
"""
from __future__ import annotations

import math
import statistics
from datetime import date, timedelta

TIPOS_ORDEN = ["lanzamiento", "inversion", "investigacion", "regulacion", "otro"]

PESOS_IMPULSO = {"wiki": 0.30, "papers": 0.20, "volumen": 0.30, "aceleracion": 0.20}


def percentiles(valores: dict[str, float | None]) -> dict[str, float | None]:
    """Rango percentil 0..1 de cada valor entre los no nulos (empates = promedio)."""
    vals = sorted(v for v in valores.values() if v is not None)
    n = len(vals)
    out = {}
    for k, v in valores.items():
        if v is None or n == 0:
            out[k] = None
        elif n == 1:
            out[k] = 0.5
        else:
            menores = sum(1 for x in vals if x < v)
            iguales = sum(1 for x in vals if x == v)
            out[k] = (menores + (iguales - 1) / 2) / (n - 1)
    return out


def crecimiento_wiki(serie: dict[str, int]) -> float | None:
    """ln(promedio últimos 3 meses / 3 anteriores), con suavizado para bases chicas."""
    meses = sorted(serie)
    if len(meses) < 6:
        return None
    ult = [serie[m] for m in meses[-3:]]
    prev = [serie[m] for m in meses[-6:-3]]
    return math.log((sum(ult) / 3 + 50) / (sum(prev) / 3 + 50))


def crecimiento_papers(reciente: int | None, previo: int | None) -> float | None:
    if reciente is None or previo is None:
        return None
    return math.log((reciente + 20) / (previo + 20))


def conteo_dias(conteos: dict[str, dict[str, list[int]]], tid: str, hoy: date, dias: int, desde: int = 0) -> int:
    """Señales de la tendencia entre hoy-desde-dias (excl.) y hoy-desde (incl.)."""
    total = 0
    for i in range(desde, desde + dias):
        d = (hoy - timedelta(days=i)).isoformat()
        fila = conteos.get(d, {}).get(tid)
        if fila:
            total += sum(fila)
    return total


def mezcla(conteos, tid: str, hoy: date, dias: int = 60) -> dict[str, int]:
    m = {t: 0 for t in TIPOS_ORDEN}
    for i in range(dias):
        fila = conteos.get((hoy - timedelta(days=i)).isoformat(), {}).get(tid)
        if fila:
            for t, n in zip(TIPOS_ORDEN, fila):
                m[t] += n
    return m


def serie_semanal(conteos, tid: str, hoy: date, semanas: int = 12) -> list[int]:
    """Señales por semana (7 días móviles), de la más antigua a la actual."""
    return [conteo_dias(conteos, tid, hoy, 7, desde=7 * s) for s in range(semanas - 1, -1, -1)]


def dias_de_historia(inicio: str | None, hoy: date) -> int:
    """Días desde que el radar empezó a medir. No se usa la fecha de la noticia más vieja:
    en la primera corrida las búsquedas traen notas de semanas atrás, pero solo algunas,
    y compararlas con la semana actual (completa) inventaría una aceleración."""
    if not inicio:
        return 0
    return max(0, (hoy - date.fromisoformat(inicio)).days)


def impulso(tendencias: list[dict], wiki: dict, papers: dict, conteos: dict, hoy: date, inicio: str | None = None) -> dict[str, dict]:
    """Impulso relativo 0-100 de cada tendencia + sus componentes crudos."""
    ids = [t["id"] for t in tendencias]
    historia = dias_de_historia(inicio, hoy)
    crudo = {"wiki": {}, "papers": {}, "volumen": {}, "aceleracion": {}}
    for tid in ids:
        crudo["wiki"][tid] = crecimiento_wiki(wiki.get(tid, {}).get("serie", {}))
        p = papers.get(tid, {})
        crudo["papers"][tid] = crecimiento_papers(p.get("reciente"), p.get("previo"))
        n14 = conteo_dias(conteos, tid, hoy, 14)
        crudo["volumen"][tid] = math.log1p(n14) if conteos else None
        if historia >= 35:
            n7 = conteo_dias(conteos, tid, hoy, 7)
            base = conteo_dias(conteos, tid, hoy, 28, desde=7) / 4
            crudo["aceleracion"][tid] = math.log((n7 + 2) / (base + 2))
        else:
            crudo["aceleracion"][tid] = None
    pct = {k: percentiles(v) for k, v in crudo.items()}
    out = {}
    for tid in ids:
        num = den = 0.0
        for k, w in PESOS_IMPULSO.items():
            v = pct[k][tid]
            if v is not None:
                num += w * v
                den += w
        valor = round(100 * num / den) if den else None
        out[tid] = {"impulso": valor, "componentes": {k: (None if pct[k][tid] is None else round(100 * pct[k][tid])) for k in PESOS_IMPULSO},
                    "crudo": {k: (None if crudo[k][tid] is None else round(crudo[k][tid], 3)) for k in crudo}}
    return out


def nivel_impulso(valor: int | None) -> str:
    if valor is None:
        return "sin datos"
    return "alto" if valor >= 70 else ("medio" if valor >= 40 else "bajo")


def horizontes(tendencias: list[dict], conteos: dict, hoy: date, dias: int = 60) -> dict[str, dict]:
    """Años hasta la adopción: base editorial ajustada por la mezcla de señales.

    "Mercado" = proporción de lanzamientos e inversiones frente a investigación en
    60 días. Lo normal es que una tendencia lejana tenga más investigación que una
    cercana, así que no se compara con la media del radar sino con lo esperado
    para su horizonte (recta mercado ~ log(años base) ajustada sobre todas las
    tendencias). Si tiene más mercado del esperado, se acerca; menos, se aleja.
    El ajuste es proporcional a la base (±30 % como máximo) y se atenúa con pocas
    señales.
    """
    datos = {}
    for t in tendencias:
        m = mezcla(conteos, t["id"], hoy, dias)
        mercado = m["lanzamiento"] + m["inversion"]
        n = mercado + m["investigacion"]
        datos[t["id"]] = (mercado / n if n else None, n, m)
    puntos = [(math.log(float(t["anios"]) + 0.5), datos[t["id"]][0]) for t in tendencias
              if datos[t["id"]][0] is not None and datos[t["id"]][1] >= 8]
    recta = None
    if len(puntos) >= 6:
        # Theil–Sen: pendiente = mediana de las pendientes entre pares; resiste tendencias atípicas
        pendientes = [(y2 - y1) / (x2 - x1) for i, (x1, y1) in enumerate(puntos) for x2, y2 in puntos[i + 1:] if abs(x2 - x1) > 1e-9]
        b = statistics.median(pendientes) if pendientes else 0.0
        recta = (statistics.median(y - b * x for x, y in puntos), b)
    out = {}
    for t in tendencias:
        share, n, m = datos[t["id"]]
        base = float(t["anios"])
        k = 0.0
        esperado = None
        if recta is not None:
            esperado = max(0.0, min(1.0, recta[0] + recta[1] * math.log(base + 0.5)))
            if share is not None and n >= 8:
                k = max(-0.3, min(0.3, (esperado - share) * 1.5)) * n / (n + 10)
        anios = max(0.5, min(12.0, base * math.exp(k)))
        out[t["id"]] = {"anios": round(anios, 2), "base": base, "ajuste": round(k, 3),
                        "mercado": None if share is None else round(share, 3), "n": n,
                        "esperado": None if esperado is None else round(esperado, 3), "mezcla": m}
    return out


def cambios(historial: dict[str, dict[str, list]], hoy: date, nombres: dict[str, str], dias: int = 7) -> dict:
    """Comparación con hace ~7 días: quién acelera, quién se enfría, quién se acerca o se aleja."""
    clave_hoy = hoy.isoformat()
    if clave_hoy not in historial:
        return {"dias": 0, "acelera": [], "enfria": [], "acerca": [], "aleja": []}
    anteriores = sorted(d for d in historial if date.fromisoformat(d) <= hoy - timedelta(days=dias - 1))
    if not anteriores:
        return {"dias": 0, "acelera": [], "enfria": [], "acerca": [], "aleja": []}
    ref = anteriores[-1]
    a, b = historial[ref], historial[clave_hoy]
    delta_imp, delta_anios = [], []
    for tid, (imp, anios) in b.items():
        if tid not in a or tid not in nombres:
            continue
        imp0, anios0 = a[tid]
        if imp is not None and imp0 is not None:
            delta_imp.append((imp - imp0, tid))
        if anios is not None and anios0 is not None:
            delta_anios.append((round(anios - anios0, 2), tid))
    delta_imp.sort()
    delta_anios.sort()
    fmt = lambda lst: [{"id": tid, "delta": d} for d, tid in lst]
    return {
        "dias": (hoy - date.fromisoformat(ref)).days,
        "acelera": fmt([x for x in reversed(delta_imp) if x[0] >= 8][:5]),
        "enfria": fmt([x for x in delta_imp if x[0] <= -8][:5]),
        "acerca": fmt([x for x in delta_anios if x[0] <= -0.25][:5]),
        "aleja": fmt([x for x in reversed(delta_anios) if x[0] >= 0.25][:5]),
    }
