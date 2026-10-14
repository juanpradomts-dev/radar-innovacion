# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Estudiantes universitarios en general, sobre todo de la UCSUR (Lima, Perú), que llegan por un enlace compartido en grupos o redes. Entran desde el celular o la laptop, muchas veces sin saber qué es un "radar de tendencias". El autor (Juan Prado, Ingeniería Industrial) también lo usa como su propia herramienta de vigilancia.

Tres trabajos, todos confirmados por el autor:
1. **Enterarse de qué se mueve:** 2 minutos para ver qué tendencias suben y leer lo último.
2. **Investigar:** profundizar en una tendencia para un trabajo o paper (datos, artículos científicos, fuentes enlazadas al original).
3. **Buscar ideas:** inspiración para proyectos, emprendimientos, hackathones y tesis.

## Product Purpose

Un radar de innovación al estilo del DHL Logistics Trend Radar que, a diferencia de un informe estático, se actualiza solo cada 3 horas con noticias, interés público (Wikipedia) y producción científica (OpenAlex). Éxito: que un visitante nuevo entienda en 5 segundos qué es y cuál es el primer clic, y que vuelva porque siempre hay algo nuevo.

## Positioning

Radar vivo y medido: cada punto se mueve con evidencia (lanzamientos e inversiones frente a investigación), cada tendencia enlaza a sus noticias originales, y la metodología y sus límites están a la vista. En español, pensado para estudiantes latinoamericanos.

## Operating Context

- Publicado en GitHub Pages (https://juanpradomts-dev.github.io/radar-innovacion/); GitHub Actions lo regenera cada 3 h. Página estática con datos embebidos; funciona también abriendo el archivo local.
- Se comparte por enlace; cada tendencia tiene enlace propio (`#t=<id>`).
- Las fuentes son mayormente en inglés; la interfaz y las fichas están en español.

## Capabilities and Constraints

- 49 tendencias en dos mitades: Tecnología y Sociedad y negocio. Distancia al centro = años hasta la adopción; altura = impacto; tamaño = impulso (0-100).
- Filtro principal «¿Qué estudias?» (15 carreras, mapeo editorial) más sector, área de impacto y familia (una opción por grupo) y búsqueda.
- Pedido del autor (2026-10-13): **prioridad a lo cercano** (Perú, luego Latinoamérica, luego el mundo) y **datos para decidir**: acción sugerida por tendencia (Actuar ahora / Prepararse / Explorar / Vigilar, con la regla a la vista), matriz de decisión, señales de Perú y la región, dónde se invierte y oportunidades en Perú.
- Ficha por tendencia con indicadores y gráficos; «Lo último» agrupado por región; «Fuera del radar»; tabla completa ordenable.
- Clasificación local por reglas, sin IA ni costo. La posición base es una estimación editorial; el impulso y el ajuste del horizonte son automáticos.
- HTML/CSS/JS vanilla, sin build ni frameworks; fuentes de Google Fonts.
- La sección de investigación depende de OpenAlex, que puede quedar sin datos si falta la clave gratuita.

## Brand Commitments

- Colores de la Universidad Científica del Sur: naranja #F56200 y azul #1D428A (tomados de cientifica.edu.pe). Pedido explícito del autor.
- **No es una página oficial de la UCSUR:** sin logo ni nombre de la universidad. Firma en el pie: «Proyecto estudiantil · Juan Prado», con enlace a su GitHub.
- Nombre del producto: «Radar de Innovación».

## Evidence on Hand

- Datos reales en `datos/` y `site/datos.json` (señales de 41 feeds, Bing News, Wikipedia, OpenAlex).
- Sin testimonios, usuarios ni métricas de uso: no inventarlos.

## Product Principles

1. Claridad a primera vista por encima de la cantidad de funciones.
2. Cada número es verificable: enlaza a su fuente o explica cómo se calcula.
3. Honestidad sobre los límites (estimación editorial, sesgo hacia medios en inglés, datos que faltan).
4. Movimiento con propósito: responde a una acción o informa algo; nunca decoración en bucle.

## Accessibility & Inclusion

- Uso frecuente en celular: objetivos táctiles amplios, sin desplazamiento horizontal.
- El equipo del autor tiene Windows con las animaciones del sistema apagadas (`prefers-reduced-motion: reduce`): los fundidos y el movimiento que responde a un clic deben verse igual; solo lo que se mueve en bucle depende de esa preferencia.
- Contraste de texto mínimo 4.5:1; los colores nunca son el único canal de identidad.
