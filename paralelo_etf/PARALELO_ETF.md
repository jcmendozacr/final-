# Paralelo ETF: el modelo principal con un universo de ETFs ampliado

Equipo de Habib · Talavera Valley Hackathon 2026 · Track 04 WealthTech.

> **Esto es un paralelo.** El modelo principal (`MODELO_ACTUAL.md`) no se toca: sus reglas,
> archivos y huellas md5 siguen iguales. Aquí se prueba si unos ETFs de otras clases de activo
> suben su alfa (+3.00% contra el KN US Equity Core en el Backtest Engine).
>
> **Resultado oficial (Backtest Engine, 2026-11-13):** P1 da +3.05% de alfa con costos base y
> +2.25% con costos de estrés, pero **no cumple el criterio**, porque en 2020–2026 su exceso baja.
> **El modelo principal se queda.** Las cifras de la réplica (+3.10%) no son oficiales; ver sección 3.
>
> Investigación y aprendizaje, no asesoría de inversión.

---

## 1. Reglas escritas antes de correr el backtest (pre-registro)

Las acciones, el régimen alcista y el interruptor de volatilidad quedan **iguales** al modelo
principal. Solo cambian las partes en ETFs de los regímenes de **caída** y **mixto**.

### P1 · Refugio ampliado (régimen de caída)

- **Hoy:** 100% en IEF o SHY, el de mayor momentum 13612.
- **P1:** se ordenan por momentum 13612 **SHY, IEF, TLT, TIP, GLD, LQD, BWX y UUP**. Se toman los
  **3 mejores** cuyo 13612 supere al de SHY, con un tercio cada uno; los lugares vacíos van a SHY.
- **Lógica:** cada crisis tiene un refugio distinto: Tesoros largos y dólar en 2008, oro en 2011,
  dólar y efectivo en 2022, cuando los bonos también cayeron. Un refugio fijo (IEF/SHY) acierta en
  unas y falla en otras (Faber, 2007; Antonacci, 2014).

### P2 · Núcleo dinámico (régimen mixto)

- **Hoy:** 70% en SPY + 30% en las 10 acciones.
- **P2:** el 70% de SPY se reparte en los **4 mejores** por 13612 de **SPY, IWM, EFA, EEM, VNQ,
  DBC, GLD, TLT, LQD, HYG y EMB**, con 17.5% cada uno, si su 13612 supera al de SHY; los lugares
  vacíos van a SHY. Las 10 acciones (30%) no cambian.
- **Lógica:** en el régimen mixto, la bolsa de EE. UU. ya muestra una señal de alerta. Rotar hacia
  la clase de activo con tendencia es el momentum entre clases de activo (Moskowitz, Ooi y Pedersen,
  2012; Faber, 2007), con un filtro absoluto contra el efectivo. Ningún ETF pasa del 17.5%.

### P3 · P1 + P2

Las dos al mismo tiempo.

### P4 · P3 con materias primas y divisas sueltas (sensibilidad)

P3 agregando **SLV, USO, DBA y UUP** al universo de P2. Sirve para ver si sumar más tickers
ayuda o solo agrega ruido. USO sufre "contango" (el costo de renovar futuros), así que *a priori*
se espera que no ayude.

### Parámetros fijos, sin optimizar

- 13612 = promedio de los rendimientos totales a 1, 3, 6 y 12 meses, al cierre de fin de mes. Es
  la misma señal del canario y del refugio del modelo principal.
- 3 refugios y 4 ETFs: números redondos tomados de la literatura (GTAA de Faber, top 3–6). **No se
  probaron otros valores.**
- Un ETF solo es elegible si tiene 12 meses de historia al cierre de la señal.
- Misma operación que el modelo principal: se opera el día hábil siguiente, reserva de efectivo de
  2%, costos base de 1 + 5 pb y de estrés de 5 + 10 pb.

### Criterio de decisión (fijado antes de ver resultados)

Una variante **se recomienda** solo si cumple las tres condiciones:

1. sube el exceso contra el KN Core **en los dos periodos**: diseño (2007-03 a 2019) y
   2020 a 2026-11-06;
2. su caída máxima no empeora más de 2 puntos;
3. sigue arriba del modelo principal con costos de estrés.

Si ninguna cumple, se reporta así y el modelo principal se queda como está.

---

## 2. Cómo se corrió

El Backtest Engine de KaxaNuk necesita licencia y los datos KN, que no están en este entorno.
Por eso `paralelo.py` **reconstruye el modelo principal a partir de su corrida oficial en el
motor** (`resultados_regimen_n10_a60/backtest_*_r2`):

1. De los pesos diarios, el valor diario y los costos por ticker del motor se despeja el
   rendimiento diario de las 10 acciones + efectivo.
2. Se vuelve a simular día a día cambiando solo la parte en ETFs. Los costos de las acciones son
   los que cobró el motor; los de los ETFs, 6 pb (base) o 15 pb (estrés) sobre lo operado.
3. **Verificación:** la réplica del modelo principal da los mismos números que el motor (tabla).

Precios: los ETFs nuevos (LQD, HYG, EMB, BWX, UUP, SLV, USO, DBA) se bajaron de Yahoo con
`yfinance` a `paralelo_etf/precios/`. Antes se comprobó que `yfinance` da **exactamente** los
mismos rendimientos que el Data Curator en los 11 ETFs que ya teníamos (diferencia máxima 0).

## 3. Resultado oficial de P1 en el Backtest Engine, 2007-03-01 a 2026-11-06

Corrido con `correr_kit.py` (`resultados_P1/backtest_base` y `resultados_P1/backtest_estres`);
tabla y criterio con `correr_kit.py <KN> --comparar`. **Estas son las cifras que se citan.**

| Costos | Modelo | CAGR | Alfa | Caída máxima | Volatilidad | IR |
| --- | --- | --- | --- | --- | --- | --- |
| Base (1 + 5 pb) | Principal | 13.46% | +3.00% | −30.87% | 20.74% | 0.18 |
| Base (1 + 5 pb) | **P1 refugio ampliado** | **13.50%** | **+3.05%** | **−30.92%** | 20.76% | 0.18 |
| Base (1 + 5 pb) | KN US Equity Core | 10.45% | — | −52.67% | 20.01% | — |
| Estrés (5 + 10 pb) | Principal | 12.68% | +2.23% | −31.57% | 20.76% | 0.15 |
| Estrés (5 + 10 pb) | **P1 refugio ampliado** | **12.70%** | **+2.25%** | **−31.82%** | 20.78% | 0.14 |

Exceso contra el KN Core por periodo (costos base, serie diaria del motor):

| Periodo | Principal | P1 | Diferencia |
| --- | --- | --- | --- |
| 2007-03 a 2019 (diseño) | +3.55% | +3.63% | +0.08 |
| 2020 a 2026-11 | +2.29% | +2.27% | **−0.02** |

La réplica esperaba +3.10% (base) y +2.34% (estrés). En el motor, la mejora se reduce a
+0.04 y +0.02 puntos, y en 2020–2026 desaparece.

## 3b. Exploración con la réplica (`paralelo.py`, no oficial)

Sirvió para elegir qué variante llevar al motor. **No citar estas cifras como resultados.**

### Costos base (1 + 5 pb)

| Variante | CAGR | Alfa | Exceso 2007-03 a 2019 | Exceso 2020 a 2026 | Caída máxima | Volatilidad |
| --- | --- | --- | --- | --- | --- | --- |
| Motor KaxaNuk (oficial) | 13.46% | +3.00 | +3.55 | +2.29 | −30.9% | 20.7% |
| Réplica del principal | 13.46% | +3.01 | +3.55 | +2.29 | −30.9% | 20.7% |
| **P1 refugio ampliado** | **13.55%** | **+3.10** | **+3.63** | **+2.42** | **−30.2%** | 20.8% |
| P2 núcleo dinámico | 12.48% | +2.03 | +2.16 | +2.01 | −27.2% | 19.5% |
| P3 = P1 + P2 | 12.59% | +2.13 | +2.25 | +2.15 | −27.2% | 19.5% |
| P4 = P3 + SLV/USO/DBA/UUP | 12.42% | +1.97 | +1.27 | +3.60 | −29.0% | 20.0% |

### Costos de estrés (5 + 10 pb)

| Variante | CAGR | Alfa | Exceso 2007-03 a 2019 | Exceso 2020 a 2026 | Caída máxima |
| --- | --- | --- | --- | --- | --- |
| Motor KaxaNuk (oficial) | 12.68% | +2.23 | +2.73 | +1.51 | −31.6% |
| Réplica del principal | 12.70% | +2.25 | +2.75 | +1.51 | −31.5% |
| **P1 refugio ampliado** | **12.79%** | **+2.34** | **+2.84** | **+1.63** | **−31.0%** |
| P2 núcleo dinámico | 11.56% | +1.11 | +1.20 | +1.07 | −27.5% |
| P3 = P1 + P2 | 11.68% | +1.23 | +1.31 | +1.21 | −27.5% |
| P4 | 11.50% | +1.05 | +0.32 | +2.61 | −29.2% |

Alfa = CAGR − CAGR del KN US Equity Core, igual que el motor. "Exceso" por periodo = diferencia
de CAGR anualizados dentro del periodo.

## 4. Veredicto con el criterio pre-registrado

| Variante | Fuente | Sube el exceso en los dos periodos | Caída máx. no empeora > 2 pts | Arriba del principal en estrés | ¿Se recomienda? |
| --- | --- | --- | --- | --- | --- |
| **P1** | **Motor oficial** | **No (+0.08 y −0.02)** | Sí (empeora 0.05) | Sí (+0.02) | **No** |
| P2 | Réplica | No | Sí (mejora 3.6) | No | No |
| P3 | Réplica | No | Sí | No | No |
| P4 | Réplica | No (baja en el diseño) | Sí | No | No |

P2–P4 ya fallaban en la réplica, así que no se llevaron al motor.

**Lectura honesta:**

- **P1 no cumple en el motor oficial.** En la réplica parecía mejorar +0.1 puntos; en el motor la
  mejora es de solo +0.04 (base) y +0.02 (estrés), y en 2020–2026 el exceso baja 0.02. Es una
  diferencia dentro del ruido: P1 solo actúa en 19 de 237 meses. La lógica sigue siendo
  razonable (en 2022 cambió "solo SHY" por UUP + oro + TIP), pero no alcanza para cambiar el
  modelo. **Se documenta como variante probada y descartada.**
- La diferencia entre la réplica y el motor muestra por qué la decisión se toma con el motor
  oficial: la réplica cobra los ETFs con costos simplificados y no reproduce la ejecución exacta.
- **Ampliar el núcleo (P2–P4) baja el alfa en ~1 punto**, aunque también baja la caída máxima
  unos 3.6 puntos. En el régimen mixto, la bolsa de EE. UU. siguió pagando más que rotar a otras
  clases de activo. Es una opción de **menos riesgo**, no de más alfa.
- P4 se ve bien en 2020–2026 (+3.60) y mal en el diseño (+1.27). Es justo la inconsistencia que
  el criterio descarta: elegirla sería sobreajuste.
- **Conclusión:** el alfa del modelo viene de las 10 acciones de momentum, no de los ETFs.
  Diversificar con ETFs ayuda a controlar el riesgo, pero no sube el alfa de forma importante.

## 5. Cómo se corrió P1 en el Backtest Engine oficial

Ver `CORRER_MANANA.md`: un solo comando (`correr_kit.py`) baja los ETFs nuevos, arma la carpeta del
motor, corre base y estrés y compara contra el principal. El `weights.csv` de P1 es el congelado
con solo las 19 columnas de caída cambiadas (380 tickers × 259 fechas). Resultado: sección 3.

La variante P1 + I1 (refugio ampliado + permanencia en las acciones, `variantes/P1_I1/`) dio en el
motor un alfa base de **+1.17%**, muy por debajo del principal, y también se descarta. Su corrida de
estrés se interrumpió sin guardar el resumen; no hace falta repetirla.

## 6. Archivos

| Archivo | Qué es |
| --- | --- |
| `paralelo.py` | Réplica del principal y variantes P1–P4 |
| `generar_weights_P1.py` | `weights.csv` de P1 para el motor |
| `correr_kit.py`, `CORRER_MANANA.md` | Corrida de P1 en el motor oficial y comparación |
| `IDEAS_2_3.md`, `ideas_2_3.py`, `resultados_ideas_2_3/` | Ideas 2 (momentum escalado) y 3 (interruptor a refugios): descartadas |
| `IDEA_1.md`, `variantes_kn.py` | Idea 1, permanencia en las acciones: lista para correr con los datos KN |
| `diagnostico_alfa.py`, `diagnosticos/` | De dónde sale y dónde se pierde el alfa, para cualquier corrida del motor |
| `precios/` | Precios de LQD, HYG, EMB, BWX, UUP, SLV, USO, DBA (Yahoo) |
| `resultados/` | Tablas, `resumen.json`, curvas diarias, 13612 mensual y pesos ETF de P4 |
| `resultados_P1/` | `weights.csv` de P1, lista de ETFs nuevos y **corridas oficiales del motor** (`backtest_base`, `backtest_estres`) |
| `variantes/` | `weights.csv` de la réplica, I1 y P1 + I1; corrida del motor de P1 + I1 |

Entorno: Python con `pandas`, `numpy`, `openpyxl` y `yfinance` (solo para bajar precios).
