# Pitch · Los LITpsteins

Talavera Valley Hackathon 2026 · Track 04 WealthTech · *Alfa a la vista*. Duración: **5 minutos**,
13 láminas.

- **Modelo:** v3, "Momentum concentrado" (`modelo_principal_v3/MODELO_PRINCIPAL.md`).
- **Presentación:** el código de las láminas está en `presentacion/project/`, con estilo Dark Quant.
  Las gráficas usan las series del backtest oficial (`modelo_principal_v3/backtests/backtest_2007_base`).
- **La lámina de método** es la 12.
- **Demo (MVP):** `demo/reporte_ana.html`, publicada como [Reporte de Ana](https://claude.ai/artifact/FAKN1wuQbFLrHEw2MN4H8u).
  Sus datos (`demo/datos.json`) salen del backtest oficial con `demo/extraer_datos.py`.
- **Guion v4 (2026-11-14):** ajustado a la hoja de evaluación. Lámina 4: validación con un usuario
  y un mentor. Láminas 5 y 6: qué compra la estrategia y cuánto según dos alarmas. Lámina 7: demo
  en vivo. Lámina 11: primer cliente y plan de 30/60/90 días. Lámina 12: experimentación. Si el
  tiempo aprieta, la lámina 9 se pasa en 5 segundos.

## Cómo cubre la rúbrica (Hoja de evaluación TV Hack 2026)

| Criterio (peso) | Dónde se cubre | Pendiente |
| --- | --- | --- |
| 1. Problema, usuario y evidencia (20%) | Láminas 2–4: Ana, datos de la CONSAR; un usuario probó la demo y dijo que sí invertiría; comentario de Arturo (KaxaNuk) sobre la ventana del backtest | — (fotos en `fotos/` y en la lámina 4) |
| 2. Solución e innovación (20%) | Láminas 5 y 6: qué compra (acciones, ETFs de sector, bonos) y cuánto según dos alarmas; lámina 7: alfa a la vista | — |
| 3. Uso significativo de la tecnología (20%) | Láminas 5 y 6: el algoritmo decide y explica; Ana no necesita saber de inversiones. Investment Lab de KaxaNuk | — |
| 4. MVP y experimentación (20%) | Lámina 7: demo en vivo ([Reporte de Ana](https://claude.ai/artifact/FAKN1wuQbFLrHEw2MN4H8u), `demo/`). Lámina 12: 40 variantes, 158 corridas, 3 versiones | Ya probada con un usuario |
| 5. Impacto, negocio y continuidad (15%) | Lámina 11: quién paga, cuánto, primer cliente (DHAR Capital) y plan de 30/60/90 días | — |
| 6. Pitch y demo (5%) | Estructura problema → solución → demo → evidencia → negocio, ~5 min | Ensayar con cronómetro |

## Guion (texto para decir en voz alta, ~909 palabras ≈ 5 minutos)

Es el mismo texto de las notas de cada lámina. Lo que va entre paréntesis es una acción, no se dice.

### 1 · Portada (0:00–0:10)
Hola, somos Los LITpsteins. Hacemos inversión activa que le gana al mercado, explicada para que cualquiera la entienda, para un mejor retiro. Les cuento la historia de Miguel y Ana.

### 2 · Miguel y Ana (0:10–0:30)
Miguel tiene 60 años y se jubila con la Ley 73: su pensión la paga el gobierno. Ana tiene 22 y acaba de entrar a su primer trabajo. Su pensión depende de cuánto ahorre y de cuánto le rinda durante 43 años. Hacia 2030 se aportará el 15% de su salario, y hoy no tiene forma fácil de saber si le está rindiendo bien.

### 3 · Lo que le falta (0:30–0:45)
La CONSAR proyecta para Ana un 4% real: cada peso que ahorra hoy se vuelve 5.4. Con casi 5 puntos más al año, ese mismo peso se vuelve unos 37. Es un ejemplo, no una promesa, pero muestra cuánto pesan unos puntos en 43 años.

### 4 · Validación con un usuario y un mentor (0:45–1:05)
No nos quedamos con la teoría. Un usuario probó nuestra demo durante el hackathon, le gustó y nos dijo que sí invertiría con nosotros. Y Arturo, de KaxaNuk, nos dijo que entre más tiempo abarque el backtest, mejor, porque así se ve cómo se comporta en los peores y en los mejores momentos. Por eso lo probamos en casi 20 años, con cuatro crisis adentro.

### 5 · Qué compra: acciones, ETFs de sector y bonos (1:05–1:35)
¿En qué invierte el dinero de Ana? En tres cosas. Uno, acciones: las 3 empresas con más impulso de las 300 más grandes de Estados Unidos, con máximo 20% en cada una; este mes, Moderna, CrowdStrike y Palo Alto. Lo que sube con fuerza suele seguir subiendo un tiempo: se llama momentum. Dos, ETFs de sector: un ETF compra todo un sector de un jalón, como tecnología o energía; tomamos los 2 que más subieron en el año. Tres, bonos del gobierno de Estados Unidos, también en ETF, solo cuando hay tormenta. En promedio: 45% acciones, 45% sectores y 10% bonos.

### 6 · Cuánto en cada cosa: un modelo dinámico con dos alarmas (1:35–2:05)
No son reglas fijas: es un modelo dinámico que se adapta cada mes. ¿Cuánto en cada cosa? Depende de dos alarmas que revisamos cada fin de mes: si el S&P 500 cae debajo de su promedio de 10 meses, y si los bonos contra inflación muestran estrés. Sin alarmas, 60% en las 3 acciones, 20% cada una, y 40% en los 2 sectores: así estuvo el 62% del tiempo. Con una alarma, las acciones bajan a 30% y los sectores suben a 70%. Con las dos, y si nuestro modelo de riesgo lo confirma, todo a bonos. Ana no decide nada; si quiere menos riesgo, el perfil moderado pone siempre la mitad en bonos.

### 7 · Demo en vivo: el backtest, mes a mes (2:05–2:45)
(Abrir la demo.) Este es nuestro MVP: el backtest en vivo, convertido en el reporte que Ana recibe cada mes. Octubre de 2026: le ganó al índice por 0.7 puntos y en el año va 35 arriba; y aun así le decimos que está 27% abajo de su máximo de junio. Aquí ve qué tiene y por qué: sonó una alarma, así que las acciones bajaron a 30%. (Ir a octubre de 2008.) Y en 2008, el freno: el modelo de riesgo confirmó y su dinero se fue a bonos.

### 8 · Resultados y por qué desde 2007 (2:45–3:20)
Lo probamos en el Backtest Engine de KaxaNuk, de 2007 a hoy, con 2008, el COVID, 2022 y los aranceles: 17.8% al año contra 10.5% del índice. Son 7.4 puntos de ventaja, y 6.2 con comisiones más caras de lo normal. La peor caída fue de 34%; la del índice, de 53%. ¿Por qué desde 2007? Una de nuestras alarmas usa un fondo de bonos que existe desde finales de 2003, y las señales necesitan un año de historia: 2007 es el primer año con todo encendido, e incluye 2008 completo. Y con 2000 a 2009 entrenamos el modelo de riesgo; no se califica a un alumno con el examen con el que estudió, por eso mostramos 2010 en adelante aparte: ahí la ventaja sigue en 4.8 puntos al año con costos altos.

### 9 · ¿Por qué nosotros? (3:20–3:25)
Comparado con sus otras opciones, Ana gana más con menos caída, y sabe cada mes por qué.

### 10 · El riesgo (3:25–3:40)
De cada 100 dólares, en el peor momento le quedaron 66; al índice, 47. Esa caída fue con los aranceles de 2025 y se recuperó en seis meses. Habrá años en que perdamos contra el índice. El mayor riesgo de Ana no es el algoritmo: es vender por miedo.

### 11 · Modelo de negocio y siguientes pasos (3:40–4:10)
¿Quién paga? La empresa de Ana, como prestación: retiene talento y Ana ahorra vía nómina. ¿Cuánto? Cerca de 0.5% al año sobre lo invertido: mil empleados ahorrando 100 dólares al mes son 1.2 millones el primer año y la cuota crece con cada aportación. Nuestro primer cliente: DHAR Capital. En 30 días, piloto con su equipo; en 60, alianza con una casa de bolsa registrada ante la CNBV; en 90, dos empresas más y la conversación con inversionistas.

### 12 · Por qué no hay sobreajuste ni sesgo (4:10–4:45)
¿Cómo sabemos que no es suerte? Probamos 40 variantes en 158 corridas, y cada una tuvo su criterio escrito antes de correrla. Sobreajustar es memorizar las respuestas de un examen viejo; para evitarlo, lo examinamos con años que nunca vio: la regla de acciones se diseñó con datos desde 2012 y en 2007 a 2014 le ganó al índice por 3.9 puntos al año. Movimos las perillas: las 7 versiones le ganan al índice y la nuestra no es la que más rinde. Y sin sesgo: usamos las empresas que existían en cada fecha, incluidas las que quebraron, y nunca información del futuro.

### 13 · Cierre (4:45–5:00)
Miguel tiene al gobierno. Ana puede tener una estrategia que trabaje por ella, con el alfa y el riesgo a la vista cada mes. Somos Los LITpsteins. Gracias.

## Lámina de método (texto de apoyo)

1. **Lógica antes que datos.** Momentum, tendencia, canario de tasas y volatilidad, con literatura
   publicada, escritos antes de cada backtest.
2. **Criterio fijado antes de correr.** Cada variante tuvo su regla de aceptación por escrito; las
   que no la cumplieron se descartaron y quedaron documentadas.
3. **Datos que no se usaron para diseñar.** El modelo de riesgo se entrenó con 2000–2009 y quitó 30%
   de las falsas alarmas en 2010–2026. La regla de acciones le ganó al KN por +3.9 puntos al año en
   2007–2014, periodo que su diseño no usó.
4. **Sin sesgo de supervivencia.** El universo es el KN Core de cada fecha; las acciones que dejan
   de cotizar se venden a su último precio. Con una lista de "ganadoras" elegida hoy, una estrategia
   pasó de 35% a 7% anual al corregirlo.
5. **Robustez.** Las 7 variantes de parámetros le ganan al KN Core; 6 de 7 superan al modelo previo,
   y los parámetros elegidos no son los que más rinden. Los sectores los define Morningstar.
6. **Sin información del futuro y con costos reales.** Señal al cierre de fin de mes y operación al
   día siguiente; costos de estrés (5 + 10 pb); Data Curator, Backtest Engine y Attribution Analysis
   de KaxaNuk; resultados reproducibles con md5.

## Cifras citadas y su fuente

| Cifra | Fuente |
| --- | --- |
| CAGR 17.82% contra 10.45%; alfa +7.37% (+6.17% con estrés); Sharpe 0.68 contra 0.52; caída −34.0% contra −52.7%; $2.83 M contra $0.76 M | `modelo_principal_v3/MODELO_PRINCIPAL.md`, sección 3.1 |
| Alfa 2010–2026: +5.97% (+4.78% con estrés) | Ídem, sección 3.2 |
| 2007–2014: 11.5% contra 7.6% del KN; sensibilidad de 6 de 7 | Ídem, secciones 3.3 y 4 |
| SPY: 10.39% anual, caída −55.2%, Sharpe 0.52 | Benchmark SPY en la misma corrida |
| Perfil moderado (50% modelo + 50% SHY): 10.25% anual, caída −18.2%, Sharpe 0.79 | Backtest Engine, 2007–2026, costos base (`perfil_moderado_v3/`) |
| Octubre de 2026: 0.0% contra −0.7% del KN; 2026: +44.1% contra +8.7%; caída de −27.3% desde el 2026-06-22 | Serie diaria del backtest oficial |
| Atribución: selección +1,670%, momentum +1,029%, tecnología +162%, mercado −310% | `modelo_principal_v3/ATRIBUCION.md` |
| 4% real, ~22% en acciones, 2.0% de los planes de empresa, Ley 73, 15% del salario hacia 2030 | Documento del reto |
| $1 → $5.4 (4%) y $37.3 (≈8.8%) en 43 años | Ilustrativo: 1.04^43 y 1.0878^43 (4% + 4.78 puntos) |
| TIP cotiza desde el 2003-12-05; primera señal 2006-01-31; backtest desde 2007-03-01 | `MODELO_M2.md`, secciones 6 y 7 |
| Las 7 variantes con alfa positivo (+1.74% a +8.74%) | `modelo_principal_v3/MODELO_PRINCIPAL.md`, sección 4 |
| 40 variantes y 158 corridas del Backtest Engine | Carpetas con `resumen.json` en el repo (`hackaton_*`, `paralelo_etf`, `resultados_*`, `modelo_principal_*`) |
| Alfa de las 3 versiones: +3.00%, +4.28%, +7.37% | `MODELO_ACTUAL.md`, `modelo_principal_c2/` y `modelo_principal_v3/` |
| Octubre de 2026 en régimen mixto (canario en alerta): MU, MRNA y DELL a 10%, XLK y XLE a 35% | `modelo_principal_v3/weights.csv` (2026-10-01) y `resultados_regimen_m2/regimenes.csv` |
| Meses por escenario: 62% sin alarmas, 26% una alarma, 9% bonos, 3% solo sectores; promedio 45.3% acciones, 45.3% ETFs de sector y 9.4% bonos (SHY 6.0%, IEF 3.4%), redondeado a 45/45/10 | `demo/datos.json` (carteras de `modelo_principal_v3/weights.csv`) |
| 30% menos falsas alarmas | `filtro_riesgo/resumen.json` |
| De 35% a 7% anual | Prueba de la estrategia V1 con universo sin sesgo |
| Usuario que probó la demo; comentario de Arturo (KaxaNuk); DHAR Capital como primer cliente | Información del equipo, 14 de noviembre de 2026 |
| Cuota ~0.5% y canal B2B2C | Borrador del modelo de negocio (`hackathon_progreso.md`) |
