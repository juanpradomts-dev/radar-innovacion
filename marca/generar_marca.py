"""Genera og.png (vista previa al compartir, 1200x630) e icono-180.png con un navegador sin ventana.

    python marca/generar_marca.py
Requiere Edge o Chrome instalados (Windows) o chromium en PATH.
"""
import shutil
import subprocess
import tempfile
from pathlib import Path

AQUI = Path(__file__).resolve().parent
CANDIDATOS = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    shutil.which("chromium") or "", shutil.which("google-chrome") or "",
]

PUNTOS = [(0.62, -0.55, "#1B6BD3", 9), (0.35, -0.2, "#1B6BD3", 7), (0.75, 0.25, "#1B6BD3", 6), (0.2, 0.5, "#1B6BD3", 8),
          (-0.5, -0.6, "#0E8F66", 9), (-0.3, -0.1, "#0E8F66", 6), (-0.7, 0.3, "#0E8F66", 7), (-0.25, 0.62, "#0E8F66", 6),
          (0.12, -0.75, "#1B6BD3", 6), (-0.12, -0.42, "#0E8F66", 8), (0.5, 0.6, "#1B6BD3", 6), (-0.55, -0.25, "#0E8F66", 5)]


def radar_svg(tam: int) -> str:
    c, r = tam / 2, tam / 2 - tam * .03
    pts = "".join(f'<circle cx="{c + x * r * .82:.1f}" cy="{c + y * r * .82:.1f}" r="{s * tam / 420:.1f}" fill="{col}" stroke="#fff" stroke-width="{2.4 * tam / 420:.1f}"/>' for x, y, col, s in PUNTOS)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" style="flex:none" width="{tam}" height="{tam}" viewBox="0 0 {tam} {tam}">
<defs><radialGradient id="a" cx="{c}" cy="{c}" r="{r}" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#BFE6D3"/><stop offset="1" stop-color="#F5FBF8"/></radialGradient>
<radialGradient id="b" cx="{c}" cy="{c}" r="{r}" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#C3D9F6"/><stop offset="1" stop-color="#F4F8FE"/></radialGradient>
<linearGradient id="g" x1="0" x2="1"><stop offset="0" stop-color="#0E8F66"/><stop offset=".5" stop-color="#1592A0"/><stop offset="1" stop-color="#1B6BD3"/></linearGradient></defs>
<circle cx="{c}" cy="{c}" r="{r}" fill="none" stroke="url(#g)" stroke-width="{tam * .05:.1f}"/>
<path d="M{c},{c - r * .95} A{r * .95},{r * .95} 0 0 0 {c},{c + r * .95} Z" fill="url(#a)"/>
<path d="M{c},{c - r * .95} A{r * .95},{r * .95} 0 0 1 {c},{c + r * .95} Z" fill="url(#b)"/>
<circle cx="{c}" cy="{c}" r="{r * .5}" fill="none" stroke="#5E7A8C" stroke-opacity=".5" stroke-width="{tam / 260:.1f}"/>
<circle cx="{c}" cy="{c}" r="{r * .8}" fill="none" stroke="#5E7A8C" stroke-opacity=".5" stroke-width="{tam / 260:.1f}"/>
<line x1="{c - r * .95}" y1="{c}" x2="{c + r * .95}" y2="{c}" stroke="#5E7A8C" stroke-opacity=".45" stroke-width="{tam / 300:.1f}"/>
{pts}
<circle cx="{c}" cy="{c}" r="{tam / 45:.1f}" fill="#E5413A" stroke="#fff" stroke-width="{tam / 140:.1f}"/></svg>'''


def html_og() -> str:
    return f'''<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;600&family=Outfit:wght@700&display=swap" rel="stylesheet">
<style>html,body{{margin:0;width:1200px;height:630px;overflow:hidden}}
body{{background:#F4F6F9;font-family:"DM Sans",sans-serif;color:#13202C;display:flex;align-items:center;gap:40px;padding:0 60px;box-sizing:border-box}}
h1{{font-family:Outfit,sans-serif;font-size:70px;line-height:1;margin:0 0 18px;letter-spacing:-.02em}}
p{{font-size:28px;line-height:1.35;color:#3A4856;margin:0 0 26px;max-width:560px}}
.chips span{{display:inline-block;font-size:21px;font-weight:600;border-radius:99px;padding:8px 18px;margin:0 8px 10px 0}}
.s{{background:#DCF2E8;color:#0A6B4C}}.t{{background:#DCE8F9;color:#14529F}}.v{{background:#13202C;color:#fff}}</style></head>
<body><div style="flex:1"><h1>Radar de<br>Innovación</h1><p>Las tendencias que están cambiando el mundo, medidas con noticias, ciencia e interés público.</p>
<div class="chips"><span class="t">Tecnología</span><span class="s">Sociedad y negocio</span><span class="v">Se actualiza solo</span></div></div>
{radar_svg(520)}</body></html>'''


def captura(html: str, salida: Path, ancho: int, alto: int):
    nav = next((c for c in CANDIDATOS if c and Path(c).exists()), None)
    if not nav:
        raise SystemExit("No encontré Edge/Chrome para generar las imágenes.")
    with tempfile.TemporaryDirectory() as tmp:
        f = Path(tmp) / "x.html"
        f.write_text(html, encoding="utf-8")
        subprocess.run([nav, "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--window-size={ancho},{alto}",
                        "--virtual-time-budget=4000", f"--screenshot={salida}", f.as_uri()], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=60)
    print("ok", salida)


if __name__ == "__main__":
    captura(html_og(), AQUI / "og.png", 1200, 630)
    icono = f'<!doctype html><html><body style="margin:0;background:#fff">{(AQUI / "favicon.svg").read_text(encoding="utf-8").replace("<svg ", "<svg width=\"180\" height=\"180\" ", 1)}</body></html>'
    captura(icono, AQUI / "icono-180.png", 180, 180)
