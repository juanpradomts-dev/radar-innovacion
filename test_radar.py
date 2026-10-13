"""Pruebas del Radar de Innovación (sin red). Corren en GitHub Actions antes de publicar.

    python -m unittest -v test_radar
"""
import json
import math
import re
import shutil
import subprocess
import tempfile
import unittest
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import clasificar as C
import fuentes as F
import metricas as M
import radar

RAIZ = Path(__file__).resolve().parent
CAT = json.loads((RAIZ / "tendencias.json").read_text(encoding="utf-8"))
CONF = json.loads((RAIZ / "fuentes.json").read_text(encoding="utf-8"))
COMP = C.compilar_tendencias(CAT["tendencias"])


def tend(titulo, resumen="", consulta=None):
    return [t for t, _ in C.tendencias_de(C.normalizar(titulo), C.normalizar(resumen), COMP, consulta)]


class Catalogo(unittest.TestCase):
    def test_ids_unicos_y_campos(self):
        ids = [t["id"] for t in CAT["tendencias"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertGreaterEqual(len(ids), 40)
        for t in CAT["tendencias"]:
            for campo in ("nombre", "corto", "en", "mitad", "familia", "impacto", "anios", "focos", "sectores",
                          "que_es", "por_que", "claves", "bing", "wiki", "oa"):
                self.assertIn(campo, t, f"{t['id']} sin {campo}")
            self.assertIn(t["mitad"], CAT["mitades"])
            self.assertEqual(CAT["familias"][t["familia"]]["mitad"], t["mitad"], t["id"])
            self.assertTrue(1 <= t["impacto"] <= 10)
            self.assertTrue(0.5 <= t["anios"] <= 12)
            self.assertTrue(set(t["focos"]) <= set(CAT["focos"]), t["id"])
            self.assertTrue(set(t["sectores"]) <= set(CAT["sectores"]), t["id"])
            self.assertTrue(t["focos"] and t["sectores"])

    def test_etiqueta_corta_cabe_en_el_radar(self):
        for t in CAT["tendencias"]:
            lineas = t["corto"].split("\n")
            self.assertLessEqual(len(lineas), 2, t["id"])
            for l in lineas:
                self.assertLessEqual(len(l), 22, f"{t['id']}: «{l}»")

    def test_consultas_bing_sin_or(self):
        # Bing News RSS devuelve 0 resultados con OR
        for t in CAT["tendencias"]:
            self.assertIsInstance(t["bing"], list)
            self.assertTrue(1 <= len(t["bing"]) <= 2, t["id"])
            for q in t["bing"]:
                self.assertNotIn(" OR ", q, t["id"])
                self.assertTrue(q.strip())

    def test_claves_compilan_y_estan_normalizadas(self):
        for t in CAT["tendencias"]:
            for c in t["claves"] + t.get("excluir", []):
                re.compile(c)
                self.assertEqual(c, C.normalizar(c), f"{t['id']}: clave con mayúsculas o tildes: {c}")

    def test_cada_familia_y_mitad_tiene_tendencias(self):
        for f in CAT["familias"]:
            self.assertTrue(any(t["familia"] == f for t in CAT["tendencias"]), f)
        for m in CAT["mitades"]:
            self.assertGreaterEqual(sum(t["mitad"] == m for t in CAT["tendencias"]), 12)

    def test_fuentes_sin_duplicados(self):
        urls = [f["url"] for f in CONF["feeds"]]
        self.assertEqual(len(urls), len(set(urls)))
        for f in CONF["feeds"]:
            self.assertIn(f.get("nivel"), (1, 2))


class Texto(unittest.TestCase):
    def test_normalizar(self):
        self.assertEqual(C.normalizar("  Energía  ÉÓLICA y “IA” "), 'energia eolica y "ia"')

    def test_limpiar_html(self):
        t = C.limpiar_html("<p>Hola &amp; <b>mundo</b>&#8217;s</p> The post X appeared first on Y.")
        self.assertEqual(t, "Hola & mundo's")
        largo = C.limpiar_html("palabra " * 200, maximo=50)
        self.assertLessEqual(len(largo), 51)
        self.assertTrue(largo.endswith("…"))

    def test_misma_historia_en_distintos_titulares(self):
        h = lambda t: C.huella(C.normalizar(t))
        a = h("Singapore lithium battery recycling startup Neu Battery Materials raises US$7.6 million")
        b = h("NEU Battery Materials Raises Oversubscribed $7.6 Million To Scale LFP Battery Recycling")
        c = h("Ford recalls 90,000 trucks over battery fire risk")
        self.assertTrue(C.parecidos(a, b))
        self.assertFalse(C.parecidos(a, c))

    def test_url_canonica_e_id(self):
        a = "https://www.example.com/nota/?utm_source=rss&utm_medium=feed&id=7"
        b = "http://example.com/nota?id=7"
        self.assertEqual(C.url_canonica(a), C.url_canonica(b))
        self.assertEqual(C.id_senal(a), C.id_senal(b))


class Calidad(unittest.TestCase):
    def excl(self, titulo, fuente="Reuters"):
        return C.motivo_exclusion(C.normalizar(titulo), fuente, {m.lower() for m in CONF["medios_excluidos"]})

    def test_excluye_ruido(self):
        self.assertTrue(self.excl("Humanoid Robot Market Size to Reach USD 38 Billion by 2032, CAGR 45%"))
        self.assertTrue(self.excl("Nvidia stock soars after earnings beat"))
        self.assertTrue(self.excl("Best robot vacuum deals for Prime Big Deal Days"))
        self.assertTrue(self.excl("3 quantum computing stocks to buy now"))
        self.assertTrue(self.excl("Why IonQ could be a great long-term pick", fuente="The Motley Fool"))
        self.assertTrue(self.excl("Human vs humanoid robot cage fight goes viral"))
        self.assertTrue(self.excl("The Download: open model trade-offs and geothermal power's promise"))
        self.assertTrue(self.excl("What's the difference between alkaline and lithium-ion batteries?"))
        self.assertTrue(self.excl("Highmark Health taps Karen Hanlon as CEO"))
        self.assertTrue(self.excl("What is Reskilling? 5 Concrete Examples", fuente="note"))

    def test_deja_pasar_noticias(self):
        self.assertIsNone(self.excl("Figure AI raises $1 billion to build humanoid robots for factories"))
        self.assertIsNone(self.excl("Researchers develop a sodium-ion battery that charges in five minutes"))
        self.assertIsNone(self.excl("Perú aprueba ley para impulsar el hidrógeno verde"))


class Tendencias(unittest.TestCase):
    def test_casos_claros(self):
        self.assertEqual(tend("Figure AI unveils new humanoid robot for BMW plant")[0], "humanoides")
        self.assertEqual(tend("Waymo expands robotaxi service to Miami")[0], "vehiculos-autonomos")
        self.assertEqual(tend("Researchers build solid-state battery with record energy density")[0], "baterias")
        self.assertIn("ia-agentica", tend("Salesforce launches AI agents for customer service"))
        self.assertIn("combustibles", tend("Perú aprueba ley para impulsar el hidrógeno verde"))
        self.assertIn("cuantica", tend("Google's quantum chip reaches error-correction milestone"))
        self.assertIn("minerales", tend("Copper supply crunch: Peru and Chile mines struggle"))
        self.assertIn("cadenas", tend("Mexico nearshoring boom draws new auto plants"))

    def test_falsos_positivos(self):
        self.assertNotIn("drones", tend("Drone strike hits fuel depot as war escalates"))
        self.assertNotIn("empaques", tend("TSMC expands advanced packaging capacity for AI chips"))
        self.assertNotIn("minerales", tend("Bitcoin mining firm buys more machines"))
        self.assertNotIn("ia-agentica", tend("Travel agents report record bookings this summer"))
        self.assertNotIn("economia-espacial", tend("Rocket Software announces acquisition of Geniez AI"))
        self.assertNotIn("nuclear", tend("AMD Helion brings agentic AI compute at rack scale"))
        self.assertNotIn("cadenas", tend("Trump is sticking with tariffs even though voters disapprove"))
        self.assertIn("cadenas", tend("New tariffs push automakers to move supply chains to Mexico"))
        self.assertIn("economia-espacial", tend("SpaceX rocket launch puts 27 satellites in orbit"))
        self.assertEqual(tend("The best pizza in New York, ranked"), [])

    def test_resumen_necesita_dos_claves_salvo_busqueda_propia(self):
        resumen = "The company said its new humanoid will ship next year."
        self.assertEqual(tend("Startup closes a big deal", resumen), [])
        self.assertIn("humanoides", tend("Startup closes a big deal", resumen, consulta="humanoides"))


class Tipos(unittest.TestCase):
    def tipo(self, t, r=""):
        return C.tipo_de(C.normalizar(t), C.normalizar(r))

    def test_tipos(self):
        self.assertEqual(self.tipo("Figure AI raises $1B in Series C"), "inversion")
        self.assertEqual(self.tipo("Researchers discover a new catalyst for green hydrogen"), "investigacion")
        self.assertEqual(self.tipo("Amazon launches drone delivery in Italy"), "lanzamiento")
        self.assertEqual(self.tipo("FDA approves first CRISPR therapy for a heart condition"), "regulacion")
        self.assertEqual(self.tipo("Startup levanta ronda de 5 millones de dólares"), "inversion")
        self.assertEqual(self.tipo("Something happened somewhere"), "otro")

    def test_tipos_trampas(self):
        self.assertNotEqual(self.tipo("Data breach at H&M raises cybersecurity concerns"), "inversion")
        self.assertEqual(self.tipo("Alibaba launches smart glasses that take on Ray-Ban Meta"), "lanzamiento")
        self.assertEqual(self.tipo("Startup raises $50M to launch delivery drones"), "inversion")
        self.assertEqual(self.tipo("Amazon launches drone delivery after FAA approval"), "lanzamiento")

    def test_novedad(self):
        self.assertFalse(C.es_novedad(C.normalizar("Astronomers catch a star snacking on a brown dwarf"), "a novel observation"))
        self.assertTrue(C.es_novedad(C.normalizar("Scientists build a nuclear clock"), "the first-ever thorium clock"))
        self.assertTrue(C.es_novedad(C.normalizar("World's first wooden satellite returns data"), ""))
        self.assertFalse(C.es_novedad(C.normalizar("Company reports quarterly results"), ""))


class Lectura(unittest.TestCase):
    RSS = b"""<?xml version="1.0"?><rss version="2.0" xmlns:media="http://search.yahoo.com/mrss/"><channel>
      <item><title>Nuevo robot &amp; IA</title><link>https://a.com/1</link><pubDate>Mon, 12 Oct 2026 10:00:00 +0000</pubDate>
      <description>&lt;p&gt;Texto &lt;img src="https://a.com/i.jpg"&gt;&lt;/p&gt;</description></item>
      <item><title>Con media</title><link>https://a.com/2</link><pubDate>2026-10-12T08:00:00Z</pubDate><media:content url="https://a.com/m.png" medium="image"/></item>
    </channel></rss>"""
    ATOM = b"""<?xml version="1.0"?><feed xmlns="http://www.w3.org/2005/Atom"><entry><title>Atom uno</title>
      <link rel="alternate" href="https://b.com/x"/><updated>2026-10-11T09:30:00-04:00</updated><summary>Resumen</summary></entry></feed>"""
    RDF = b"""<?xml version="1.0"?><rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns="http://purl.org/rss/1.0/" xmlns:dc="http://purl.org/dc/elements/1.1/">
      <item rdf:about="https://c.com/p"><title>Paper RDF</title><link>https://c.com/p</link><dc:date>2026-10-10</dc:date></item></rdf:RDF>"""

    def test_rss(self):
        it = F.parse_feed(self.RSS, "A")
        self.assertEqual(len(it), 2)
        self.assertEqual(it[0]["titulo"], "Nuevo robot & IA")
        self.assertEqual(it[0]["imagen"], "https://a.com/i.jpg")
        self.assertEqual(it[1]["imagen"], "https://a.com/m.png")
        self.assertEqual(it[0]["fecha"], datetime(2026, 10, 12, 10, tzinfo=timezone.utc))

    def test_atom_y_rdf(self):
        a = F.parse_feed(self.ATOM, "B")[0]
        self.assertEqual(a["url"], "https://b.com/x")
        self.assertEqual(a["fecha"].astimezone(timezone.utc).hour, 13)
        r = F.parse_feed(self.RDF, "C")[0]
        self.assertEqual(r["titulo"], "Paper RDF")
        self.assertEqual(r["fecha"].date(), date(2026, 10, 10))

    def test_url_real_de_bing(self):
        link = "http://www.bing.com/news/apiclick.aspx?ref=FexRss&aid=&tid=x&url=https%3a%2f%2fwww.reuters.com%2ftech%2fnota&c=1"
        self.assertEqual(F._url_real(link), "https://www.reuters.com/tech/nota")


class Metricas(unittest.TestCase):
    def test_percentiles(self):
        p = M.percentiles({"a": 1.0, "b": 2.0, "c": 3.0, "d": None})
        self.assertEqual((p["a"], p["b"], p["c"], p["d"]), (0.0, 0.5, 1.0, None))

    def conteos(self, hoy, reparto):
        """reparto: {tid: [lanz, inv, invest, reg, otro]} repartido en los últimos 10 días."""
        c = {}
        for i in range(10):
            d = (hoy - timedelta(days=i)).isoformat()
            c[d] = {tid: [v // 10 for v in fila] for tid, fila in reparto.items()}
        return c

    def test_horizonte_se_mueve_en_la_direccion_correcta_y_con_tope(self):
        hoy = date(2026, 10, 13)
        tends = [{"id": f"t{i}", "anios": 4} for i in range(8)]
        reparto = {f"t{i}": [50, 0, 50, 0, 0] for i in range(6)}
        reparto["t6"] = [100, 100, 0, 0, 0]      # todo mercado → se acerca
        reparto["t7"] = [0, 0, 200, 0, 0]        # todo investigación → se aleja
        h = M.horizontes(tends, self.conteos(hoy, reparto), hoy)
        self.assertLess(h["t6"]["anios"], 4)
        self.assertGreater(h["t7"]["anios"], 4)
        for v in h.values():
            self.assertTrue(4 * math.exp(-0.35) - 1e-9 <= v["anios"] <= 4 * math.exp(0.35) + 1e-9)
        self.assertAlmostEqual(h["t0"]["anios"], 4)

    def test_horizonte_compara_con_lo_tipico_de_su_plazo(self):
        # las lejanas tienen menos mercado que las cercanas: eso es lo normal y no las mueve
        hoy = date(2026, 10, 13)
        tends, reparto = [], {}
        for i, (base, merc) in enumerate([(1, 90), (2, 85), (3, 80), (5, 70), (7, 60), (10, 50), (2, 85), (9, 52)]):
            tends.append({"id": f"t{i}", "anios": base})
            reparto[f"t{i}"] = [merc, 0, 100 - merc, 0, 0]
        reparto["t7"] = [95, 0, 5, 0, 0]  # lejana (9 años) pero con mercado de tendencia cercana → se acerca
        h = M.horizontes(tends, self.conteos(hoy, reparto), hoy)
        self.assertLess(h["t7"]["anios"], 9 * 0.85)
        for tid in ("t0", "t1", "t2", "t3", "t4"):
            self.assertLess(abs(h[tid]["anios"] / h[tid]["base"] - 1), 0.15, tid)

    def test_horizonte_sin_senales_no_se_mueve(self):
        hoy = date(2026, 10, 13)
        h = M.horizontes([{"id": "x", "anios": 7}], {}, hoy)
        self.assertEqual(h["x"]["anios"], 7)

    def test_impulso_en_rango(self):
        hoy = date(2026, 10, 13)
        tends = [{"id": "a"}, {"id": "b"}, {"id": "c"}]
        wiki = {"a": {"serie": {f"2026-0{m}": 100 * m for m in range(1, 10)}}, "b": {"serie": {f"2026-0{m}": 900 for m in range(1, 10)}}}
        papers = {"a": {"reciente": 300, "previo": 100}, "c": {"reciente": 10, "previo": 100}}
        conteos = {hoy.isoformat(): {"a": [5, 0, 0, 0, 0], "b": [1, 0, 0, 0, 0]}}
        imp = M.impulso(tends, wiki, papers, conteos, hoy)
        for v in imp.values():
            self.assertTrue(0 <= v["impulso"] <= 100)
        self.assertGreater(imp["a"]["impulso"], imp["c"]["impulso"])

    def test_cambios(self):
        hoy = date(2026, 10, 13)
        hist = {(hoy - timedelta(days=7)).isoformat(): {"a": [40, 3.0], "b": [60, 5.0]}, hoy.isoformat(): {"a": [70, 2.5], "b": [45, 5.6]}}
        c = M.cambios(hist, hoy, {"a": "A", "b": "B"})
        self.assertEqual(c["dias"], 7)
        self.assertEqual(c["acelera"][0]["id"], "a")
        self.assertEqual(c["enfria"][0]["id"], "b")
        self.assertEqual(c["acerca"][0]["id"], "a")
        self.assertEqual(c["aleja"][0]["id"], "b")


class Proceso(unittest.TestCase):
    def item(self, titulo, url, horas=1, fuente="Reuters", origen="rss", nivel=1, consulta=None):
        return {"titulo": titulo, "url": url, "fecha": AHORA - timedelta(hours=horas), "resumen": "", "imagen": None,
                "fuente": fuente, "origen": origen, "nivel": nivel, "consulta_de": consulta}

    def test_procesar_cuenta_agrupa_y_no_repite(self):
        estado, senales = {}, {}
        items = [
            self.item("Figure AI unveils a new humanoid robot for car factories", "https://a.com/1"),
            self.item("Figure AI unveils new humanoid robot for car factories, report says", "https://b.com/2", fuente="The Verge", nivel=1),
            self.item("Nvidia stock soars on AI chip demand", "https://c.com/3"),
            self.item("Old news about humanoid robots", "https://d.com/4", horas=24 * 60),
            self.item("World's first wooden satellite sends data from orbit", "https://e.com/5"),
        ]
        st = radar.procesar(items, CAT, CONF, estado, senales, AHORA)
        self.assertEqual(st["nuevas"], 3)
        self.assertEqual(st["viejas"], 1)
        self.assertEqual(sum(st["excluidas"].values()), 1)
        hum = senales["por_tendencia"]["humanoides"]
        self.assertEqual(len(hum), 1)           # dos medios, una sola historia
        self.assertEqual(hum[0]["n"], 2)
        dia = (AHORA - timedelta(hours=1)).date().isoformat()
        self.assertEqual(sum(estado["conteos"][dia]["humanoides"]), 2)
        self.assertTrue(any("economia-espacial" in s["tend"] for s in senales["ultimas"]))
        # segunda corrida con lo mismo: nada nuevo
        st2 = radar.procesar(items, CAT, CONF, estado, senales, AHORA)
        self.assertEqual(st2["nuevas"], 0)
        self.assertEqual(sum(estado["conteos"][dia]["humanoides"]), 2)


class Pagina(unittest.TestCase):
    def test_plantilla_tiene_un_solo_hueco(self):
        html = (RAIZ / "plantilla.html").read_text(encoding="utf-8")
        self.assertEqual(html.count("/*__DATOS__*/null"), 1)

    def test_javascript_de_la_plantilla_es_valido(self):
        node = shutil.which("node")
        if not node:
            self.skipTest("node no está instalado")
        html = (RAIZ / "plantilla.html").read_text(encoding="utf-8")
        js = re.search(r"<script>(.*)</script>", html, re.S).group(1).replace("/*__DATOS__*/null", "{}")
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "pagina.js"
            f.write_text(js, encoding="utf-8")
            r = subprocess.run([node, "--check", str(f)], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr[:800])

    def test_pagina_se_genera_y_no_se_rompe_con_script_en_titulos(self):
        estado, senales = {}, {}
        radar.procesar([{"titulo": "Humanoid robot </script><script>alert(1)</script> unveiled", "url": "https://x.com/1",
                         "fecha": AHORA, "resumen": "", "imagen": None, "fuente": "X", "origen": "rss", "nivel": 1}],
                       CAT, CONF, estado, senales, AHORA)
        datos = radar.datos_pagina(CAT, estado, senales, {}, AHORA, CONF)
        self.assertEqual(len(datos["tendencias"]), len(CAT["tendencias"]))
        with tempfile.TemporaryDirectory() as tmp:
            viejo = radar.SITE
            radar.SITE = Path(tmp)
            try:
                p = radar.construir_pagina(datos)
                html = p.read_text(encoding="utf-8")
            finally:
                radar.SITE = viejo
        self.assertNotIn("/*__DATOS__*/null", html)
        self.assertEqual(html.lower().count("</script>"), 1 + html.lower().count('<script src'))
        self.assertIn("<\\/script>", html)


class Flujo(unittest.TestCase):
    def test_workflow_prueba_antes_de_publicar(self):
        wf = (RAIZ / ".github" / "workflows" / "actualizar.yml").read_text(encoding="utf-8")
        self.assertIn("cron:", wf)
        self.assertLess(wf.index("unittest"), wf.index("python radar.py"))
        self.assertLess(wf.index("python radar.py"), wf.index("deploy-pages"))


AHORA = datetime(2026, 10, 13, 15, 0, tzinfo=timezone.utc)

if __name__ == "__main__":
    unittest.main()
