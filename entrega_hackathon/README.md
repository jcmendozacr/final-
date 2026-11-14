# DHAR Capital · Alfa a la vista

Equipo Los LITpsteins.

Talavera Valley Hackathon 2026 · Track 04 WealthTech · Tec de Monterrey, Puebla.

> Un ahorro voluntario en dólares que complementa la Afore de Ana. Invierte en las acciones y los
> sectores con más impulso, se protege con bonos cuando el mercado se pone feo y le explica a Ana,
> cada mes, cuánto le ganó al benchmark, con cuánto riesgo y por qué.

## Resultado principal

Backtest Engine 0.68.0 del Investment Lab de KaxaNuk, del 2007-03-01 al 2026-11-06, $100,000
iniciales, máximo 20% por acción.

| | Modelo (costos base) | Modelo (costos de estrés) | KN US Equity Core | SPY |
| --- | --- | --- | --- | --- |
| Rendimiento anual (CAGR) | **17.82%** | 16.62% | 10.45% | 10.39% |
| **Alfa contra el KN US Equity Core** | **+7.37%** | **+6.17%** | — | — |
| Sharpe | **0.68** | 0.63 | 0.52 | 0.52 |
| Peor caída | **−34.0%** | −35.1% | −52.7% | −55.2% |
| Valor final de $100,000 | $2.83 M | — | $0.76 M | — |

Del 2010 en adelante, años que el modelo de riesgo no usó para entrenarse, el alfa con costos de
estrés es de **+4.78%** al año.

## Los entregables

| # | Entregable que pide el reto | Dónde está |
| --- | --- | --- |
| 01 | El backtest contra su benchmark | [`01_backtest/`](01_backtest/): reglas (`MODELO_PRINCIPAL.md`), pesos (`weights.csv`), las 4 corridas oficiales (2007 y 2010, costos base y de estrés) con el Excel del motor, el perfil moderado y la atribución del alfa |
| 02 | El código, y cómo correrlo | En el repositorio del equipo (ya entregado): ver `COMO_CORRER.md` |
| 03 | El pitch: cliente, estrategia, riesgo y quién paga | [`03_pitch/presentacion.html`](03_pitch/presentacion.html) (13 láminas) el guion con la fuente de cada cifra en [`03_pitch/PITCH.md`](03_pitch/PITCH.md) y el reparto para 3 personas en [`03_pitch/PITCH_3_PERSONAS.md`](03_pitch/PITCH_3_PERSONAS.md) |
| 04 | Una lámina de método: cómo evitaron el sobreajuste | [`04_lamina_metodo/`](04_lamina_metodo/): la lámina y su texto |
| + | Demo (MVP) | [`05_demo/reporte_ana.html`](05_demo/reporte_ana.html): el reporte mensual de Ana con los 237 meses reales del backtest. Fotos de la prueba con un usuario en `05_demo/fotos_prueba_usuario/` |

## Cómo abrir cada cosa

- **Presentación:** abre `03_pitch/presentacion.html` en el navegador. Flechas o clic para avanzar,
  **N** para ver las notas del orador y **Ctrl+P → Guardar como PDF** para tener el PDF.
- **Demo:** abre `05_demo/reporte_ana.html`. Funciona sin servidor: elige perfil, ahorro mensual,
  año de inicio y mes del reporte.
- **Versiones en línea:** [presentación](https://claude.ai/artifact/LZ6zzaCmni2T3jBCxKmT1W) y
  [demo](https://claude.ai/artifact/FAKN1wuQbFLrHEw2MN4H8u).
- **Regenerar los datos de la demo:** `python3 pitch/demo/extraer_datos.py pitch/demo/datos.json`,
  desde la raíz del repositorio del equipo.

## La estrategia en 30 segundos

Cada fin de mes revisa dos alarmas: si el S&P 500 cae debajo de su promedio de 10 meses y si los
bonos contra inflación (TIP) muestran estrés.

| Alarmas | Acciones (las 3 con más impulso) | ETFs de sector (los 2 más fuertes) | Bonos (SHY o IEF) | Meses |
| --- | --- | --- | --- | --- |
| Ninguna | 60% (3 × 20%) | 40% (2 × 20%) | 0% | 62% |
| Una | 30% (3 × 10%) | 70% (2 × 35%) | 0% | 26% |
| Dos, y el modelo de riesgo confirma | 0% | 0% | 100% | 9% |

Si suenan las dos y el modelo de riesgo no confirma (3% de los meses), todo va a los 2 ETFs de
sector. Se opera al día siguiente de la señal. Perfil moderado: la mitad en la estrategia y la mitad
en SHY (10.25% anual, peor caída −18.2%).

## Validación

- Un usuario probó la demo durante el hackathon, le gustó y dijo que sí invertiría con nosotros.
- Arturo (KaxaNuk), mentor: entre más tiempo abarque el backtest, mejor, para ver cómo se comporta
  en los peores y en los mejores momentos. El backtest cubre 19.7 años con 4 crisis.
- Primer cliente: una empresa de Puebla con empleados jóvenes que lo ofrezca como prestación (plan de 30/60/90 días en la lámina 11).

---

Investigación y aprendizaje, no asesoría de inversión. Rendimientos pasados no garantizan
rendimientos futuros.
