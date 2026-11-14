# Idea 1: regla de permanencia en las 10 acciones

Paralelo al modelo principal, que no se toca. Mismo método y mismo criterio que P1, I2 e I3.
Reglas escritas **antes** de correr (2026-11-14). Se corre mañana en la laptop, porque necesita
los datos KN.

Investigación y aprendizaje, no asesoría de inversión.

---

## 1. Por qué esta idea (diagnóstico)

`diagnostico_alfa.py` sobre la corrida oficial del principal (costos base):

- Las 10 acciones aportan **+5.2 puntos al año** contra el KN Core: todo el alfa sale de ahí.
- Los costos restan **0.46 puntos al año** con costos base, y el doble con costos de estrés
  (+3.00 → +2.23 de alfa). Casi todos esos costos vienen de rotar acciones cada mes.

Si las ganadoras de momentum siguen ganando unos meses (Jegadeesh y Titman, 1993), vender una
acción solo porque bajó del lugar 10 al 12 paga costos sin cambiar la exposición a la señal.

## 2. Regla (pre-registro)

### I1 · Permanencia (top 10 para entrar, top 20 para salir)

- Cada fin de mes se ordenan las acciones elegibles por momentum 12-1, con el mismo universo y la
  misma señal del principal (top 300 por peso del KN Core, 240 de 252 días).
- **Una acción que ya está en la lista se queda mientras siga en el top 20.**
- Los lugares libres se llenan con las mejores del ranking que no estén en la lista, hasta 10.
- Pesos iguales, como hoy (6% en alcista, 3% en mixto). Régimen, SPY, refugio e interruptor:
  iguales.
- La lista evoluciona cada mes, aunque el régimen sea de caída y no se tengan acciones.
- **Lógica:** una banda de permanencia reduce la rotación de una estrategia de momentum casi sin
  perder la señal (Novy-Marx y Velikov, 2016). 20 = 2 × 10 es la banda estándar; **no se prueban
  otros valores**.

### P1 + I1

La permanencia más el refugio ampliado de P1 en el régimen de caída.

### Criterio de decisión (el mismo)

1. Sube el exceso contra el KN Core en **2007-03 a 2019 y en 2020 a 2026-11-06**;
2. la caída máxima no empeora más de 2 puntos;
3. sigue arriba del modelo principal con costos de estrés.

**Qué se espera *a priori*:** menos costos, sobre todo en estrés. El riesgo es que mantener
acciones en los lugares 11 a 20 diluya la señal y baje el rendimiento bruto. El resultado puede
ir en cualquier dirección.

## 3. Cómo se corre (laptop)

```powershell
$env:KNBE_API_KEY_KAXANUK = "<LICENCIA>"
# 1. Pesos: réplica del principal (debe salir idéntica al congelado), I1 y P1 + I1
.venv\Scripts\python paralelo_etf\variantes_kn.py "<KN>"
# 2. Motor oficial, base y estrés, para cada variante
.venv\Scripts\python paralelo_etf\correr_kit.py "<KN>" paralelo_etf\variantes\I1
.venv\Scripts\python paralelo_etf\correr_kit.py "<KN>" paralelo_etf\variantes\P1_I1
# 3. Diagnóstico (la comparación del paso 2 ya incluye los dos periodos)
.venv\Scripts\python paralelo_etf\diagnostico_alfa.py paralelo_etf\variantes\I1\backtest_base paralelo_etf\variantes\I1\regimenes.csv
```

`variantes_kn.py` se detiene si la réplica no sale idéntica al `weights.csv` congelado: eso
garantiza que I1 solo cambia lo que dice la regla.

## 4. Resultados

*Pendiente: se llena después de correr en el motor.*
