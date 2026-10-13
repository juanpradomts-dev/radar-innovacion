"""Lectura de fuentes públicas: feeds RSS/Atom, Bing News RSS, Wikipedia (vistas) y OpenAlex.

Solo biblioteca estándar. Cada función devuelve datos o lanza excepción; quien
llama decide qué hacer si una fuente cae (el radar conserva lo anterior).
"""
from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime

from clasificar import limpiar_html

UA = "RadarInnovacion/1.0 (+https://github.com/juanpradomts-dev/radar-innovacion; proyecto estudiantil)"
UA_NAVEGADOR = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0 Safari/537.36"


def http_get(url: str, ua: str = UA, timeout: int = 25, intentos: int = 3, aceptar: str = "*/*") -> bytes:
    """GET con reintentos. Respeta Retry-After en 429/503 (tope 30 s)."""
    ultimo = None
    for i in range(intentos):
        req = urllib.request.Request(url, headers={"User-Agent": ua, "Accept": aceptar,
                                                   "Accept-Language": "en-US,en;q=0.8,es;q=0.6"})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            ultimo = e
            if e.code in (429, 503) and i < intentos - 1:
                espera = e.headers.get("Retry-After")
                try:
                    espera = min(30.0, float(espera))
                except (TypeError, ValueError):
                    espera = 4.0 * (i + 1)
                time.sleep(espera)
                continue
            if e.code in (500, 502, 504) and i < intentos - 1:
                time.sleep(2.0 * (i + 1))
                continue
            raise
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            ultimo = e
            if i < intentos - 1:
                time.sleep(2.0 * (i + 1))
                continue
            raise
    raise ultimo  # pragma: no cover


def http_json(url: str, **kw):
    return json.loads(http_get(url, aceptar="application/json", **kw))


# ---------------------------------------------------------------- robots.txt

_ROBOTS: dict[str, urllib.robotparser.RobotFileParser | None] = {}


def permitido(url: str, ua: str = UA) -> bool:
    """True si robots.txt del dominio permite leer la URL (si robots no responde, se asume permitido)."""
    p = urllib.parse.urlsplit(url)
    base = f"{p.scheme}://{p.netloc}"
    if base not in _ROBOTS:
        rp = urllib.robotparser.RobotFileParser()
        try:
            rp.parse(http_get(base + "/robots.txt", timeout=12, intentos=1).decode("utf-8", "replace").splitlines())
            _ROBOTS[base] = rp
        except urllib.error.HTTPError as e:
            # 4xx = no hay robots.txt → todo permitido; 5xx = no se sabe → permitido
            _ROBOTS[base] = None
        except Exception:
            _ROBOTS[base] = None
    rp = _ROBOTS[base]
    return True if rp is None else rp.can_fetch(ua.split("/")[0], url)


# ---------------------------------------------------------------- fechas

def parse_fecha(txt: str | None) -> datetime | None:
    if not txt:
        return None
    txt = txt.strip()
    try:
        d = parsedate_to_datetime(txt)
        if d is not None:
            return d if d.tzinfo else d.replace(tzinfo=timezone.utc)
    except (TypeError, ValueError, IndexError):
        pass
    t = txt.replace("Z", "+00:00")
    for f in (None, "%a, %d %b %Y", "%d %b %Y", "%Y-%m-%d"):
        try:
            d = datetime.fromisoformat(t) if f is None else datetime.strptime(txt, f)
            return d if d.tzinfo else d.replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


# ---------------------------------------------------------------- RSS / Atom

_NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "dc": "http://purl.org/dc/elements/1.1/",
    "content": "http://purl.org/rss/1.0/modules/content/",
    "media": "http://search.yahoo.com/mrss/",
    "rss1": "http://purl.org/rss/1.0/",
    "prism": "http://prismstandard.org/namespaces/basic/2.0/",
}


def _texto(el, *rutas):
    for r in rutas:
        x = el.find(r, _NS)
        if x is not None:
            if x.text and x.text.strip():
                return x.text.strip()
            if x.get("href"):
                return x.get("href").strip()
    return None


def _imagen(el) -> str | None:
    for r in ("media:content", "media:thumbnail", "media:group/media:content", "enclosure"):
        for x in el.findall(r, _NS):
            u = x.get("url")
            tipo = (x.get("type") or x.get("medium") or "image").lower()
            if u and ("image" in tipo or u.lower().split("?")[0].endswith((".jpg", ".jpeg", ".png", ".webp"))):
                return u
    html = _texto(el, "content:encoded", "description", "atom:content", "atom:summary") or ""
    i = html.find("<img")
    if i >= 0:
        j = html.find("src=", i)
        if j > 0:
            q = html[j + 4]
            if q in "\"'":
                fin = html.find(q, j + 5)
                if fin > 0:
                    return html[j + 5:fin]
    return None


def parse_feed(datos: bytes, fuente: str) -> list[dict]:
    """Lee RSS 2.0, RSS 1.0 (RDF) o Atom. Devuelve [{titulo, url, fecha, resumen, imagen, fuente}]."""
    raiz = ET.fromstring(datos)
    items = raiz.findall(".//item") or raiz.findall(".//rss1:item", _NS) or raiz.findall(".//atom:entry", _NS)
    out = []
    for it in items:
        titulo = _texto(it, "title", "rss1:title", "atom:title")
        url = _texto(it, "link", "rss1:link") or None
        if not url:
            for l in it.findall("atom:link", _NS):
                if l.get("rel", "alternate") == "alternate" and l.get("href"):
                    url = l.get("href")
                    break
        if not titulo or not url:
            continue
        fecha = parse_fecha(_texto(it, "pubDate", "dc:date", "prism:publicationDate", "atom:published", "atom:updated"))
        resumen = limpiar_html(_texto(it, "description", "rss1:description", "atom:summary", "content:encoded", "atom:content") or "")
        out.append({"titulo": limpiar_html(titulo, 300), "url": url.strip(), "fecha": fecha, "resumen": resumen,
                     "imagen": _imagen(it), "fuente": fuente})
    return out


def leer_feed(feed: dict) -> list[dict]:
    datos = http_get(feed["url"], ua=UA_NAVEGADOR if feed.get("navegador") else UA, intentos=2)
    return parse_feed(datos, feed["nombre"])


# ---------------------------------------------------------------- Bing News RSS

BING = "https://www.bing.com/news/search?format=rss&count=50&setlang=en-us&q="


def _url_real(link: str) -> str:
    """Bing envuelve los enlaces en apiclick.aspx?...&url=<destino>."""
    try:
        q = dict(urllib.parse.parse_qsl(urllib.parse.urlsplit(link).query))
        if q.get("url", "").startswith("http"):
            return q["url"]
    except ValueError:
        pass
    return link


def bing_news(consulta: str) -> list[dict]:
    datos = http_get(BING + urllib.parse.quote_plus(consulta), ua=UA_NAVEGADOR, intentos=2)
    raiz = ET.fromstring(datos)
    out = []
    for it in raiz.findall(".//item"):
        titulo = (it.findtext("title") or "").strip()
        link = (it.findtext("link") or "").strip()
        if not titulo or not link:
            continue
        fuente = None
        imagen = None
        for hijo in it:
            etiqueta = hijo.tag.split("}")[-1].lower()
            if etiqueta == "source" and hijo.text:
                fuente = hijo.text.strip()
            elif etiqueta == "image" and hijo.text:
                imagen = hijo.text.strip()
        out.append({"titulo": limpiar_html(titulo, 300), "url": _url_real(link),
                     "fecha": parse_fecha(it.findtext("pubDate")),
                     "resumen": limpiar_html(it.findtext("description") or ""),
                     "imagen": imagen, "fuente": fuente or urllib.parse.urlsplit(_url_real(link)).netloc.removeprefix("www.")})
    return out


# ---------------------------------------------------------------- Wikipedia

def resolver_titulos(titulos: list[str]) -> dict[str, str | None]:
    """Título pedido → título canónico en en.wikipedia (siguiendo redirecciones). None si no existe."""
    res: dict[str, str | None] = {}
    for i in range(0, len(titulos), 40):
        lote = titulos[i:i + 40]
        q = urllib.parse.urlencode({"action": "query", "titles": "|".join(lote), "redirects": 1, "format": "json"})
        d = http_json("https://en.wikipedia.org/w/api.php?" + q)
        norm = {n["from"]: n["to"] for n in d["query"].get("normalized", [])}
        red = {r["from"]: r["to"] for r in d["query"].get("redirects", [])}
        existe = {p["title"]: "missing" not in p for p in d["query"]["pages"].values()}
        for t in lote:
            c = norm.get(t, t)
            c = red.get(c, c)
            res[t] = c if existe.get(c) else None
        time.sleep(0.5)
    return res


def vistas_mensuales(titulo: str, desde: str, hasta: str) -> dict[str, int]:
    """{'2026-09': vistas} de usuarios humanos, todas las plataformas."""
    art = urllib.parse.quote(titulo.replace(" ", "_"), safe="")
    url = (f"https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/user/"
           f"{art}/monthly/{desde}/{hasta}")
    d = http_json(url, intentos=4)
    return {x["timestamp"][:4] + "-" + x["timestamp"][4:6]: int(x["views"]) for x in d.get("items", [])}


# ---------------------------------------------------------------- OpenAlex

class SinPresupuesto(Exception):
    """OpenAlex agotó el presupuesto diario (sin clave se comparte por IP)."""


def openalex_por_anio(consulta: str, desde_anio: int, hasta_anio: int, clave: str | None = None) -> dict[str, int]:
    """Artículos por año de publicación cuyo título o resumen coincide con la consulta.

    Sin clave, OpenAlex da un presupuesto diario pequeño compartido por IP; con una
    clave gratuita (variable OPENALEX_API_KEY) el presupuesto es propio.
    """
    filtro = f"title_and_abstract.search:{consulta},publication_year:{desde_anio}-{hasta_anio}"
    url = "https://api.openalex.org/works?group_by=publication_year&filter=" + urllib.parse.quote(filtro, safe=":,-")
    if clave:
        url += "&api_key=" + urllib.parse.quote(clave)
    try:
        d = json.loads(http_get(url, aceptar="application/json", intentos=1))
    except urllib.error.HTTPError as e:
        if e.code == 429:
            raise SinPresupuesto(e.headers.get("Retry-After", "")) from None
        raise
    return {str(g["key"]): int(g["count"]) for g in d.get("group_by", [])}


def ahora() -> datetime:
    return datetime.now(timezone.utc)


def hace(dias: float) -> datetime:
    return ahora() - timedelta(days=dias)
