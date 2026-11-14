# Pitch · Los LITpsteins

Talavera Valley Hackathon 2026 · Track 04 WealthTech · *Alfa a la vista*. Duración: **5 minutos**,
11 láminas.

- **Modelo:** v3, "Momentum concentrado" (`modelo_principal_v3/MODELO_PRINCIPAL.md`).
- **Presentación:** el código de las láminas está en `presentacion/project/`, con estilo Dark Quant.
  Las gráficas usan las series del backtest oficial (`modelo_principal_v3/backtests/backtest_2007_base`).
- **La lámina de método** es la 10.

## Guion

| Tiempo | Lámina | Qué decir |
| --- | --- | --- |
| 0:00–0:15 | 1 · Portada | Hola, somos Los LITpsteins. Inversión activa que genere alfa, de forma transparente, para un mejor retiro. Les quiero contar la historia de Miguel y Ana. |
| 0:15–0:40 | 2 · Miguel y Ana | Miguel, 60 años, se jubila con la Ley 73: le paga el gobierno. Ana, 22 años, primer empleo: su pensión depende de lo que ahorre y de lo que rinda durante 43 años. Hacia 2030 se aportará el 15% de su salario a su retiro, y hoy no es fácil saber si ese dinero le está rindiendo bien. |
| 0:40–1:05 | 3 · Lo que le falta | La CONSAR proyecta 4% real para Ana; su Siefore tiene ~22% en acciones; los planes de empresa rinden 2% real. Un peso a 4% real en 43 años se vuelve 5.4; sumando los 4.8 puntos de alfa con estrés de los años fuera de muestra, ~37 (ilustrativo, no promesa). |
| 1:05–1:40 | 4 · El producto | Ahorro voluntario en dólares que complementa a su Afore. Tres reglas mensuales: las 3 acciones con más impulso (máximo 20% cada una), un núcleo que rota hacia los 2 sectores cíclicos más fuertes y un freno de emergencia confirmado por un modelo de riesgo. Perfiles: dinámico (17.8% anual, caída −34.0%) y moderado (10.3% anual, caída −18.2%). |
| 1:40–2:10 | 5 · Alfa a la vista | Cada mes, Ana sabe cuánto le ganó al benchmark, con cuánto riesgo y por qué. Ejemplo con datos reales: octubre de 2026, +0.7 puntos contra el índice; en el año, +35.4 puntos; y aun así le decimos que está 27.3% abajo del máximo de junio. Attribution Analysis de KaxaNuk: el alfa viene de la selección de acciones y del factor momentum, no de tomar más mercado. |
| 2:10–2:40 | 6 · Resultados | Backtest Engine del Investment Lab, de 2007 a hoy: 17.8% anual contra 10.5% del KN US Equity Core. Son 7.4 puntos de alfa (6.2 con costos de estrés), Sharpe 0.68 contra 0.52 y caída de −34% contra −53%. De 2010 en adelante, fuera de muestra, +4.8 con estrés. $100,000 → $2.83 M (KN: $0.76 M). |
| 2:40–3:05 | 7 · ¿Por qué nosotros? | Solo su Afore: 4% real proyectado. El SPY por su cuenta: 10.4% anual, caída −55.2%. Nosotros: 17.8% anual, caída −34.0%, Sharpe 0.68 y un reporte mensual. |
| 3:05–3:30 | 8 · El riesgo | De cada $100, en el peor momento le quedaron $66; al índice, $47. La peor caída fue en 2025 (aranceles) y se recuperó en seis meses. Habrá años en que pierda contra el índice; el mayor riesgo de Ana es vender en pánico. |
| 3:30–4:00 | 9 · La empresa | Paga la empresa, como prestación (B2B2C): ~0.5% anual sobre lo invertido. La empresa retiene talento y Ana ve cada mes qué hace su dinero. Registro ante la CNBV, o alianza con una casa de bolsa. |
| 4:00–4:35 | 10 · Método | Lógica antes que datos; criterio fijado antes; datos no usados para diseñar (modelo de riesgo 2010–26; regla de acciones 2007–14: +3.9 puntos); sin sesgo de supervivencia; robustez (6 de 7 variantes); Investment Lab (Data Curator, Backtest Engine y Attribution Analysis). |
| 4:35–5:00 | 11 · Cierre | Miguel tiene al gobierno. Ana puede tener una estrategia que trabaje por ella, con el alfa y el riesgo a la vista. Gracias. |

## Lámina de método (texto completo)

1. **Lógica antes que datos.** Momentum, tendencia, canario de tasas y volatilidad, con literatura
   publicada, escritos antes de cada backtest.
2. **Criterio fijado antes de correr.** Cada variante tuvo su regla de aceptación por escrito; las
   que no la cumplieron se descartaron y quedaron documentadas.
3. **Datos que no se usaron para diseñar.** El modelo de riesgo se entrenó con 2000–2009 y quitó 30%
   de las falsas alarmas en 2010–2026. La regla de acciones le ganó al KN por +3.9 puntos al año en
   2007–2014, periodo que su diseño no usó.
4. **Sin sesgo de supervivencia.** El universo es el KN Core de cada fecha. Con una lista de
   "ganadoras" elegida hoy, una estrategia pasó de 35% a 7% anual al corregirlo.
5. **Robustez.** 6 de 7 variantes de parámetros superan al modelo previo, y los parámetros elegidos
   no son los que más rinden. Los sectores los define Morningstar.
6. **Investment Lab y costos reales.** Data Curator, Backtest Engine y Attribution Analysis de
   KaxaNuk; costos de estrés (5 + 10 pb), ejecución al día siguiente y resultados reproducibles con md5.

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
| 30% menos falsas alarmas | `filtro_riesgo/resumen.json` |
| De 35% a 7% anual | Prueba de la estrategia V1 con universo sin sesgo |
| Cuota ~0.5% y canal B2B2C | Borrador del modelo de negocio (`hackathon_progreso.md`) |
