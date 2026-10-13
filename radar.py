"""Radar de Innovación — recolecta señales del mundo, las mide y genera la página.

Uso:
  python radar.py                  corrida completa (red) + página en site/
  python radar.py --sin-red        solo regenera la página con los datos guardados
  python radar.py --sin-bing       omite las búsquedas por tendencia (más rápido)
  python radar.py --forzar-diario  vuelve a medir Wikipedia y OpenAlex aunque ya se hizo hoy
  python radar.py --abrir          abre la página al terminar

Fuentes: feeds RSS de medios (fuentes.json), Bing News RSS por tendencia,
vistas de Wikipedia (interés público) y OpenAlex (producción científica).
Si una fuente cae, se conservan sus datos anteriores: la página nunca queda vacía.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import shutil
import sys
import time
import webbrowser
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import clasificar as C
import fuentes as F
import metricas as M

RAIZ = Path(__file__).resolve().parent
DATOS = RAIZ / "datos"
SITE = RAIZ / "site"

RETENCION_VISTOS = 46       # días que se recuerda una URL ya contada
RETENCION_SENAL = 45        # días que una noticia puede mostrarse
RETENCION_CONTEOS = 400     # días de conteos diarios por tendencia
MAX_POR_TENDENCIA = 30
MAX_ULTIMAS = 120
MAX_FUERA = 40

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def log(*a):
    print("[radar]", *a, flush=True)


def cargar(nombre: str, defecto):
    p = DATOS / nombre
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as e:
            log(f"aviso: {nombre} ilegible ({e}); se empieza de cero")
    return defecto


def guardar(nombre: str, obj, compacto: bool = False):
    DATOS.mkdir(exist_ok=True)
    tmp = DATOS / (nombre + ".tmp")
    texto = json.dumps(obj, ensure_ascii=False, separators=(",", ":")) if compacto else json.dumps(obj, ensure_ascii=False, indent=1)
    tmp.write_text(texto, encoding="utf-8")
    os.replace(tmp, DATOS / nombre)


# ---------------------------------------------------------------- recolección

def recolectar_rss(feeds: list[dict], estado_fuentes: dict) -> list[dict]:
    def uno(feed):
        try:
            if not F.permitido(feed["url"]):
                return feed, [], "robots.txt no lo permite"
            items = F.leer_feed(feed)
            return feed, items, None
        except Exception as e:  # una fuente caída no detiene el radar
            return feed, [], f"{type(e).__name__}: {str(e)[:120]}"

    out = []
    with ThreadPoolExecutor(max_workers=8) as ex:
        for feed, items, error in ex.map(uno, feeds):
            ef = estado_fuentes.setdefault(feed["nombre"], {})
            ef["tipo"] = "rss"
            if error:
                ef["error"] = error
                ef["fallo"] = F.ahora().isoformat(timespec="minutes")
                log(f"  ✗ {feed['nombre']}: {error}")
            else:
                ef.pop("error", None)
                ef["ok"] = F.ahora().isoformat(timespec="minutes")
                ef["n"] = len(items)
            for it in items:
                it.update(origen="rss", nivel=feed.get("nivel", 2), idioma=feed.get("idioma", "en"))
            out.extend(items)
    return out


def recolectar_bing(tendencias: list[dict], estado_fuentes: dict, nivel1: list[str]) -> list[dict]:
    ef = estado_fuentes.setdefault("Bing News (búsqueda por tendencia)", {"tipo": "busqueda"})
    if not F.permitido(F.BING + "test"):
        ef["error"] = "robots.txt no lo permite"
        log("  ✗ Bing News: robots.txt no lo permite; se omite")
        return []
    nivel1_norm = [n.lower() for n in nivel1]
    out, fallos, total = [], 0, 0
    for t in tendencias:
        for q in t["bing"]:
            if total:
                time.sleep(1.0)
            total += 1
            try:
                items = F.bing_news(q)
            except Exception as e:
                fallos += 1
                log(f"  ✗ Bing «{q}»: {type(e).__name__}: {str(e)[:80]}")
                continue
            for it in items:
                f = (it.get("fuente") or "").lower()
                it.update(origen="bing", consulta_de=t["id"], idioma="en",
                          nivel=1 if any(n in f for n in nivel1_norm) else 3)
            out.extend(items)
    if fallos == total:
        ef["error"] = "todas las búsquedas fallaron"
        ef["fallo"] = F.ahora().isoformat(timespec="minutes")
    else:
        ef.pop("error", None)
        ef["ok"] = F.ahora().isoformat(timespec="minutes")
        ef["n"] = len(out)
        ef["fallos"] = fallos
    return out


# ---------------------------------------------------------------- procesamiento

def puntaje(s: dict, ahora: datetime) -> float:
    base = {1: 3.0, 2: 2.0, 3: 1.0}.get(s.get("nivel", 3), 1.0)
    base += {"lanzamiento": 1.0, "inversion": 1.0, "investigacion": 1.0, "regulacion": 0.5}.get(s.get("tipo"), 0.0)
    base += 0.5 if s.get("nov") else 0.0
    base += 0.5 * min(s.get("n", 1) - 1, 4)
    edad = max(0.0, (ahora - datetime.fromisoformat(s["d"])).total_seconds() / 86400)
    return base * math.exp(-edad / 10)


def agregar_agrupando(lista: list[dict], s: dict) -> bool:
    """Añade s a la lista; si ya hay una nota casi igual (misma historia en otro medio), la agrupa."""
    h = C.huella(C.normalizar(s["t"]))
    for e in lista:
        if e["id"] == s["id"]:
            return False
        if C.parecidos(h, C.huella(C.normalizar(e["t"]))):
            e["n"] = e.get("n", 1) + 1
            otras = e.setdefault("otras", [])
            if s["f"] != e["f"] and s["f"] not in otras and len(otras) < 5:
                otras.append(s["f"])
            if s.get("nivel", 3) < e.get("nivel", 3):  # gana el medio de mayor nivel
                for k in ("id", "t", "u", "f", "d", "r", "i", "nivel", "tipo"):
                    if k in s:
                        e[k] = s[k]
                if s["f"] in otras:
                    otras.remove(s["f"])
            return False
    lista.append(s)
    return True


def procesar(items: list[dict], cat: dict, conf: dict, estado: dict, senales: dict, ahora: datetime) -> dict:
    compiladas = C.compilar_tendencias(cat["tendencias"])
    excluidos = {m.lower() for m in conf.get("medios_excluidos", [])}
    vistos_dict = estado.setdefault("vistos", {})
    vistos = set()
    for ids in vistos_dict.values():
        vistos.update(ids.split())
    conteos = estado.setdefault("conteos", {})
    por_t = senales.setdefault("por_tendencia", {})
    ultimas = senales.setdefault("ultimas", [])
    fuera = senales.setdefault("fuera", [])
    hoy = ahora.date().isoformat()
    nuevos_hoy = vistos_dict.get(hoy, "").split()
    stats = {"leidas": len(items), "nuevas": 0, "repetidas": 0, "excluidas": {}, "sin_tendencia": 0, "viejas": 0}
    limite = ahora - timedelta(days=RETENCION_SENAL)

    for it in items:
        fecha = it.get("fecha") or ahora
        if fecha > ahora + timedelta(hours=6):
            fecha = ahora
        if fecha < limite:
            stats["viejas"] += 1
            continue
        tn, rn = C.normalizar(it["titulo"]), C.normalizar(it.get("resumen", ""))
        motivo = C.motivo_exclusion(tn, it.get("fuente", ""), excluidos)
        if motivo:
            stats["excluidas"][motivo] = stats["excluidas"].get(motivo, 0) + 1
            continue
        tend = C.tendencias_de(tn, rn, compiladas, it.get("consulta_de"))
        novedad = C.es_novedad(tn, rn)
        if not tend and not (it["origen"] == "rss" and novedad):
            stats["sin_tendencia"] += 1
            continue
        sid = C.id_senal(it["url"])
        if sid in vistos:
            stats["repetidas"] += 1
            continue
        vistos.add(sid)
        nuevos_hoy.append(sid)
        stats["nuevas"] += 1
        tipo = C.tipo_de(tn, rn)
        s = {"id": sid, "t": it["titulo"], "u": it["url"], "f": it.get("fuente") or "", "d": fecha.astimezone(timezone.utc).isoformat(timespec="minutes"),
             "r": it.get("resumen", "")[:240], "i": it.get("imagen"), "tipo": tipo, "nov": novedad,
             "nivel": it.get("nivel", 3), "o": it["origen"], "tend": [tid for tid, _ in tend], "n": 1}
        if not s["i"]:
            s.pop("i")
        dia = fecha.astimezone(timezone.utc).date().isoformat()
        for tid, _ in tend:
            fila = conteos.setdefault(dia, {}).setdefault(tid, [0] * len(M.TIPOS_ORDEN))
            fila[M.TIPOS_ORDEN.index(tipo)] += 1
            agregar_agrupando(por_t.setdefault(tid, []), dict(s))
        if tend and (s["nivel"] <= 2 or tipo != "otro"):
            agregar_agrupando(ultimas, dict(s))
        if not tend and novedad:
            agregar_agrupando(fuera, dict(s))

    vistos_dict[hoy] = " ".join(nuevos_hoy)
    # podas
    corte_vistos = (ahora.date() - timedelta(days=RETENCION_VISTOS)).isoformat()
    for d in [d for d in vistos_dict if d < corte_vistos]:
        del vistos_dict[d]
    corte_conteos = (ahora.date() - timedelta(days=RETENCION_CONTEOS)).isoformat()
    for d in [d for d in conteos if d < corte_conteos]:
        del conteos[d]
    lim_iso = limite.isoformat(timespec="minutes")
    for tid in list(por_t):
        lst = [s for s in por_t[tid] if s["d"] >= lim_iso]
        lst.sort(key=lambda s: -puntaje(s, ahora))
        por_t[tid] = lst[:MAX_POR_TENDENCIA]
    senales["ultimas"] = sorted([s for s in ultimas if s["d"] >= lim_iso], key=lambda s: s["d"], reverse=True)[:MAX_ULTIMAS]
    lim_fuera = (ahora - timedelta(days=14)).isoformat(timespec="minutes")
    senales["fuera"] = sorted([s for s in fuera if s["d"] >= lim_fuera], key=lambda s: s["d"], reverse=True)[:MAX_FUERA]
    return stats


# ---------------------------------------------------------------- métricas diarias

def medir_wikipedia(cat: dict, diario: dict, ahora: datetime, estado_fuentes: dict) -> bool:
    """Vistas mensuales (24 meses completos) de los artículos de cada tendencia. True si salió bien."""
    hoy = ahora.date()
    tend = cat["tendencias"]
    fin_mes = hoy.replace(day=1) - timedelta(days=1)
    ini = (fin_mes.replace(day=1) - timedelta(days=700)).replace(day=1)
    wiki = diario.setdefault("wiki", {})
    ef = estado_fuentes.setdefault("Wikipedia (vistas)", {"tipo": "diario"})
    errores = len(tend)
    try:
        titulos = sorted({w for t in tend for w in t.get("wiki", [])})
        canon = F.resolver_titulos(titulos)
        faltan = [w for w, c in canon.items() if not c]
        if faltan:
            log(f"  aviso: artículos de Wikipedia inexistentes en el catálogo: {faltan}")
        es = resolver_es([c for c in canon.values() if c])
        errores = 0
        for t in tend:
            serie: dict[str, int] = {}
            usados = []
            ok = True
            for w in t.get("wiki", []):
                c = canon.get(w)
                if not c or c in usados:
                    continue
                try:
                    v = F.vistas_mensuales(c, ini.strftime("%Y%m%d"), fin_mes.strftime("%Y%m%d"))
                    for m, n in v.items():
                        serie[m] = serie.get(m, 0) + n
                    usados.append(c)
                except Exception as e:
                    ok = False
                    errores += 1
                    log(f"  ✗ Wikipedia «{c}»: {e}")
                time.sleep(1.1)
            if usados and ok:
                wiki[t["id"]] = {"serie": serie, "articulos": usados, "es": es.get(usados[0])}
        if errores:
            ef["error"] = f"{errores} artículos fallaron"
        else:
            ef.pop("error", None)
        ef["ok"] = F.ahora().isoformat(timespec="minutes")
    except Exception as e:
        ef["error"] = f"{type(e).__name__}: {str(e)[:120]}"
        log(f"  ✗ Wikipedia: {e}")
    return errores <= len(tend) // 10


def medir_papers(cat: dict, diario: dict, ahora: datetime, estado_fuentes: dict) -> bool:
    """Artículos científicos por año (OpenAlex), una consulta por tendencia. True si salió bien.

    El crecimiento compara el último año completo con el anterior: la indexación
    de lo reciente tarda meses y el año en curso siempre sale incompleto.
    """
    hoy = ahora.date()
    clave = os.environ.get("OPENALEX_API_KEY") or None
    papers = diario.setdefault("papers", {})
    ef = estado_fuentes.setdefault("OpenAlex (investigación)", {"tipo": "diario"})
    errores = 0
    for i, t in enumerate(cat["tendencias"]):
        try:
            anios = F.openalex_por_anio(t["oa"], hoy.year - 7, hoy.year, clave)
        except F.SinPresupuesto:
            ef["error"] = "sin presupuesto diario (falta clave OPENALEX_API_KEY); se reintenta más tarde"
            log(f"  ✗ OpenAlex: presupuesto diario agotado tras {i} consultas; se conservan los datos anteriores")
            return False
        except Exception as e:
            errores += 1
            log(f"  ✗ OpenAlex «{t['id']}»: {type(e).__name__}: {str(e)[:80]}")
            continue
        papers[t["id"]] = {"anios": anios, "reciente": anios.get(str(hoy.year - 1), 0), "previo": anios.get(str(hoy.year - 2), 0)}
        time.sleep(0.12)
    if errores:
        ef["error"] = f"{errores} consultas fallaron"
    else:
        ef.pop("error", None)
    ef["ok"] = F.ahora().isoformat(timespec="minutes")
    return errores <= len(cat["tendencias"]) // 10


def resolver_es(titulos: list[str]) -> dict[str, str]:
    """Título en es.wikipedia del mismo artículo (si existe)."""
    import urllib.parse
    out = {}
    for i in range(0, len(titulos), 40):
        lote = titulos[i:i + 40]
        q = urllib.parse.urlencode({"action": "query", "titles": "|".join(lote), "prop": "langlinks",
                                    "lllang": "es", "lllimit": "max", "format": "json"})
        try:
            d = F.http_json("https://en.wikipedia.org/w/api.php?" + q)
        except Exception:
            continue
        for p in d["query"]["pages"].values():
            ll = p.get("langlinks")
            if ll:
                out[p["title"]] = ll[0]["*"]
        time.sleep(0.5)
    return out


# ---------------------------------------------------------------- página

def datos_pagina(cat: dict, estado: dict, senales: dict, diario: dict, ahora: datetime, conf: dict | None = None) -> dict:
    # las reglas de calidad se vuelven a aplicar a lo guardado: una mejora de filtros limpia la página al instante
    excluidos = {m.lower() for m in (conf or {}).get("medios_excluidos", [])}
    vale = lambda s: C.motivo_exclusion(C.normalizar(s["t"]), s.get("f", ""), excluidos) is None
    hoy = ahora.date()
    tend = cat["tendencias"]
    conteos = estado.get("conteos", {})
    inicio = estado.get("inicio")
    imp = M.impulso(tend, diario.get("wiki", {}), diario.get("papers", {}), conteos, hoy, inicio)
    hz = M.horizontes(tend, conteos, hoy)
    historial = estado.setdefault("historial", {})
    historial[hoy.isoformat()] = {t["id"]: [imp[t["id"]]["impulso"], hz[t["id"]]["anios"]] for t in tend}
    corte = (hoy - timedelta(days=RETENCION_CONTEOS)).isoformat()
    for d in [d for d in historial if d < corte]:
        del historial[d]
    nombres = {t["id"]: t["nombre"] for t in tend}
    cambios = M.cambios(historial, hoy, nombres)

    fin_mes = hoy.replace(day=1) - timedelta(days=1)
    meses = []
    m = fin_mes.replace(day=1)
    for _ in range(24):
        meses.append(m.strftime("%Y-%m"))
        m = (m - timedelta(days=1)).replace(day=1)
    meses.reverse()

    salida = []
    for t in tend:
        tid = t["id"]
        w = diario.get("wiki", {}).get(tid)
        p = diario.get("papers", {}).get(tid)
        lst = sorted([s for s in senales.get("por_tendencia", {}).get(tid, []) if vale(s)], key=lambda s: -puntaje(s, ahora))[:14]
        lst.sort(key=lambda s: s["d"], reverse=True)
        art = (w or {}).get("articulos") or []
        salida.append({
            **{k: t[k] for k in ("id", "nombre", "corto", "en", "mitad", "familia", "focos", "sectores", "impacto", "que_es", "por_que")},
            "anios": hz[tid]["anios"], "anios_base": hz[tid]["base"], "ajuste": hz[tid]["ajuste"],
            "mercado": hz[tid]["mercado"], "esperado": hz[tid]["esperado"], "n_mezcla": hz[tid]["n"], "mezcla": hz[tid]["mezcla"],
            "impulso": imp[tid]["impulso"], "nivel": M.nivel_impulso(imp[tid]["impulso"]), "componentes": imp[tid]["componentes"],
            "n7": M.conteo_dias(conteos, tid, hoy, 7), "n30": M.conteo_dias(conteos, tid, hoy, 30),
            "semanas": M.serie_semanal(conteos, tid, hoy, 12),
            "wiki": None if not w else {
                "vistas": [w["serie"].get(mm) for mm in meses],
                "url": "https://en.wikipedia.org/wiki/" + art[0].replace(" ", "_") if art else None,
                "url_es": ("https://es.wikipedia.org/wiki/" + w["es"].replace(" ", "_")) if w.get("es") else None,
            },
            "papers": None if not p else {"anios": p.get("anios", {}), "reciente": p.get("reciente"), "previo": p.get("previo")},
            "senales": [limpiar_para_pagina(s) for s in lst],
        })

    ultimas = [limpiar_para_pagina(s, con_tend=True) for s in senales.get("ultimas", []) if vale(s)][:80]
    fuera = sorted([s for s in senales.get("fuera", []) if vale(s) and C.es_novedad(C.normalizar(s["t"]), C.normalizar(s.get("r", "")))],
                   key=lambda s: -puntaje(s, ahora))
    por_fuente, fuera_sel = {}, []
    for s in fuera:
        if por_fuente.get(s["f"], 0) >= 2:
            continue
        por_fuente[s["f"]] = por_fuente.get(s["f"], 0) + 1
        fuera_sel.append(limpiar_para_pagina(s, con_resumen=True))
        if len(fuera_sel) >= 12:
            break

    ef = estado.get("fuentes", {})
    rss = {k: v for k, v in ef.items() if v.get("tipo") == "rss"}
    corte7 = (ahora - timedelta(days=7)).isoformat(timespec="minutes")
    medios7 = {s["f"] for lst in senales.get("por_tendencia", {}).values() for s in lst if s["d"] >= corte7}
    total7 = sum(sum(sum(f) for f in conteos.get((hoy - timedelta(days=i)).isoformat(), {}).values()) for i in range(7))
    return {
        "generado": ahora.isoformat(timespec="minutes"),
        "catalogo": {k: cat[k] for k in ("mitades", "familias", "focos", "sectores")},
        "tendencias": salida,
        "ultimas": ultimas,
        "fuera": fuera_sel,
        "cambios": cambios,
        "meses": meses,
        "estado": {
            "fuentes_total": len(rss), "fuentes_ok": sum(1 for v in rss.values() if not v.get("error")),
            "caidas": sorted(k for k, v in ef.items() if v.get("error")),
            "senales_7d": total7, "medios_7d": len(medios7),
            "diario": diario.get("fecha_wiki"), "papers": diario.get("fecha_papers"), "historia_dias": M.dias_de_historia(inicio, hoy), "inicio": inicio,
            "revisado": cat.get("revisado"),
        },
    }


def limpiar_para_pagina(s: dict, con_tend: bool = False, con_resumen: bool = False) -> dict:
    o = {"t": s["t"], "u": s["u"], "f": s["f"], "d": s["d"], "tipo": s.get("tipo", "otro")}
    if s.get("i"):
        o["i"] = s["i"]
    if s.get("n", 1) > 1:
        o["n"] = s["n"]
        if s.get("otras"):
            o["otras"] = s["otras"][:4]
    if con_tend:
        o["tend"] = s.get("tend", [])[:3]
    if con_resumen and s.get("r"):
        o["r"] = s["r"]
    return o


def construir_pagina(datos: dict) -> Path:
    plantilla = (RAIZ / "plantilla.html").read_text(encoding="utf-8")
    js = json.dumps(datos, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    html = plantilla.replace("/*__DATOS__*/null", js)
    SITE.mkdir(exist_ok=True)
    (SITE / "index.html").write_text(html, encoding="utf-8")
    (SITE / "datos.json").write_text(json.dumps(datos, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    marca = RAIZ / "marca"
    if marca.exists():
        for f in marca.iterdir():
            if f.suffix.lower() in (".svg", ".png", ".ico", ".webmanifest"):
                shutil.copy2(f, SITE / f.name)
    (SITE / ".nojekyll").write_text("", encoding="utf-8")
    return SITE / "index.html"


# ---------------------------------------------------------------- main

def main(argv=None):
    ap = argparse.ArgumentParser(description="Radar de Innovación")
    ap.add_argument("--sin-red", action="store_true")
    ap.add_argument("--sin-bing", action="store_true")
    ap.add_argument("--forzar-diario", action="store_true")
    ap.add_argument("--abrir", action="store_true")
    a = ap.parse_args(argv)

    t0 = time.time()
    cat = json.loads((RAIZ / "tendencias.json").read_text(encoding="utf-8"))
    conf = json.loads((RAIZ / "fuentes.json").read_text(encoding="utf-8"))
    estado = cargar("estado.json", {})
    senales = cargar("senales.json", {})
    diario = cargar("diario.json", {})
    ahora = F.ahora()

    if not a.sin_red:
        estado.setdefault("inicio", ahora.date().isoformat())
        ef = estado.setdefault("fuentes", {})
        log(f"leyendo {len(conf['feeds'])} feeds…")
        items = recolectar_rss(conf["feeds"], ef)
        if not a.sin_bing:
            log(f"buscando {len(cat['tendencias'])} tendencias en Bing News…")
            items += recolectar_bing(cat["tendencias"], ef, conf.get("medios_nivel1", []))
        stats = procesar(items, cat, conf, estado, senales, ahora)
        log(f"señales: {stats['leidas']} leídas · {stats['nuevas']} nuevas · {stats['repetidas']} ya vistas · "
            f"{stats['sin_tendencia']} sin tendencia · {stats['viejas']} viejas · excluidas {sum(stats['excluidas'].values())} {stats['excluidas']}")
        hoy = ahora.date().isoformat()
        if a.forzar_diario or diario.get("fecha_wiki") != hoy:
            log("medición diaria: Wikipedia…")
            if medir_wikipedia(cat, diario, ahora, ef):
                diario["fecha_wiki"] = hoy
            guardar("diario.json", diario, compacto=True)
        # sin clave, OpenAlex puede negar el servicio: se reintenta como máximo cada 6 h
        intento = diario.get("intento_papers", "")
        if a.forzar_diario or (diario.get("fecha_papers") != hoy and intento < (ahora - timedelta(hours=6)).isoformat()):
            log("medición diaria: OpenAlex…")
            diario["intento_papers"] = ahora.isoformat(timespec="minutes")
            if medir_papers(cat, diario, ahora, ef):
                diario["fecha_papers"] = hoy
            guardar("diario.json", diario, compacto=True)
        estado["ultima_corrida"] = ahora.isoformat(timespec="minutes")
        estado["ultimas_stats"] = stats

    datos = datos_pagina(cat, estado, senales, diario, ahora, conf)
    guardar("estado.json", estado, compacto=True)
    guardar("senales.json", senales, compacto=True)
    pagina = construir_pagina(datos)
    e = datos["estado"]
    log(f"página: {pagina} · {e['senales_7d']} señales en 7 días · {e['fuentes_ok']}/{e['fuentes_total']} feeds ok · {time.time() - t0:.0f} s")
    if a.abrir:
        webbrowser.open(pagina.as_uri())
    return 0


if __name__ == "__main__":
    sys.exit(main())
