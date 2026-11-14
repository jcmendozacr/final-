# Lámina de método · Los LITpsteins


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

