# Pitch · Los LITpsteins

Talavera Valley Hackathon 2026 · Track 04 WealthTech. Duración: **5 minutos**, 10 láminas.

- **Presentación:** el código de las láminas está en `presentacion/project/`: un HTML por lámina más
  `deck.css`, con estilo Dark Quant.
- **Datos de las gráficas:** las curvas de capital y de caídas salen del backtest oficial del modelo
  principal (`modelo_principal_c2/backtests/backtest_2007_base`).
- **La lámina de método** es la 9.

## Guion

| Tiempo | Lámina | Qué decir |
| --- | --- | --- |
| 0:00–0:20 | 1 · Portada | Hola, somos Los LITpsteins. Les quiero contar la historia de dos personas: Miguel y Ana. Y por qué lo que el sistema no le garantiza a Ana es nuestra oportunidad de negocio. |
| 0:20–0:50 | 2 · Miguel y Ana | Miguel tiene 60 años y se jubila con la Ley 73: su pensión la paga el gobierno, sin importar lo que hagan los mercados. Ana tiene 22 años y es su primer empleo formal. Para ella no hay garantía: su pensión será lo que ahorre y lo que rinda ese ahorro durante 43 años. Miguel no necesita a una empresa como la nuestra. Ana sí. |
| 0:50–1:25 | 3 · Lo que le falta | La CONSAR proyecta para Ana un 4% real. Su Siefore tiene alrededor de 22% en acciones y los planes de empresa rinden 2% real. A 43 años, cada punto cuenta: un peso ahorrado hoy a 4% real se vuelve 5.4 pesos; con los 3.3 puntos de alfa que obtuvimos con costos de estrés, serían casi 21. Es una ilustración, no una promesa. |
| 1:25–1:50 | 4 · El producto | No le pedimos a Ana que deje su Afore: esa es su base. Le ofrecemos un ahorro voluntario en dólares que la complementa, con una estrategia dinámica. Ella decide qué parte de su ahorro voluntario pone aquí, según su perfil. |
| 1:50–2:25 | 5 · La estrategia | Tres reglas que se revisan cada mes. Uno: las 10 acciones con más impulso de las 300 más grandes del KN US Equity Core, sin pasar de 6% en ninguna. Dos: el resto rota hacia los 2 sectores cíclicos con mejor tendencia. Tres: un freno de emergencia; si el mercado rompe su tendencia y hay estrés, pasamos a bonos, pero solo si nuestro modelo de riesgo confirma la alarma. |
| 2:25–3:00 | 6 · Resultados | En el motor oficial de KaxaNuk, de 2007 a hoy: 14.7% anual contra 10.5% del KN US Equity Core. Son 4.3 puntos de alfa al año, y 3.3 con costos de estrés. De 2010 en adelante, años que el modelo de riesgo nunca vio, sigue ganando con costos de estrés. |
| 3:00–3:35 | 7 · El riesgo | De cada 100 dólares, en el peor momento de la estrategia le quedaron 66; al índice, en su peor momento, le quedaron 47. Habrá años en que pierda contra el índice, y nuestra peor caída fue en el COVID. Para una inversionista de 22 años, el mayor riesgo es vender en pánico. |
| 3:35–4:10 | 8 · La empresa | Paga la empresa, como prestación (B2B2C): alrededor de 0.5% anual sobre lo invertido. La empresa retiene talento y Ana ve cada mes qué hace su dinero. La línea: registro ante la CNBV como asesor en inversiones, o alianza con una casa de bolsa. |
| 4:10–4:45 | 9 · Método | Lógica antes que datos; criterio fijado antes de cada corrida; modelo de riesgo probado en años que nunca vio; sin sesgo de supervivencia (una estrategia pasó de 35% a 7% al corregirlo); universo de sectores definido por una regla externa; costos de estrés, motor oficial y resultados reproducibles. |
| 4:45–5:00 | 10 · Cierre | Miguel tiene al gobierno. Ana puede tener una estrategia que trabaje por ella, con el riesgo a la vista. Gracias. |

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
6. **Costos y motor oficial.** Costos de estrés (5 + 10 pb), ejecución al día siguiente, Backtest
   Engine de KaxaNuk y resultados reproducibles con md5.

## Cifras citadas y su fuente

| Cifra | Fuente |
| --- | --- |
| CAGR 14.74% contra 10.45% del KN Core; alfa +4.28% (+3.33% con estrés); caída −33.8% contra −52.7% | `modelo_principal_c2/MODELO_PRINCIPAL.md`, sección 5.1 |
| Alfa 2010–2026: +1.98% (+1.06% con estrés) | Ídem, sección 5.2 |
| 4% real (CONSAR), ~22% en acciones, 2.0% de los planes de empresa, Ley 73 | Caso del reto (`hackathon_progreso.md`, sección 1) |
| $1 → $5.4 (4%) y $20.9 (7.3%) en 43 años | Cálculo ilustrativo: 1.04^43 y 1.0733^43 |
| 30% menos falsas alarmas | `filtro_riesgo/resumen.json` |
| De 35% a 7% anual | Prueba de la estrategia V1 con universo sin sesgo |
| Cuota ~0.5% y canal B2B2C | Borrador del modelo de negocio (`hackathon_progreso.md`, sección 12) |
