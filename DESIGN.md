---
name: Radar de Innovación
description: Radar vivo de 49 tendencias, vestido con el bicolor naranja y azul de la UCSUR.
colors:
  azul: "#1D428A"
  azul-noche: "#0D2960"
  azul-dato: "#2557A8"
  azul-suave: "#E8EEF8"
  azul-texto: "#C3D0EA"
  naranja: "#F56200"
  naranja-texto: "#B84A00"
  naranja-suave: "#FFF0E5"
  naranja-pista: "#FFE1CC"
  sobre-naranja: "#0A1F47"
  fondo: "#F3F6FB"
  tarjeta: "#FFFFFF"
  plano: "#F6F8FC"
  tinta: "#14213D"
  tinta-2: "#34435E"
  muted: "#56657E"
  linea: "#DCE3EE"
  linea-2: "#EAEFF6"
  borde-hover: "#B8C4D6"
  t-lanzamiento: "#1BAF7A"
  t-inversion: "#EDA100"
  t-investigacion: "#4A3AA7"
  t-regulacion: "#E87BA4"
  t-otro: "#A7B1C2"
  a-actuar: "#0D2960"
  a-preparar: "#1D428A"
  a-explorar: "#5A79B8"
  a-vigilar: "#93A8D4"
  bien: "#0F8A5F"
  mal: "#C2362F"
typography:
  display:
    fontFamily: "Montserrat, system-ui, sans-serif"
    fontSize: "30px"
    fontWeight: 800
    lineHeight: 1.12
    letterSpacing: "-0.01em"
  headline:
    fontFamily: "Montserrat, system-ui, sans-serif"
    fontSize: "23px"
    fontWeight: 800
    lineHeight: 1.1
    letterSpacing: "-0.01em"
  title:
    fontFamily: "Montserrat, system-ui, sans-serif"
    fontSize: "17px"
    fontWeight: 700
    lineHeight: 1.3
  numeral:
    fontFamily: "Montserrat, system-ui, sans-serif"
    fontSize: "25px"
    fontWeight: 700
    lineHeight: 1.1
    fontFeature: "tnum"
  body:
    fontFamily: "Source Sans 3, system-ui, -apple-system, Segoe UI, sans-serif"
    fontSize: "16px"
    fontWeight: 400
    lineHeight: 1.5
  body-lectura:
    fontFamily: "Source Sans 3, system-ui, -apple-system, Segoe UI, sans-serif"
    fontSize: "16.5px"
    fontWeight: 400
    lineHeight: 1.55
  label:
    fontFamily: "Source Sans 3, system-ui, -apple-system, Segoe UI, sans-serif"
    fontSize: "14px"
    fontWeight: 600
    lineHeight: 1.2
rounded:
  muestra: "3px"
  etiqueta: "5px"
  fila: "8px"
  control: "10px"
  panel: "12px"
  tarjeta: "16px"
  ficha: "22px"
  pildora: "999px"
spacing:
  chip: "6px"
  fila: "8px"
  control: "12px"
  tarjeta: "16px"
  tablero: "18px"
  seccion: "22px"
  columna: "28px"
components:
  caja:
    backgroundColor: "{colors.tarjeta}"
    rounded: "{rounded.tarjeta}"
    padding: "16px"
  chip:
    backgroundColor: "{colors.tarjeta}"
    textColor: "{colors.tinta}"
    typography: "{typography.label}"
    rounded: "{rounded.pildora}"
    padding: "6px 11px"
    height: "34px"
  chip-activo:
    backgroundColor: "{colors.azul}"
    textColor: "{colors.tarjeta}"
    rounded: "{rounded.pildora}"
  chip-sociedad-activo:
    backgroundColor: "{colors.naranja}"
    textColor: "{colors.sobre-naranja}"
    rounded: "{rounded.pildora}"
  segmento-activo:
    backgroundColor: "{colors.azul}"
    textColor: "{colors.tarjeta}"
    rounded: "{rounded.pildora}"
    padding: "7px 13px"
    height: "36px"
  boton:
    backgroundColor: "{colors.tarjeta}"
    textColor: "{colors.tinta}"
    rounded: "{rounded.pildora}"
    padding: "9px 18px"
    height: "40px"
  boton-icono:
    backgroundColor: "{colors.tarjeta}"
    textColor: "{colors.tinta}"
    rounded: "{rounded.pildora}"
    size: "40px"
  selector-carrera:
    backgroundColor: "{colors.tarjeta}"
    textColor: "{colors.tinta}"
    rounded: "{rounded.control}"
    padding: "10px 36px 10px 12px"
  buscador:
    backgroundColor: "{colors.fondo}"
    textColor: "{colors.tinta}"
    rounded: "{rounded.control}"
    padding: "9px 12px 9px 36px"
  barra-superior:
    backgroundColor: "{colors.azul}"
    textColor: "{colors.tarjeta}"
    padding: "16px 20px"
  enlace-nav:
    textColor: "{colors.tarjeta}"
    rounded: "{rounded.pildora}"
    padding: "7px 12px"
  globo:
    backgroundColor: "{colors.azul-noche}"
    textColor: "{colors.tarjeta}"
    rounded: "{rounded.control}"
    padding: "8px 11px"
  ficha:
    backgroundColor: "{colors.tarjeta}"
    textColor: "{colors.tinta}"
    rounded: "{rounded.ficha}"
    width: "min(920px, calc(100vw - 24px))"
  kpi:
    backgroundColor: "{colors.plano}"
    rounded: "{rounded.panel}"
    padding: "12px 14px"
---

# Design System: Radar de Innovación

## Overview

**Creative North Star: "El Radar Bicolor"**

El sistema es un instrumento de lectura antes que una página de marketing. El radar ocupa el centro y sus dos mitades son a la vez el mapa y la marca. A la izquierda, en naranja UCSUR, va sociedad y negocio; a la derecha, en azul UCSUR, va tecnología. Todo lo demás (filtros, listas, tabla, fichas) es un soporte claro sobre un fondo azulado muy suave, con tarjetas blancas y líneas finas.

La densidad es de tablero: mucha información por pantalla, ordenada por líneas de 1 px y por fondos planos, no por cajas dentro de cajas. Montserrat pone la voz en los títulos y en las cifras. Source Sans 3 se encarga de leer. El movimiento es escaso y siempre responde a algo: una aguja barre el radar una vez al cargar, un anillo enciende el punto enlazado y la ficha se abre con un fundido corto.

Rechazos confirmados por el autor:
- el panel gris con un solo acento;
- el informe estático en PDF;
- cualquier parecido con un sitio oficial (sin logo ni nombre de la universidad).

**Key Characteristics:**
- Bicolor con significado: el naranja es sociedad y negocio y el azul es tecnología, también fuera del radar.
- Estructura en azul: barra superior, chips activos y escala de acciones.
- Tarjetas blancas planas con una sola sombra suave; dentro, separación por líneas y fondos planos.
- Cifras en Montserrat con números tabulares.
- Color de dato en el punto, nunca en la letra.

## Colors

Un bicolor institucional (naranja cálido y azul profundo) sobre neutros tintados de azul, con una paleta de datos aparte validada para daltonismo.

### Primary
- **Azul UCSUR** (azul): barra superior, chips y segmentos activos, borde del selector de carrera, enlaces de texto, mitad derecha del radar. Es el color de la estructura.
- **Azul noche** (azul-noche): banda superior e inferior del radar (eje de impacto), globo de ayuda, fondo del velo de la ficha y nivel más intenso de la escala de acciones.
- **Azul dato** (azul-dato): los puntos de tecnología. Es un azul algo más claro que el UCSUR para que el punto se separe de la banda.

### Secondary
- **Naranja UCSUR** (naranja): mitad izquierda del radar, puntos de sociedad y negocio, chips activos de familias sociales, íconos de encabezado, medidores de impulso y contorno de foco.
- **Naranja texto** (naranja-texto): la única forma de escribir en naranja sobre blanco, por ejemplo la marca «Perú» en las noticias.
- **Azul tinta sobre naranja** (sobre-naranja): todo texto que va encima del naranja.
- **Naranja suave y pista** (naranja-suave, naranja-pista): fondo de la marca «Perú» y riel de los medidores.

### Tertiary
- **Tipos de señal:** lanzamiento en aqua (t-lanzamiento), inversión en oro (t-inversion), investigación en violeta (t-investigacion), regulación en magenta (t-regulacion) y otro en gris (t-otro). Se usan en puntos y barras, nunca en texto.
- **Escala de acciones** (a-actuar → a-vigilar): un solo tono azul de oscuro a claro para Actuar ahora, Prepararse, Explorar y Vigilar.
- **Sube y baja** (bien, mal): solo en las flechas de cambio de posición.

### Neutral
- **Fondo azulado** (fondo): lienzo de la página y relleno del buscador.
- **Blanco tarjeta** (tarjeta): tarjetas, ficha, chips en reposo y píldoras de etiqueta del radar.
- **Plano** (plano): paneles dentro de una tarjeta (KPI, cifras, gráficos) y hover de las noticias.
- **Tinta** (tinta): texto principal. **Tinta 2** (tinta-2): texto secundario fuerte, encabezados de grupo. **Apagado** (muted): notas, conteos y metadatos.
- **Línea** (linea): borde de tarjetas y controles. **Línea 2** (linea-2): separadores internos. **Borde hover** (borde-hover): borde de chips, botones y etiquetas al pasar el mouse.

### Named Rules
**La regla de las dos mitades.** El naranja significa sociedad y negocio y el azul significa tecnología en todo el sitio. Un chip, una bola o un punto naranja nunca representa una tendencia de tecnología.

**La regla del texto sobre naranja.** Sobre el naranja #F56200 el texto es azul tinta (sobre-naranja), nunca blanco. Para escribir en naranja sobre blanco se usa naranja-texto.

**La regla del color en el punto.** Los colores de tipo de señal y de acción viven en puntos, cuadros y barras. La palabra que los acompaña va siempre en tinta.

## Typography

**Display Font:** Montserrat (con system-ui, sans-serif)
**Body Font:** Source Sans 3 (con system-ui, -apple-system, Segoe UI, sans-serif)

**Character:** Montserrat es geométrica y firme, cercana a la voz de la universidad, y se reserva para títulos y números. Source Sans 3 es humanista y compacta, y aguanta etiquetas de 13 px y párrafos largos sin cansar.

### Hierarchy
- **Display** (800, 30px, 1.12): título de la ficha de una tendencia.
- **Headline** (800, 23px, 1.1): nombre del sitio en la barra (20px en el celular) y encabezados de sección.
- **Title** (700–800, 17px): encabezados de tarjetas laterales y de paneles de «Para decidir».
- **Numeral** (700, 19–25px, números tabulares): KPI de la ficha y cifras de la semana.
- **Body** (400, 16px, 1.5): texto general. **Lectura** (16.5px, 1.55, máximo 72ch): párrafos «Qué es» y «Por qué importa» de la ficha.
- **Label** (600, 13.5–15px): chips, etiquetas del radar, filas de listas, metadatos.

### Named Rules
**La regla de las cifras.** Toda cifra que se compara (impulso, años, historias, KPI) usa números tabulares; las cifras protagonistas van en Montserrat.

**La regla del piso de 12.** Ningún texto HTML baja de 12px. La marca de lugar usa 12px en negrita y los conteos de los chips, 12.5px.

## Layout

- **Contenedor:** ancho máximo de 1480px, centrado, con 20px de lado (14px en el celular).
- **Tablero:** en escritorio son tres columnas: filtros de 270px, radar flexible y lateral de 300px, con 18px entre ellas.
  - Hasta 1180px el lateral baja debajo, en una rejilla automática de columnas de 280px como mínimo.
  - Hasta 860px todo va en una columna, en este orden: filtros, radar y lateral. Los filtros secundarios se pliegan en «Más filtros».
- **Secciones:** van una debajo de otra, separadas por 22px, con 20px de relleno (16 × 14 en el celular).
- **«Para decidir»:** las filas de paneles usan dos columnas y pasan a una sola hasta 1000px. Las acciones van en 4, 2 o 1 columnas según el ancho (1000px y 560px).
- **El radar** es cuadrado. Su alto no pasa de min(920px, alto de pantalla − 150px), salvo en el celular, donde ocupa todo el ancho y muestra solo las 5 etiquetas principales.
- **Ritmo:** pasos de 6, 8, 12, 16, 18, 22 y 28px. Los cortes son 1240, 1180, 1000, 860, 760, 640 y 560px.

## Elevation & Depth

Es un sistema plano con una sola capa elevada. Las tarjetas flotan apenas sobre el fondo azulado con una sombra doble muy suave. Dentro de ellas no hay más sombras: la jerarquía viene de las líneas de 1px y de los fondos planos. Solo dos elementos se separan de verdad: el globo de ayuda y la ficha, que se abre sobre un velo azul noche desenfocado.

### Shadow Vocabulary
- **Tarjeta** (`box-shadow: 0 1px 2px rgba(20,33,61,.05), 0 8px 24px rgba(20,33,61,.07)`): todas las tarjetas del tablero y las secciones.
- **Globo** (`box-shadow: 0 8px 28px rgba(13,41,96,.25)`): ayuda flotante del radar.
- **Ficha** (`box-shadow: 0 30px 80px rgba(13,41,96,.30)`): diálogo de detalle, con velo `rgba(13,41,96,.40)` y desenfoque de 6px.
- **Píldora del radar** (`filter: drop-shadow(0 1px 1.5px rgba(20,33,61,.12))`): etiquetas dentro del SVG, para que se lean sobre las bandas.

### Named Rules
**La regla de una sola tarjeta.** Dentro de una tarjeta no se pone otra tarjeta con borde y sombra. Se separa con una línea (linea-2) o con un fondo plano.

## Shapes

Las formas son redondeadas y amables, sin llegar a lo infantil.
- Los controles interactivos sueltos son píldoras: chips, segmentos, botones, enlaces de navegación, estado y botones de ícono circulares.
- Las superficies grandes usan radios medios: 16px las tarjetas y 22px la ficha.
- Lo que está dentro de una tarjeta usa radios chicos: 12px los paneles, 10px los campos y filas, 8px los botones de lista y 5px la marca de lugar.
- Las acciones se marcan con un cuadrado de 12px y radio de 3px. Las mitades del radar, con círculos.
- Los puntos del radar llevan un anillo blanco de 2px que los separa de la banda.

## Components

### Buttons
- **Shape:** píldora (999px) con borde de 1px en linea y fondo blanco.
- **Primario de texto:** «Ver más» y equivalentes. Llevan texto en tinta y 600 de peso, con 40px de alto mínimo.
- **Hover / Focus:** el borde pasa a borde-hover y el fondo, a fondo. El foco es un contorno naranja de 2px separado 2px.
- **Botón de ícono:** círculo de 40px, usado en la cabecera de la ficha (copiar enlace, cerrar). Al copiar, el borde y el ícono pasan a verde (bien).
- **Botón de texto:** azul, peso 700, sin fondo. Se subraya al pasar el mouse. Se usa para «Quitar filtros».

### Chips
- **Style:** píldora blanca con borde linea, 34px de alto mínimo y conteo en apagado.
- **State:** activo en azul con texto blanco. Si el chip es de una familia de sociedad y negocio, activo en naranja con texto azul tinta. Si deja sin resultados, baja a opacidad 0.4 y no responde.
- **Segmentos:** la misma píldora a 36px, para elegir una opción dentro de una sección.

### Cards / Containers
- **Corner Style:** 16px.
- **Background:** blanco sobre el fondo azulado.
- **Shadow Strategy:** la sombra de tarjeta (ver Elevation & Depth).
- **Border:** 1px en linea.
- **Internal Padding:** 16px en tarjetas laterales y 20px en secciones (16 × 14 en el celular).

### Inputs / Fields
- **Selector «¿Qué estudias?»:** es el único campo con borde azul de 1.5px y flecha propia, porque es el primer filtro y el más importante. Lleva radio de 10px y peso 600.
- **Buscador:** relleno de fondo, borde linea y lupa a la izquierda. **Focus:** blanco, borde azul y halo azul de 3px al 14 %.

### Navigation
La barra superior es azul a todo el ancho. Lleva la marca (radar bicolor de 42px y nombre en Montserrat 800) y una frase de qué es. La navegación son enlaces blancos en píldora con hover blanco al 12 %. A la derecha, la luz de estado indica si los datos están frescos: verde, ámbar o rojo. En el celular, la navegación pasa a una segunda fila, cambia «Radar» por «Método» y la luz de estado se ajusta a dos líneas.

### Radar (componente firma)
- **Estructura:** un SVG cuadrado con banda segmentada en cuatro arcos, separados por cortes blancos:
  - izquierda en naranja, con texto azul tinta;
  - derecha en azul, con texto blanco;
  - arriba y abajo en azul noche, para el eje de impacto.
- **Anillos:** marcan los años hasta la adopción.
- **Puntos:** naranja o azul dato, con un tamaño que sigue al impulso.
- **Etiquetas:** píldoras blancas con línea guía cuando no caben junto al punto.
- **Estados:** al pasar el mouse o el foco por una fila enlazada, se enciende un anillo alrededor del punto. Al filtrar, lo que queda fuera baja a opacidad 0.12 y pierde su etiqueta.
- **Al cargar:** una aguja barre el radar una vez en 1.5 s.
- **Bucles:** el latido de las tendencias calientes y el pulso de «hoy» corren solo con `prefers-reduced-motion: no-preference`.

### Ficha (modo enfoque)
- **Forma:** diálogo nativo de hasta 920px con radio de 22px. Abre en 0.34 s con un fundido y una subida de 14px.
- **Cabecera:** fija, blanca translúcida.
- **Contenido, en orden:**
  - caja de acción sugerida en azul suave;
  - tres KPI en paneles planos;
  - fila de indicadores separada por líneas;
  - párrafos de lectura;
  - tres gráficos en paneles planos.

## Do's and Don'ts

### Do:
- **Do** usar el naranja solo para sociedad y negocio, para el foco y para los acentos de íconos, y el azul para tecnología y estructura (la regla de las dos mitades).
- **Do** escribir sobre naranja con sobre-naranja (#0A1F47) y escribir en naranja sobre blanco con naranja-texto (#B84A00).
- **Do** mostrar las acciones con la escala de un solo tono azul (#0D2960, #1D428A, #5A79B8 y #93A8D4) y su regla escrita al lado.
- **Do** dejar que los fundidos y los movimientos que responden a un clic corran para todos, y reservar `prefers-reduced-motion: no-preference` solo para los bucles y el desplazamiento suave.
- **Do** dar a cada control táctil al menos 32px de alto (34px a los chips, 40px a los botones) y un foco naranja de 2px.

### Don't:
- **Don't** poner logo, nombre ni escudo de la UCSUR: es un proyecto estudiantil firmado «Proyecto estudiantil · Juan Prado».
- **Don't** poner texto blanco sobre el naranja #F56200.
- **Don't** pintar texto con los colores de tipo de señal o de acción: van en el punto, la barra o el cuadro.
- **Don't** anidar tarjetas con borde y sombra dentro de otra tarjeta.
- **Don't** agregar sombras fuera del vocabulario de cuatro (tarjeta, globo, ficha y píldora del radar).
