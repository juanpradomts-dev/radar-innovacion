---
version: 1
slug: "plantilla-html"
primary_target: "plantilla.html"
related_targets: []
---

## Scope

Página única del Radar de Innovación (`plantilla.html` → `site/index.html`). Modo de visitante: **Operate** (explorar tendencias, filtrar, abrir fichas), con pasajes Read (fichas y metodología). Construcción code-led.

Áreas de trabajo, en orden: filtros (con «¿Qué estudias?» primero) + radar + «Con más impulso»; «Para decidir» (acciones, matriz de decisión, cerca de ti, dónde se invierte, oportunidades en Perú); «Lo último» agrupado Perú → Latinoamérica → mundo; «Fuera del radar»; tabla de todas las tendencias.

## Audience and job

Estudiantes universitarios (sobre todo UCSUR) que llegan por un enlace: enterarse de qué se mueve, investigar una tendencia para un trabajo, buscar ideas de proyectos. Constraints: colores UCSUR sin logo ni nombre de la universidad; firma «Proyecto estudiantil · Juan Prado»; animaciones que respondan a un clic visibles aunque Windows reporte reduced-motion.

## Direction contract

THESIS: Un radar vivo vestido con la identidad bicolor de la UCSUR: la mitad naranja (sociedad y negocio) y la mitad azul (tecnología) son a la vez el mapa y la marca. Rechaza el dashboard gris con un solo acento y el informe estático en PDF.

OWN-WORLD: Barra superior azul #1D428A con texto blanco; fondo tintado #F3F6FB; tarjetas blancas con borde #DCE3EE. Radar con banda segmentada de cuatro arcos separados por cortes blancos: izquierda naranja #F56200 con texto azul noche, derecha azul #1D428A con texto blanco, arriba y abajo azul noche #0D2960 para el eje de impacto. Puntos naranja #F56200 y azul #2557A8 con anillo blanco de 2 px, etiquetas en píldoras blancas. Montserrat para títulos y cifras, Source Sans 3 para texto y etiquetas. Tipos de señal en aqua #1BAF7A, oro #EDA100, violeta #4A3AA7 y magenta #E87BA4, con el color siempre en el punto y nunca en la letra.

STORY: En 5 segundos el visitante entiende que es un mapa de tendencias que se actualiza solo. Toca un punto, lee qué es la tendencia, por qué importa y qué pasó esta semana, y vuelve porque siempre hay algo nuevo.

FIRST VIEWPORT: Barra azul a todo el ancho con el nombre, una frase de qué es, la navegación por secciones y el estado de actualización. Debajo, tres áreas: filtros a la izquierda (260 px), el radar al centro como el elemento más grande, con «Toca un punto» y la leyenda de mitades encima, y «Con más impulso» a la derecha. La acción principal es tocar un punto del radar.

FORM: DHL Logistics Trend Radar, fijado por el brief del autor (captura de referencia); se corrió el sorteo sin que imprimiera referencia de semilla, y la dirección fijada por el autor prevalece sobre él. seed: none (unavailable). Movimiento distintivo: una aguja barre el radar una sola vez al cargar y las tendencias nacen a su paso; las 5 con más impulso emiten un solo pulso. Al señalar un punto, o una fila de «Con más impulso», de la tabla o una etiqueta de tendencia, su punto crece y se enciende con un anillo, y el resto del radar baja la voz. Al filtrar, las que quedan asienten una vez. Al cerrar una ficha, su punto queda marcado un momento. Pedido del autor (2026-10-14): animaciones pocas y sin exagerar, para no abrumar.

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance

## Unresolved

- La sección de investigación queda sin datos hasta que exista la clave de OpenAlex.
