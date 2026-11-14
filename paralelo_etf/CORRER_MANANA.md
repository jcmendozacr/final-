# Correr P1 en el Backtest Engine oficial

Objetivo: comprobar en el motor de KaxaNuk si **P1 (refugio ampliado)** sube el alfa del modelo
principal (+3.00% contra el KN US Equity Core). El modelo principal no se toca.

## Qué cambia (el único cambio que mejoró el alfa)

Solo los **19 meses en régimen de caída**. Hoy el modelo pone 100% en IEF o SHY; P1 pone un
tercio en cada uno de los **3 mejores refugios** por momentum 13612, entre SHY, IEF, TLT, TIP,
GLD, LQD, BWX y UUP, siempre que le ganen a SHY (si no, ese tercio va a SHY). Acciones, régimen
alcista, régimen mixto e interruptor: **iguales**. Detalle y resultados: `PARALELO_ETF.md`.

| Costos | Principal (motor) | P1 (réplica) | Esperado en el motor |
| --- | --- | --- | --- |
| Base 1 + 5 pb | +3.00% | +3.10% | ~+3.1% |
| Estrés 5 + 10 pb | +2.23% | +2.34% | ~+2.3% |

## Lo que necesitas en la laptop

1. **La carpeta del proyecto**, donde están `preparar_motor.py`, `correr_backtest.py`, el `.venv` y
   `datos_backtest_m2/precios/`.
2. **Esta carpeta `paralelo_etf/` copiada dentro**, al lado de `resultados_regimen_n10_a60/`. Con
   git: `git pull`. Sin git: cópiala completa.
3. **La carpeta `<KN>`** con los CSV de `KN_US_Equity_Core.zip` y `KN_US_Equity_Factor_Model.zip`,
   sueltos y sin subcarpetas.
4. **La licencia** del Backtest Engine.

## Pasos

Abre una terminal **en la carpeta del proyecto**.

**PowerShell:**
```powershell
$env:KNBE_API_KEY_KAXANUK = "<LICENCIA>"
.venv\Scripts\python paralelo_etf\correr_kit.py "<KN>"
```

**cmd:**
```bat
set KNBE_API_KEY_KAXANUK=<LICENCIA>
.venv\Scripts\python paralelo_etf\correr_kit.py "<KN>"
```

**Mac/Linux:**
```bash
KNBE_API_KEY_KAXANUK=<LICENCIA> .venv/bin/python paralelo_etf/correr_kit.py <KN>
```

El script primero revisa que esté todo. Si falta algo, lo dice y no corre nada. Luego hace 4 pasos
(tarda como el backtest del principal, dos veces):

1. Copia `datos_backtest_m2/precios` a `datos_backtest_p1/precios` y baja con el Data Curator los
   ETFs nuevos (TLT, TIP, GLD, LQD, BWX, UUP). El original no se toca.
2. Arma la carpeta del motor en `datos_backtest_p1/motor` con `preparar_motor.py`.
3. Corre el motor con costos base → `paralelo_etf/resultados_P1/backtest_base/`.
4. Corre el motor con costos de estrés → `paralelo_etf/resultados_P1/backtest_estres/`.

Al final imprime la comparación contra el principal y el veredicto:
`P1 MEJORA al principal en el motor oficial` o `P1 NO mejora: el principal se queda`.

La comparación incluye el exceso por periodo (2007–2019 y 2020–2026) con la serie diaria del
motor, y revisa las tres condiciones del criterio. Solo para volver a imprimir la tabla: `--comparar`.

## Si algo falla

| Mensaje | Qué hacer |
| --- | --- |
| `Falta ... datos_backtest_m2/precios` | Regenerarla: `MODELO_ACTUAL.md`, sección 9 (`descargar_precios.py` con `resultados_regimen_n10_a60/tickers_para_curator.csv`) |
| `El Backtest Engine no está instalado` | Usar el Python del `.venv` del proyecto, no el del sistema |
| `escritos 5 de 6; sin precios: ...` en el paso 1 | Volver a correr: el Curator solo baja lo que falta |
| `La corrida falló: ... cash` | Igual que con el principal: la reserva de 2% ya está puesta; avisar con el `motor.log` |

## Diagnóstico de P1 (opcional)

Para ver de dónde sale y dónde se pierde el alfa de P1 en el motor:
```
.venv\Scripts\python paralelo_etf\diagnostico_alfa.py paralelo_etf\resultados_P1\backtest_base
```
Escribe `paralelo_etf/diagnosticos/resultados_P1__backtest_base/DIAGNOSTICO.md`. El del principal ya
está en `paralelo_etf/diagnosticos/resultados_regimen_n10_a60__backtest_base_r2/`.

## Después de P1: idea 1 (permanencia en las acciones)

Ver `IDEA_1.md`. Necesita los datos KN y tarda más, porque cambia las acciones:
```powershell
.venv\Scripts\python paralelo_etf\variantes_kn.py "<KN>"
.venv\Scripts\python paralelo_etf\correr_kit.py "<KN>" paralelo_etf\variantes\I1
.venv\Scripts\python paralelo_etf\correr_kit.py "<KN>" paralelo_etf\variantes\P1_I1
```
`variantes_kn.py` primero reconstruye el principal y se detiene si no sale idéntico al congelado.

## Qué reportar

- La tabla que imprime el script (o los dos `resumen.json`).
- Si el alfa base da **≥ +3.05%** y el de estrés **≥ +2.28%**, P1 mejora y se puede presentar
  como "versión 1.1" en un MD aparte, sin cambiar el congelado.
- Si da menos, se reporta como variante probada y descartada (eso también suma en la lámina de
  método).

## Lo que no hay que hacer

- No probar otros números de refugios (2, 4, 5) ni otras listas hasta "encontrar" más alfa: el
  criterio se fijó antes, y cambiarlo después de ver el resultado es sobreajuste.
- No sobrescribir `resultados_regimen_n10_a60/` ni `datos_backtest_m2/`.
