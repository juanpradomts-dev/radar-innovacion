# Radar de Innovación

Un radar al estilo del *Logistics Trend Radar* de DHL, pero que **se actualiza solo**: 49 tendencias de tecnología y de sociedad y negocio, medidas varias veces al día con noticias, ciencia e interés público.

**Página:** https://juanpradomts-dev.github.io/radar-innovacion/

## Cómo se lee

- **Mitad izquierda:** sociedad y negocio. **Mitad derecha:** tecnología.
- **Distancia al centro:** años estimados hasta la adopción masiva (el centro es hoy).
- **Altura:** impacto esperado (arriba, más).
- **Tamaño del punto:** impulso, de 0 a 100, relativo a las demás tendencias.

## Qué se actualiza solo

| Qué | Fuente | Frecuencia |
|---|---|---|
| Noticias por tendencia | 41 feeds RSS de medios (`fuentes.json`) + Bing News RSS (1–2 búsquedas por tendencia) | cada 3 h |
| Interés público | Vistas mensuales de Wikipedia (API de Wikimedia) | 1 vez al día |
| Ciencia | Artículos por año en OpenAlex | 1 vez al día |

Con eso se calculan:

- **Impulso** = 30 % crecimiento de vistas en Wikipedia (3 meses vs. 3 anteriores) + 20 % crecimiento de papers (último año completo vs. el anterior) + 30 % volumen de noticias (14 días) + 20 % aceleración de noticias (7 días vs. las 4 semanas previas; se activa con 5 semanas de historia). Todo en percentiles.
- **Horizonte**: parte de la estimación base de `tendencias.json` y se mueve hasta ±30 % según la mezcla de señales de 60 días. La proporción de lanzamientos e inversiones se compara con lo típico para su plazo (recta ajustada sobre todas las tendencias contra el logaritmo de los años base): más mercado del esperado → se acerca; menos → se aleja.
- **Fuera del radar**: novedades de los feeds que no encajan en ninguna tendencia (candidatas a tendencia nueva).

La clasificación es local, por palabras clave (sin IA ni costo). Se descartan notas de bolsa, informes de mercado pagados, ofertas y reseñas.

## Uso local

```bash
python radar.py            # recolecta, mide y genera site/index.html (3–5 min)
python radar.py --sin-red  # solo regenera la página con los datos guardados
python radar.py --abrir    # abre la página al terminar
python -m unittest -v test_radar
```

Solo usa la biblioteca estándar de Python (3.10+).

## Archivos

- `tendencias.json` — catálogo: nombre, mitad, familia, impacto, años base, claves de búsqueda, artículos de Wikipedia, consulta de OpenAlex. **Aquí se agregan o ajustan tendencias.**
- `fuentes.json` — feeds RSS, medios de referencia y medios excluidos.
- `radar.py` (orquesta), `fuentes.py` (red), `clasificar.py` (reglas), `metricas.py` (cálculos), `plantilla.html` (página).
- `datos/` — estado acumulado (lo guarda el robot en cada corrida): conteos diarios, historial de posiciones, señales para mostrar y mediciones diarias.
- `.github/workflows/actualizar.yml` — corre las pruebas, actualiza y publica en GitHub Pages cada 3 h.

## OpenAlex

Sin clave, OpenAlex da un presupuesto diario pequeño compartido por IP, que en GitHub Actions puede estar agotado. Con una clave gratuita (https://help.openalex.org/api/authentication/) guardada como secreto `OPENALEX_API_KEY` del repo, la medición científica es estable. Si falla, el radar conserva el último dato y reintenta cada 6 h.

## Respeto a las fuentes

Se lee robots.txt de cada medio antes de su feed (por eso se omite Logistics Viewpoints) y se espera 1 s entre búsquedas. Los titulares enlazan siempre al medio original.
