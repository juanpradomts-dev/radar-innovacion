"""Genera og.png (vista previa al compartir, 1200x630) e icono-180.png con un navegador sin ventana.

    python marca/generar_marca.py
Requiere Edge o Chrome instalados (Windows) o chromium en PATH. Paleta UCSUR: naranja #F56200, azul #1D428A.
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

# (x, y) relativos al radio, mitad (s = sociedad, t = tecnología), tamaño
PUNTOS = [(0.62, -0.55, "t", 9), (0.35, -0.2, "t", 7), (0.75, 0.25, "t", 6), (0.2, 0.5, "t", 8), (0.12, -0.75, "t", 6), (0.5, 0.6, "t", 6),
          (-0.5, -0.6, "s", 9), (-0.3, -0.1, "s", 6), (-0.7, 0.3, "s", 7), (-0.25, 0.62, "s", 6), (-0.12, -0.42, "s", 8), (-0.55, -0.25, "s", 5)]


def radar_svg(tam: int) -> str:
    c, r = tam / 2, tam / 2 - tam * .045
    k = tam / 420
    col = {"s": "#F56200", "t": "#2557A8"}
    pts = "".join(f'<circle cx="{c + x * r * .8:.1f}" cy="{c + y * r * .8:.1f}" r="{s * k:.1f}" fill="{col[m]}" stroke="#fff" stroke-width="{2.4 * k:.1f}"/>' for x, y, m, s in PUNTOS)
    ri = r * .9

    def arco(a0, a1):
        import math
        p = lambda a: (c + r * math.sin(math.radians(a)), c - r * math.cos(math.radians(a)))
        (x0, y0), (x1, y1) = p(a0), p(a1)
        return f'M{x0:.1f},{y0:.1f} A{r:.1f},{r:.1f} 0 0 1 {x1:.1f},{y1:.1f}'
    banda = "".join(f'<path d="{arco(a0, a1)}" fill="none" stroke="{color}" stroke-width="{tam * .075:.1f}"/>'
                    for a0, a1, color in [(-33, 33, "#0D2960"), (35, 145, "#1D428A"), (147, 213, "#0D2960"), (215, 325, "#F56200")])
    return f'''<svg xmlns="http://www.w3.org/2000/svg" style="flex:none" width="{tam}" height="{tam}" viewBox="0 0 {tam} {tam}">
<defs><radialGradient id="a" cx="{c}" cy="{c}" r="{ri}" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#FFD4B5"/><stop offset="1" stop-color="#FFF7F1"/></radialGradient>
<radialGradient id="b" cx="{c}" cy="{c}" r="{ri}" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#C7D6F0"/><stop offset="1" stop-color="#F5F8FD"/></radialGradient></defs>
{banda}
<path d="M{c},{c - ri} A{ri},{ri} 0 0 0 {c},{c + ri} Z" fill="url(#a)"/>
<path d="M{c},{c - ri} A{ri},{ri} 0 0 1 {c},{c + ri} Z" fill="url(#b)"/>
<circle cx="{c}" cy="{c}" r="{ri * .52}" fill="none" stroke="#6A7D9C" stroke-opacity=".5" stroke-width="{tam / 280:.1f}"/>
<circle cx="{c}" cy="{c}" r="{ri * .84}" fill="none" stroke="#6A7D9C" stroke-opacity=".5" stroke-width="{tam / 280:.1f}"/>
<line x1="{c - ri}" y1="{c}" x2="{c + ri}" y2="{c}" stroke="#6A7D9C" stroke-opacity=".45" stroke-width="{tam / 320:.1f}"/>
{pts}
<circle cx="{c}" cy="{c}" r="{tam / 44:.1f}" fill="#0D2960" stroke="#fff" stroke-width="{tam / 130:.1f}"/></svg>'''


def html_og() -> str:
    return f'''<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@700;800&family=Source+Sans+3:wght@400;600&display=swap" rel="stylesheet">
<style>html,body{{margin:0;width:1200px;height:630px;overflow:hidden}}
body{{background:#1D428A;font-family:"Source Sans 3",sans-serif;color:#fff;display:flex;align-items:center;gap:36px;padding:0 56px;box-sizing:border-box}}
h1{{font-family:Montserrat,sans-serif;font-weight:800;font-size:68px;line-height:1.02;margin:0 0 20px;letter-spacing:-.02em}}
h1 span{{color:#F56200}}
p{{font-size:29px;line-height:1.35;color:#D6E0F2;margin:0 0 28px;max-width:540px}}
.chips span{{display:inline-block;font-size:22px;font-weight:600;border-radius:99px;padding:8px 18px;margin:0 8px 10px 0;background:rgba(255,255,255,.12)}}
.chips b{{display:inline-block;width:12px;height:12px;border-radius:50%;margin-right:9px;vertical-align:1px}}
.r{{background:#fff;border-radius:50%;padding:12px;flex:none}}</style></head>
<body><div style="flex:1"><h1>Radar de<br><span>Innovación</span></h1><p>Las tendencias que están cambiando el mundo, medidas cada 3 horas.</p>
<div class="chips"><span><b style="background:#F56200"></b>Sociedad y negocio</span><span><b style="background:#8FB0E8"></b>Tecnología</span></div></div>
<div class="r">{radar_svg(500)}</div></body></html>'''


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
    svg = (AQUI / "favicon.svg").read_text(encoding="utf-8").replace("<svg ", '<svg width="180" height="180" ', 1)
    captura(f'<!doctype html><html><body style="margin:0;background:#fff">{svg}</body></html>', AQUI / "icono-180.png", 180, 180)
