"""Clasificación local de señales (sin IA, sin red): calidad, tendencia, tipo y duplicados.

Todo trabaja sobre texto normalizado: minúsculas y sin tildes. Las claves de
tendencias.json se escriben así.
"""
from __future__ import annotations

import hashlib
import re
import unicodedata
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

# ---------------------------------------------------------------- normalización

def normalizar(texto: str) -> str:
    """Minúsculas, sin tildes, comillas y guiones tipográficos unificados."""
    if not texto:
        return ""
    t = unicodedata.normalize("NFKD", texto)
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = (t.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
           .replace("–", "-").replace("—", "-").replace(" ", " "))
    return re.sub(r"\s+", " ", t).strip().lower()


_TAG = re.compile(r"<[^>]+>")
_TAG_BLOQUE = re.compile(r"</?(p|br|div|li|ul|ol|h[1-6]|tr|td|th|table|figure|figcaption|blockquote|section|article|img)\b[^>]*>", re.I)
_ENT = {"&amp;": "&", "&lt;": "<", "&gt;": ">", "&quot;": '"', "&#39;": "'", "&apos;": "'", "&nbsp;": " ",
        "&#8217;": "'", "&#8216;": "'", "&#8220;": '"', "&#8221;": '"', "&#8211;": "-", "&#8212;": "-",
        "&hellip;": "...", "&#8230;": "..."}


def limpiar_html(texto: str, maximo: int = 320) -> str:
    """Quita etiquetas y entidades comunes; recorta en frontera de palabra."""
    if not texto:
        return ""
    t = _TAG_BLOQUE.sub(" ", texto)
    t = _TAG.sub("", t)
    for k, v in _ENT.items():
        t = t.replace(k, v)
    t = re.sub(r"&#(\d+);", lambda m: chr(int(m.group(1))) if int(m.group(1)) < 0x110000 else " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    # cola típica de WordPress: "The post X appeared first on Y."
    t = re.sub(r"\s*(The post .{0,200} appeared first on .{0,80}\.?|La entrada .{0,200} se public[oó] primero en .{0,80}\.?)$", "", t)
    if len(t) > maximo:
        t = t[:maximo].rsplit(" ", 1)[0].rstrip(",.;:") + "…"
    return t


# ---------------------------------------------------------------- URL e identidad

_PARAMS_BASURA = re.compile(r"^(utm_|fbclid|gclid|mc_|ref$|ref_src|cmpid|ocid|taid|rss|source$|guccounter)", re.I)


def url_canonica(url: str) -> str:
    try:
        p = urlsplit(url.strip())
    except ValueError:
        return url.strip()
    q = [(k, v) for k, v in parse_qsl(p.query, keep_blank_values=False) if not _PARAMS_BASURA.match(k)]
    host = p.netloc.lower().removeprefix("www.")
    ruta = p.path.rstrip("/") or "/"
    return urlunsplit(("https", host, ruta, urlencode(q), ""))


def id_senal(url: str) -> str:
    return hashlib.sha1(url_canonica(url).encode("utf-8")).hexdigest()[:12]


# ---------------------------------------------------------------- calidad

_RUIDO_TITULO = [
    (re.compile(r"\bmarket (size|share|report|forecast|research|analysis|outlook|growth|trends?)\b|\bcagr\b|\bby 20[3-4]\d\b|\bkey players\b|\bindustry analysis\b"), "informe de mercado (spam)"),
    (re.compile(r"\bstocks? (to buy|price|rall\w+|soar\w*|jump\w*|fall\w*|plung\w+|surg\w+|slid\w+|tumbl\w+|down|up)\b|\bshares (rise|rose|fall|fell|jump\w*|soar\w*|plung\w+|drop\w*|surg\w+|tumbl\w+|slid\w+|gain\w*|climb\w*)\b|\bprice target\b|\b(buy|sell|hold) rating\b|\bdividends?\b|\betfs?\b|\b(nasdaq|nyse):|\bearnings (call|report|beat|miss)\b|\bq[1-4] (results|earnings)\b|\bto buy (now|today|right now)\b|\bundervalued\b|\bacciones de\b"), "bolsa y finanzas personales"),
    (re.compile(r"\b(best|top) .{0,40}deals?\b|\d+% off\b|\bdiscount code\b|\bcoupons?\b|\bprime (big )?deal days\b|\bblack friday\b|\bcyber monday\b|\bon sale\b|\bofertas?\b|\bdescuentos?\b|\bchollos?\b|\bremat(a|an|ando)\b|\brebaj\w+|\bprecio (minimo|historico|de locura)\b|\bliquidacion\b|\bcyber (days|wow)\b|\bpor menos de (s/|\$|us\$)? ?\d|\bunder \$\d"), "ofertas"),
    (re.compile(r"\bviral\b|\bhoroscope\b|\bwatch:|\bvideo:|\bphotos:|\bquiz\b|\bpodcast\b|\bnewsletter\b|\bweek in review\b|\bthis week in\b|\bdaily brief\b|\bpodcast:|\blive updates?\b|\bunboxing\b"), "entretenimiento o boletín"),
    (re.compile(r"\b(review|reseña|analisis):|\bhands[- ]on\b|\bhow to\b|\bcomo (elegir|configurar|activar)\b"), "reseña de producto o tutorial"),
    (re.compile(r"^the download:|^the batch:|^this week|\bweekly (roundup|recap)\b|\bmorning brief\b|^survey (sunday|says)\b|\bin brief:"), "entretenimiento o boletín"),
    (re.compile(r"\bwhat'?s the difference\b|^what (is|are) \b|^what happens (to|when|if)\b|\bexplained:|\beverything you need to know\b|\bbeginner'?s guide\b|\bhere'?s what (you|to)\b|\bwhat (patients|you) need to know\b|^que es\b"), "explicativo o guía básica"),
    (re.compile(r"\b(names?|named|appoints?|appointed|taps|tapped|hires?|hired) [^.]{0,40}\bas (new )?(ceo|cfo|cto|coo|chief|president|chair\w*)\b|\bsteps down\b|\bnuevo (ceo|gerente|director)\b"), "nombramiento"),
]


def motivo_exclusion(titulo_norm: str, fuente: str, excluidos: set[str]) -> str | None:
    """None si la señal pasa; si no, el motivo en español."""
    if not titulo_norm or len(titulo_norm) < 18:
        return "título vacío o muy corto"
    if fuente and fuente.strip().lower() in excluidos:
        return "medio de bolsa o notas de prensa pagadas"
    for patron, motivo in _RUIDO_TITULO:
        if patron.search(titulo_norm):
            return motivo
    return None


# ---------------------------------------------------------------- tendencias

_BORDE_I = r"(?<![a-z0-9])"
_BORDE_D = r"(?![a-z0-9])"


def compilar_tendencias(tendencias: list[dict]) -> list[dict]:
    """Devuelve una lista paralela con los patrones compilados de cada tendencia."""
    out = []
    for t in tendencias:
        claves = [re.compile(_BORDE_I + "(?:" + c + ")" + _BORDE_D) for c in t.get("claves", [])]
        excluir = [re.compile(_BORDE_I + "(?:" + c + ")" + _BORDE_D) for c in t.get("excluir", [])]
        out.append({"id": t["id"], "claves": claves, "excluir": excluir})
    return out


def _aciertos(patrones, texto: str) -> set[int]:
    return {i for i, p in enumerate(patrones) if p.search(texto)}


def tendencias_de(titulo_norm: str, resumen_norm: str, compiladas: list[dict], consulta_de: str | None = None) -> list[tuple[str, float]]:
    """Tendencias a las que pertenece una señal, con su puntaje (mayor primero).

    Regla: basta una clave en el título; en el resumen hacen falta dos claves
    distintas, salvo que la señal venga de la búsqueda de esa misma tendencia.
    """
    res = []
    texto = titulo_norm + " \n " + resumen_norm
    for c in compiladas:
        en_titulo = _aciertos(c["claves"], titulo_norm)
        en_resumen = _aciertos(c["claves"], resumen_norm) - en_titulo
        propia = consulta_de == c["id"]
        if not (en_titulo or len(en_resumen) >= 2 or (propia and en_resumen)):
            continue
        if any(p.search(texto) for p in c["excluir"]):
            continue
        res.append((c["id"], 2.0 * len(en_titulo) + len(en_resumen) + (0.5 if propia else 0.0)))
    res.sort(key=lambda x: -x[1])
    return res


# ---------------------------------------------------------------- tipo de señal

TIPOS = {
    "inversion": "Inversión",
    "regulacion": "Regulación",
    "investigacion": "Investigación",
    "lanzamiento": "Lanzamiento",
    "otro": "Noticia",
}

_PATRON_TIPO = [
    ("inversion", re.compile(r"\brais(e|es|ed|ing)\b(?=[^.;:]{0,50}(\$|€|£|usd|us\$|million|billion|millones|funding|round|seed|series))|\b(funding|financing round|series [a-e]|seed round|invest(s|ed|ing|ments?)?|investors?|acquir(e|es|ed|ing)|acquisition|merger|ipo|valuation|unicorn|venture capital|levanta|ronda|financiacion|financiamiento|inversion(es)?|invierte|invertira|adquiere|adquisicion|compra de)\b|\$\d+(\.\d+)? ?(m|bn?|million|billion)\b|\d+ (millones|mil millones) de (dolares|euros)")),
    ("regulacion", re.compile(r"\b(regulat\w+|laws?|legislat\w+|bills?|(?<!-)bans?|banned|rules?|polic(y|ies)|government|ministry|senate|congress|parliament|european commission|white house|executive order|mandates?|approv\w+|fda|epa|lawsuits?|sues|sued|court|antitrust|tariffs?|regulacion|regula|ley(es)?|gobierno|ministerio|congreso|normas?|prohib\w+|aprueba\w*|aranceles?)\b")),
    ("investigacion", re.compile(r"\b(researchers?|scientists?|study|studies|universit(y|ies)|paper|journal|lab|laboratory|prototypes?|experiment\w*|discover\w*|breakthrough|physicists?|engineers (have )?(developed|created|built|designed)|investigador\w*|cientific\w+|estudio|universidad\w*|laboratorio|prototipo|descubr\w+|hallazgo)\b")),
    ("lanzamiento", re.compile(r"\b(launch\w*|unveil\w*|introduc\w+|announc\w+|rolls? out|rolled out|rollout|deploy\w*|debut\w*|releas\w+|available|ships|begins|starts|opens|pilot\w*|partner\w*|contracts?|orders|commerciali[sz]\w+|lanza\w*|presenta\w*|anuncia\w*|desplieg\w+|estrena\w*|alianza|disponible|inaugura\w*|llega\w*)\b")),
]


def tipo_de(titulo_norm: str, resumen_norm: str) -> str:
    """Tipo de señal. Gana el verbo que aparece primero en el título ("X raises $5M to launch Y" = inversión);
    si el título no dice nada, se mira el resumen."""
    for texto in (titulo_norm, resumen_norm):
        mejor = None
        for orden, (tipo, patron) in enumerate(_PATRON_TIPO):
            m = patron.search(texto)
            if m and (mejor is None or (m.start(), orden) < mejor[:2]):
                mejor = (m.start(), orden, tipo)
        if mejor:
            return mejor[2]
    return "otro"


MERCADO = {"lanzamiento", "inversion"}

# ---------------------------------------------------------------- novedad (fuera del radar)

_MARCAS_NOVEDAD = re.compile(
    r"\b(world'?s first|first[- ]ever|first of its kind|breakthrough|new (type|kind|way|material|method|technique|device|system|class|approach)|"
    r"record[- ](breaking|setting)|sets? (a )?record|novel|pioneering (technique|method|technology|device)|invents?|invented|develop(s|ed)? (a|an|the) new|"
    r"primer\w* (del|en el) mundo|innovador\w*|revolucionari\w+|nuevo (tipo|material|metodo|sistema)|inventa\w*|logra)\b")


_NO_INNOVACION = re.compile(
    r"\b(astronom\w+|galax(y|ies)|black holes?|exoplanets?|brown dwarfs?|supernova\w*|nebula\w*|dinosaurs?|fossils?|ancient|archaeolog\w+|"
    r"prehistoric|species|evolution(ary)?|neanderthal\w*|mummy|comet|asteroid belt|light[- ]years?|ceo|elections?|horoscope)\b")
_INVESTIGA = re.compile(r"\b(researchers?|scientists?|engineers?|investigador\w*|cientific\w+)\b")


def es_novedad(titulo_norm: str, resumen_norm: str) -> bool:
    """Novedad tecnológica: marca de novedad en el título, o titular de investigación con marca en el resumen.
    Se excluye la ciencia básica que no es innovación (astronomía, paleontología, etc.)."""
    if _NO_INNOVACION.search(titulo_norm):
        return False
    if _MARCAS_NOVEDAD.search(titulo_norm):
        return True
    return bool(_INVESTIGA.search(titulo_norm) and _MARCAS_NOVEDAD.search(resumen_norm[:240]))


# ---------------------------------------------------------------- duplicados

_VACIAS = set("""a an the of to in on for and or with from by at as is are was were be its it this that new how why what
says said will can could may into over after about up out more than not no your you our their his her they we
el la los las de del y o en con por para un una unos unas que se su sus es al lo como mas""".split())


def huella(titulo_norm: str) -> frozenset:
    palabras = re.findall(r"[a-z0-9]+", titulo_norm)
    return frozenset(w for w in palabras if w not in _VACIAS and len(w) > 2)


def parecidos(a: frozenset, b: frozenset, umbral: float = 0.6) -> bool:
    if not a or not b:
        return False
    inter = len(a & b)
    if inter < 3:
        return False
    if inter / len(a | b) >= umbral:
        return True
    # titulares de la misma historia con distinta longitud ("X raises $7.6M" / "X closes oversubscribed $7.6M round")
    return inter >= 5 and inter / min(len(a), len(b)) >= 0.6


# ---------------------------------------------------------------- cercanía (Perú → Latinoamérica → mundo)

REGIONES = {"pe": "Perú", "la": "Latinoamérica", "mu": "Mundo"}

_PERU = re.compile(
    r"\b(peru|peruan[oa]s?|lima|limen[oa]s?|callao|arequipa|cusco|cuzco|trujillo|piura|chiclayo|iquitos|huancayo|tacna|puno|"
    r"cajamarca|ayacucho|ancash|ucayali|loreto|madre de dios|moquegua|chancay|indecopi|sunat|minem|osinergmin|osiptel|"
    r"concytec|proinversion|mincetur|minam|senamhi|bcrp|mef peru|mtc peru|pucp|unmsm|san marcos|utec|ulima|yape|plin|"
    r"interbank|bcp|credicorp|alicorp|backus|petroperu|southern peru|antamina|las bambas|quellaveco|cerro verde|"
    r"soles|s/ ?\d[\d.,]*|uit|afp|onp|essalud|minsa|midagri|mvcs|ceplan|pcm|reniec|sunafil|sedapal|pronabec|minedu|mtpe|digesa|sernanp|"
    r"ositran|sunass|ingemmet|inacal|cofide|mypes?|nino costero|congreso de la republica|gobierno peruano|ejecutivo peruano)\b")
_LATAM = re.compile(
    r"\b(latinoamerica\w*|latam|america latina|latin america\w*|sudamerica\w*|south america\w*|centroamerica\w*|"
    r"mexic\w+|colombi\w+|chile\w*|argentin\w+|brasil\w*|brazil\w*|ecuador\w*|bolivi\w+|uruguay\w*|paraguay\w*|venezol\w+|venezuela|"
    r"costa rica|panama|guatemal\w+|hondur\w+|el salvador|nicaragu\w+|dominican\w*|puerto rico|cuba\w*|"
    r"bogota|santiago de chile|buenos aires|sao paulo|ciudad de mexico|monterrey|medellin|quito|la paz|montevideo|"
    r"mercado ?libre|nubank|rappi)\b")
_MUNDO = re.compile(
    r"\b(estados unidos|eeuu|ee\. ?uu\.?|united states|u\.s\.|usa|washington|silicon valley|california|nueva york|new york|texas|"
    r"china|chin[oa]s?|chinese|beijing|pekin|shanghai|shenzhen|europa|europe\w*|union europea|uk|reino unido|britain|british|londres|london|"
    r"alemania|german\w*|francia|france|french|espana|spain|italia|italy|japon|japan\w*|corea|korea\w*|india|indian|taiwan\w*|"
    r"rusia|russia\w*|ucrania|ukrain\w*|israel\w*|canada|canadian|australia\w*|singapur|singapore|emiratos|uae|dubai|arabia saudita|saudi|"
    r"openai|anthropic|google|alphabet|meta|facebook|apple|microsoft|amazon|nvidia|tesla|spacex|samsung|huawei|alibaba|tencent|byd|tsmc|"
    r"intel|ibm|oracle|xai|deepseek|figure ai|waymo)\b")


def region_de(titulo_norm: str, resumen_norm: str, region_fuente: str | None = None, local_por_defecto: bool = False) -> str:
    """'pe', 'la' o 'mu'. Manda lo que dice la nota; la fuente solo decide cuando la nota no nombra ningún lugar.

    - Nombra a Perú (o una ciudad, entidad o empresa peruana) → 'pe'.
    - Si no, nombra un país o ciudad de Latinoamérica → 'la'.
    - Si no nombra lugares ni empresas globales y viene de un medio de nicho local (minería, pymes,
      sostenibilidad en Perú) → la región de la fuente. La prensa general no cuenta: también publica
      noticias globales sin nombrar el país.
    - En cualquier otro caso → 'mu'.
    """
    texto = titulo_norm + " " + resumen_norm[:400]
    if _PERU.search(texto):
        return "pe"
    if _LATAM.search(texto):
        return "la"
    if local_por_defecto and region_fuente in ("pe", "la") and not _MUNDO.search(texto):
        return region_fuente
    return "mu"
