# Ideas 2 y 3: momentum escalado por volatilidad e interruptor a refugios

Paralelo al modelo principal, que no se toca. Mismo método y mismo criterio que P1
(`PARALELO_ETF.md`). Reglas escritas **antes** de correr.

Investigación y aprendizaje, no asesoría de inversión.

---

## 1. Reglas (pre-registro, 2026-11-14)

### I2 · Momentum escalado por su propia volatilidad

- **Diagnóstico:** las 10 acciones pasaron de beta 1.2 y volatilidad 25% (2007–2019) a beta 1.6
  y volatilidad 42% (2020–2026), y pierden fuerte en rebotes después de una caída.
- **Regla:** en cada rebalanceo mensual con acciones (alcista o mixto), se calcula la volatilidad
  realizada de la parte en acciones en los **últimos 126 días hábiles** (Barroso y Santa-Clara,
  2015), solo con información anterior a la fecha de operación. El peso en acciones se multiplica
  por `escala = min(1, objetivo / volatilidad realizada)`, donde `objetivo` = **la mediana
  histórica** de esa misma volatilidad hasta esa fecha (sin ver el futuro). Lo que se quita va a
  **SPY**, no a bonos: se baja el riesgo de momentum sin salir de la bolsa.
- **Sin apalancamiento:** la escala nunca pasa de 1, así que ninguna acción supera su 6% o 3%.
- **Lógica:** el riesgo del momentum es predecible y sus caídas llegan cuando su propia
  volatilidad está alta (Barroso y Santa-Clara, 2015; Daniel y Moskowitz, 2016). Escalarlo mejora
  el rendimiento ajustado por riesgo y, al no apalancar, lo que se espera es menos pérdida en los
  "momentum crashes".
- **Parámetros:** 126 días y la mediana histórica como objetivo vienen del artículo y de no
  querer escoger un número. **No se prueban otros valores.**

### I3 · El interruptor sale a los refugios de P1

- **Diagnóstico:** los días con el interruptor encendido restan 0.8 puntos al año; el refugio es
  siempre SHY.
- **Regla:** cuando el interruptor de volatilidad saca las acciones, lo que hoy va a SHY va a la
  canasta de P1 del último fin de mes (los 3 mejores por 13612 de SHY, IEF, TLT, TIP, GLD, LQD,
  BWX y UUP que superen a SHY; lo vacío, a SHY).
- **Lógica:** la misma de P1: en un pánico, Tesoros largos, dólar u oro suelen subir mientras SHY
  solo conserva. **No agrega parámetros.**

### Combinaciones que también se reportan

- **P1 + I3:** el refugio ampliado en caída y en el interruptor.
- **P1 + I2 + I3:** las tres juntas.

### Criterio de decisión (el mismo de P1)

1. Sube el exceso contra el KN Core en **2007-03 a 2019 y en 2020 a 2026-11-06**;
2. la caída máxima no empeora más de 2 puntos;
3. sigue arriba del modelo principal con costos de estrés.

---

## 2. Resultados, 2007-03-01 a 2026-11-06 (réplica validada contra el motor)

Corrido con `ideas_2_3.py`, la misma reconstrucción de `paralelo.py`: la réplica del principal da
lo mismo que el motor (+3.01 contra +3.00).

### Costos base (1 + 5 pb)

| Variante | CAGR | Alfa | Exceso 2007-03 a 2019 | Exceso 2020 a 2026 | Caída máxima | Volatilidad |
| --- | --- | --- | --- | --- | --- | --- |
| Motor KaxaNuk (oficial) | 13.46% | +3.00 | +3.55 | +2.29 | −30.9% | 20.7% |
| Réplica del principal | 13.46% | +3.01 | +3.55 | +2.29 | −30.9% | 20.7% |
| P1 refugio ampliado | 13.55% | **+3.10** | +3.63 | +2.42 | −30.2% | 20.8% |
| I2 momentum escalado | 13.21% | +2.76 | +3.36 | +1.91 | **−28.9%** | **18.5%** |
| I3 interruptor a refugios | 13.30% | +2.84 | +3.52 | +1.86 | −30.9% | 21.0% |
| P1 + I3 | 13.39% | +2.94 | +3.60 | +1.99 | −30.2% | 21.0% |
| P1 + I2 + I3 | 13.15% | +2.69 | +3.41 | +1.61 | −28.3% | 18.8% |

### Costos de estrés (5 + 10 pb)

| Variante | CAGR | Alfa | Exceso 2007-03 a 2019 | Exceso 2020 a 2026 | Caída máxima |
| --- | --- | --- | --- | --- | --- |
| Motor KaxaNuk (oficial) | 12.68% | +2.23 | +2.73 | +1.51 | −31.6% |
| P1 refugio ampliado | 12.79% | **+2.34** | +2.84 | +1.63 | −31.0% |
| I2 momentum escalado | 12.50% | +2.05 | +2.57 | +1.26 | −29.6% |
| I3 interruptor a refugios | 12.53% | +2.08 | +2.73 | +1.05 | −31.5% |
| P1 + I3 | 12.63% | +2.18 | +2.83 | +1.17 | −31.0% |
| P1 + I2 + I3 | 12.43% | +1.98 | +2.65 | +0.92 | −29.4% |

## 3. Veredicto con el criterio pre-registrado

| Variante | Sube el exceso en los dos periodos | Caída máx. no empeora > 2 pts | Arriba del principal en estrés | ¿Se recomienda? |
| --- | --- | --- | --- | --- |
| I2 | No (−0.19 y −0.38) | Sí (mejora 2.0) | No | **No** |
| I3 | No (−0.03 y −0.43) | Sí (igual) | No | **No** |
| P1 + I3 | No (2020–2026 baja) | Sí | No | No |
| P1 + I2 + I3 | No | Sí | No | No |

**P1 sigue siendo la única que sube el alfa.** I2 e I3 se descartan para alfa y se documentan.

**Por qué fallaron:**

- **I2 baja el riesgo, no sube el alfa.** Recorta las acciones en 56% de los rebalanceos (a 73% de
  su peso en promedio), baja la volatilidad de 20.7% a 18.5% y la caída máxima en 2 puntos. Su
  rendimiento por unidad de volatilidad mejora (0.71 contra 0.65), pero el reto mide alfa como
  diferencia de CAGR, y en 2020–2026 las acciones más volátiles fueron también las que más
  subieron. Queda como **opción de perfil conservador**, no como mejora de alfa.
- **I3 llega tarde.** El interruptor se enciende cuando el pánico ya está en su punto más alto; para
  entonces los refugios ya subieron y bajan cuando la bolsa rebota. En 4 de 6 episodios la canasta
  rindió menos que SHY (2008-09: −0.7% contra +0.3%; 2009-01: −1.8% contra −0.2%; 2009-04: −1.5%
  contra −0.2%; 2020: −0.6% contra +0.7%). Solo ganó en 2011 y 2025.

**Corrección al diagnóstico de la sección 1:** el script final `diagnostico_alfa.py` separa mejor
los días del interruptor que el cálculo rápido usado para escribir estas reglas. El interruptor
resta **1.4** puntos al año (no 0.8) y el régimen mixto suma **1.1** (no 0.5). Las reglas y el
veredicto no cambian.

## 4. Registro de intentos (para la lámina de método)

| # | Variante | Fecha | Resultado |
| --- | --- | --- | --- |
| 1 | P1 refugio ampliado | 2026-11-14 | **Pasa** (+0.10 alfa) |
| 2 | P2 núcleo dinámico en mixto | 2026-11-14 | Descartada (−0.98 alfa, −3.6 pts de caída) |
| 3 | P3 = P1 + P2 | 2026-11-14 | Descartada |
| 4 | P4 = P3 + SLV/USO/DBA/UUP | 2026-11-14 | Descartada (inconsistente entre periodos) |
| 5 | I2 momentum escalado por volatilidad | 2026-11-14 | Descartada para alfa; opción de menor riesgo |
| 6 | I3 interruptor a refugios | 2026-11-14 | Descartada |
| 7 | P1 + I3 | 2026-11-14 | Descartada |
| 8 | P1 + I2 + I3 | 2026-11-14 | Descartada |

Ocho variantes probadas, una pasa por poco. Con ese número de intentos, +0.10 puntos puede ser
ruido (Bailey y López de Prado, 2014): por eso P1 debe confirmarse en el motor oficial antes de
presentarse como mejora.
