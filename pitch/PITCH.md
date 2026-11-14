# Pitch · Los LITpsteins

Talavera Valley Hackathon 2026 · Track 04 WealthTech · *Alfa a la vista*. Duración: **5 minutos**,
11 láminas.

- **Presentación:** el código de las láminas está en `presentacion/project/`: un HTML por lámina más
  `deck.css`, con estilo Dark Quant.
- **Datos de las gráficas:** las curvas de capital y de caídas salen del backtest oficial del modelo
  principal (`modelo_principal_c2/backtests/backtest_2007_base`).
- **La lámina de método** es la 10.

## Guion

| Tiempo | Lámina | Qué decir |
| --- | --- | --- |
| 0:00–0:15 | 1 · Portada | Hola, somos Los LITpsteins. Inversión activa que genere alfa, de forma transparente, para un mejor retiro. Les quiero contar la historia de Miguel y Ana. |
| 0:15–0:40 | 2 · Miguel y Ana | Miguel, 60 años, se jubila con la Ley 73: le paga el gobierno. Ana, 22 años, primer empleo: su pensión depende de lo que ahorre y de lo que rinda ese ahorro durante 43 años. Hacia 2030 se aportará el 15% de su salario a su retiro, y hoy no es fácil saber si ese dinero le está rindiendo bien. |
| 0:40–1:05 | 3 · Lo que le falta | La CONSAR proyecta 4% real para Ana; su Siefore tiene ~22% en acciones; los planes de empresa rinden 2% real. Un peso a 4% real en 43 años se vuelve 5.4; con +3.3 puntos de alfa, casi 21 (ilustrativo, no promesa). |
| 1:05–1:40 | 4 · El producto | Ahorro voluntario en dólares que complementa a su Afore. Tres reglas mensuales: las 10 acciones con más impulso (máximo 6% cada una), un núcleo que rota hacia los 2 sectores cíclicos más fuertes y un freno de emergencia confirmado por un modelo de riesgo. Dos perfiles: dinámico (14.7% anual, caída −33.8%) y moderado (8.6% anual, caída −16.5%). |
| 1:40–2:10 | 5 · Alfa a la vista | Nuestro diferenciador: cada mes, Ana sabe cuánto le ganó al benchmark, con cuánto riesgo y por qué. Ejemplo con datos reales: en octubre de 2026 perdimos 2.1 puntos contra el índice, y se lo decimos; en el año vamos 20 puntos arriba; estamos 23.5% abajo del máximo de junio. Y de dónde vino el alfa: Attribution Analysis de KaxaNuk muestra que viene de la selección de acciones (+799%) y del factor momentum (+620%), no de tomar más mercado (−235%). |
| 2:10–2:40 | 6 · Resultados | Backtest Engine del Investment Lab, de 2007 a hoy: 14.7% anual contra 10.5% del KN US Equity Core. Son 4.3 puntos de alfa (3.3 con costos de estrés). Considerando el riesgo: Sharpe 0.64 contra 0.52, caída −33.8% contra −52.7%. De 2010 en adelante, fuera de muestra, +1.1% con estrés. |
| 2:40–3:05 | 7 · ¿Por qué nosotros? | Solo su Afore: 4% real proyectado. El SPY por su cuenta: 10.4% anual, caída −55.2%, nadie que la acompañe. Nosotros: 14.7% anual, caída −33.8%, Sharpe 0.64 y un reporte mensual que le explica todo. |
| 3:05–3:30 | 8 · El riesgo | De cada $100, en el peor momento le quedaron $66; al índice, $47. Habrá años en que pierda contra el índice, y la peor caída fue en el COVID. El mayor riesgo de Ana es vender en pánico. |
| 3:30–4:00 | 9 · La empresa | Paga la empresa, como prestación (B2B2C): ~0.5% anual sobre lo invertido. La empresa retiene talento y Ana ve cada mes qué hace su dinero. Registro ante la CNBV, o alianza con una casa de bolsa. |
| 4:00–4:35 | 10 · Método | Lógica antes que datos; criterio fijado antes de cada corrida; modelo de riesgo probado en años que nunca vio; sin sesgo de supervivencia (35% → 7% al corregirlo); universo por regla externa; Investment Lab (Data Curator, Backtest Engine y Attribution Analysis), costos de estrés y resultados reproducibles. |
| 4:35–5:00 | 11 · Cierre | Miguel tiene al gobierno. Ana puede tener una estrategia que trabaje por ella, con el alfa y el riesgo a la vista. Gracias. |

## Lámina de método (texto completo)

1. **Lógica antes que datos.** Momentum, tendencia, canario de tasas y volatilidad, con literatura
   publicada, escritos antes de cada backtest.
2. **Criterio fijado antes de correr.** Cada variante tuvo su regla de aceptación por escrito; las
   que no la cumplieron se descartaron y quedaron documentadas.
3. **Datos que el modelo nunca vio.** El modelo de riesgo se entrenó con 2000–2009 y se probó en
   2010–2026: quitó 30% de las falsas alarmas.
4. **Sin sesgo de supervivencia.** El universo es el KN Core de cada fecha. Con una lista de
   "ganadoras" elegida hoy, una estrategia pasó de 35% a 7% anual al corregirlo.
5. **Universo por regla externa.** Una lista de 4 sectores elegida a mano perdía el alfa con los 9;
   usamos la clasificación cíclica de Morningstar.
6. **Investment Lab y costos reales.** Data Curator, Backtest Engine y Attribution Analysis de KaxaNuk; costos de estrés
   (5 + 10 pb), ejecución al día siguiente y resultados reproducibles con md5.

## Cifras citadas y su fuente

| Cifra | Fuente |
| --- | --- |
| CAGR 14.74% contra 10.45% del KN Core; alfa +4.28% (+3.33% con estrés); caída −33.8% contra −52.7%; Sharpe 0.64 contra 0.52 | `modelo_principal_c2/MODELO_PRINCIPAL.md`, sección 5.1 |
| Alfa 2010–2026: +1.98% (+1.06% con estrés) | Ídem, sección 5.2 |
| SPY: 10.39% anual, caída −55.2%, Sharpe 0.52 | Benchmark SPY en la misma corrida del Backtest Engine |
| Perfil moderado (50% estrategia + 50% SHY): 8.61% anual, caída −16.5%, Sharpe 0.76 | Corrida del Backtest Engine, 2007–2026, costos base |
| Reporte de octubre de 2026: −2.8% contra −0.7% del KN; 2026: +28.7% contra +8.7%; caída de −23.5% desde el 2026-06-22 | Serie diaria del backtest oficial, costos base |
| 4% real (CONSAR), ~22% en acciones, 2.0% de los planes de empresa, Ley 73, 15% del salario hacia 2030 | Documento del reto (*Reto_WealthTech.pdf*) |
| $1 → $5.4 (4%) y $20.9 (7.3%) en 43 años | Cálculo ilustrativo: 1.04^43 y 1.0733^43 |
| Atribución del alfa: selección +799%, momentum +620%, energía +209%, mercado −235% (contribución al rendimiento activo acumulado, 2007–2026) | `hackaton_combos/ATRIBUCION_C2.md` (Attribution Analysis de KaxaNuk) |
| 30% menos falsas alarmas | `filtro_riesgo/resumen.json` |
| De 35% a 7% anual | Prueba de la estrategia V1 con universo sin sesgo |
| Cuota ~0.5% y canal B2B2C | Borrador del modelo de negocio (`hackathon_progreso.md`, sección 12) |
