# Modelo

Equipo de Habib · Talavera Valley Hackathon 2026 · Track 04 WealthTech · KaxaNuk Investment Lab.

Una estrategia en dólares que combina ETFs y acciones para ganarle al **KN US Equity Core** con el
riesgo bajo control.

> Investigación y aprendizaje, no asesoría de inversión. Las cifras vienen de backtests sobre
> precios pasados.

> **Para correr el backtest del modelo principal: [`COMO_CORRER.md`](COMO_CORRER.md).** El repo trae los pesos
> (`modelo_principal_c2/weights.csv`) y los precios listos para el Backtest Engine (`motor/precios/`).

## El modelo principal (v3, congelado el 2026-11-14): "Momentum concentrado"

**La misma estructura de la v2 (régimen de mercado, núcleo de sectores cíclicos y freno de emergencia
confirmado por un modelo de riesgo), con las 3 acciones de momentum más fuerte a 20% cada una.**
Reglas, pruebas contra el sobreajuste, resultados y replicación:
**[`modelo_principal_v3/MODELO_PRINCIPAL.md`](modelo_principal_v3/MODELO_PRINCIPAL.md)**.

| Backtest Engine, 2007-03-01 a 2026-11-06 | Modelo principal v3 | KN US Equity Core |
| --- | --- | --- |
| CAGR | **17.82%** (16.62% con costos de estrés) | 10.45% |
| Alfa vs KN Core | **+7.37%** (+6.17% con estrés) | — |
| Alfa 2010–2026 (fuera de muestra del modelo de riesgo) | +5.97% (+4.78% con estrés) | — |
| Sharpe | 0.68 | 0.52 |
| Caída máxima | **−34.0%** | −52.7% |

Versión previa v2: [`modelo_principal_c2/`](modelo_principal_c2/MODELO_PRINCIPAL.md) (+4.28% de alfa).

## Versión previa (congelada el 2026-11-13; componente de acciones del v2)

**Régimen de mercado con 10 acciones de momentum e interruptor de volatilidad.** Las reglas, los
parámetros, los resultados y los pasos para replicarlo están en **[`MODELO_ACTUAL.md`](MODELO_ACTUAL.md)**.

| Backtest Engine, 2007-03-01 a 2026-11-06 | Modelo principal | KN US Equity Core |
| --- | --- | --- |
| CAGR | **13.46%** (12.68% con costos de estrés) | 10.45% |
| Alfa del motor | **+3.00%** (+2.23% con costos de estrés) | — |
| Alfa ajustado por beta | **+7.1%** | — |
| Caída máxima | **−30.9%** | −52.7% |
| Beta | 0.67 | 1.00 |

Para verificar que es la versión congelada:

```bash
while read h f; do [ "$(md5 -q "$f")" = "$h" ] && echo "OK $f" || echo "FALLA $f"; done < MODELO_PRINCIPAL_CONGELADO.md5
```

Las líneas de los dos zips de KaxaNuk solo dan OK en una carpeta que tenga esos archivos, porque no
están en este repositorio.

## Qué hay aquí

| Archivo o carpeta | Qué es |
| --- | --- |
| `MODELO_ACTUAL.md` | Modelo principal congelado: reglas, parámetros, resultados y replicación |
| `MODELO_PRINCIPAL_CONGELADO.md5` | Huellas md5 de la versión congelada |
| **`modelo_principal_v3/`** | **Modelo principal desde el 2026-11-14 ("Momentum concentrado")**: +7.37% de alfa (+6.17% con estrés), CAGR 17.82%, caída −34.0% |
| `modelo_principal_c2/` | Versión previa v2 ("C2 confirmada"): reglas, resultados, replicación y md5. Alfa vs KN Core +4.28% (+3.33% con estrés), CAGR 14.74%, caída −33.8%, 2007–2026 |
| `MODELO_M2.md` | Modelo M2, de régimen con 20 acciones (anterior) |
| `ESTRATEGIA_NUCLEO_SATELITE.md` | Estrategia C0, núcleo SPY + satélite de momentum, 2000–2026 (primera versión) |
| `modelo_regimen.py` | Señales, regímenes, interruptor y `weights.csv` del modelo principal y de M2 |
| `nucleo_satelite.py` | Selección de acciones por momentum y estrategia C0 |
| `descargar_precios.py` | Descarga de precios con el Data Curator (Yahoo Finance) |
| `preparar_motor.py` | Carpeta de precios del Backtest Engine: Yahoo verificado contra KaxaNuk |
| `correr_backtest.py` | Corre el Backtest Engine (base y estrés) |
| `preparar_atribucion.py`, `correr_atribucion.py` | Attribution Analysis (modelo de factores de KaxaNuk) |
| `resultados_regimen_n10_a60/` | **Modelo principal:** `weights.csv`, `regimenes.csv`, `interruptor.csv` y backtests (`*_r2`) |
| `resultados_regimen_n10_a40/` | Variante con 40% en régimen alcista |
| `resultados_regimen_m2/`, `resultados_regimen_m2_vol/` | M2 y M2 + interruptor |
| `resultados_nucleo_satelite*/` | C0 en 2019–2026, 2001–2026 y 2000–2026 (`RESULTADOS.md`) |
| `datos_etf/precios/` | Precios de SPY, IWM, EFA, EEM, VNQ, DBC, IEF, TLT, TIP, SHY y GLD (Yahoo, vía Data Curator) |
| `estrategia*.py`, `diagnostico.py` | Primeras versiones del equipo (multiactivo, sectores, régimen) |
| `hackathon_progreso.md` | Bitácora del equipo |
| `Reto_WealthTech.pdf`, `Estrategias con Mayor CAGR Histórico.pdf` | Reto y documento de investigación |

## Qué NO está, y cómo reconstruirlo

| Falta | Por qué | Cómo obtenerlo |
| --- | --- | --- |
| `.venv/` | Contiene las librerías con licencia de KaxaNuk; se instalan por máquina | `uv venv --python 3.12 .venv`, luego las instalaciones de `ESTRATEGIA_NUCLEO_SATELITE.md`, 8.1 (las de KaxaNuk con su licencia) |
| `KN_US_Equity_Core.zip`, `KN_US_Equity_Factor_Model.zip` | Datos propietarios de KaxaNuk; uno pesa 624 MB, más que el límite de GitHub | KaxaNuk (Analytics Factory) |
| `datos_backtest*/`, `datos_atribucion*/` | Derivados de los datos de KaxaNuk, ~8 GB | Se regeneran con los pasos de `MODELO_ACTUAL.md`, sección 9 |

## Licencias y claves

Ninguna clave ni licencia está en este repositorio. Los scripts leen las licencias de las variables
de entorno `KNBE_API_KEY_KAXANUK` (Backtest Engine) y `KNAA_API_KEY_KAXANUK` (Attribution
Analysis).
