"""Arma la carpeta `entrega_hackathon/` con los entregables del reto.

Uso, desde la raíz del repo:  python3 pitch/construir_entrega.py

1. Regenera el guion de `pitch/PITCH.md` a partir de las notas de cada lámina.
2. Construye una versión de la presentación que se abre sin internet (flechas para avanzar,
   N para notas, imprimir para PDF).
3. Copia el backtest oficial, la lámina de método, la demo y las fotos de la prueba con usuario.
"""
import html
import json
import re
import shutil
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PITCH = RAIZ / "pitch"
DECK = PITCH / "presentacion" / "project"
SALIDA = RAIZ / "entrega_hackathon"

TITULOS = {
    "cover": "Portada", "contraste": "Miguel y Ana", "brecha": "Lo que le falta",
    "validacion": "Validación con un usuario y un mentor",
    "producto": "Qué compra: acciones, ETFs de sector y bonos",
    "reglas": "Cuánto en cada cosa: un modelo dinámico con dos alarmas",
    "transparencia": "Demo en vivo: el backtest, mes a mes",
    "resultados": "Resultados y por qué desde 2007", "porque": "¿Por qué nosotros?",
    "riesgo": "El riesgo", "negocio": "Modelo de negocio y siguientes pasos",
    "metodo": "Por qué no hay sobreajuste ni sesgo", "cierre": "Cierre",
}


def laminas():
    deck = json.loads((DECK / "deck.json").read_text())
    for n, sid in enumerate(deck["order"], 1):
        yield n, sid, (DECK / "slides" / f"{sid}.html").read_text()


def nota(seccion):
    a = re.search(r"<aside>(.*?)</aside>", seccion, re.S).group(1).strip()
    tiempo, texto = re.match(r"\[(.*?)\]\s*(.*)", a, re.S).groups()
    return tiempo, html.unescape(texto)


def regenerar_guion():
    bloques, palabras = [], 0
    for n, sid, s in laminas():
        tiempo, texto = nota(s)
        palabras += len(re.sub(r"\(.*?\)", "", texto).split())
        bloques.append(f"### {n} · {TITULOS.get(sid, sid)} ({tiempo})\n{texto}\n")
    p = PITCH / "PITCH.md"
    s = p.read_text()
    a, b = s.index("## Guion"), s.index("## Lámina de método")
    s = (s[:a] + f"## Guion (texto para decir en voz alta, ~{palabras} palabras ≈ 5 minutos)\n\n"
         "Es el mismo texto de las notas de cada lámina. Lo que va entre paréntesis es una acción, "
         "no se dice.\n\n" + "\n".join(bloques) + "\n" + s[b:])
    p.write_text(s)
    return palabras


VISOR = """<!doctype html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>DHAR Capital</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300..700&family=Inter:wght@400;600&display=swap">
<style>
{css}
html,body{{margin:0;height:100%;background:#000;overflow:hidden}}
#escena{{position:absolute;left:50%;top:50%;width:1920px;height:1080px;transform-origin:0 0}}
section{{position:absolute;inset:0;width:1920px;height:1080px;box-sizing:border-box;overflow:hidden;display:none}}
section.activa{{display:flex}}
section aside{{display:none}}
p,h1,h2,h3{{margin:0}}
#notas{{position:fixed;left:0;right:0;bottom:0;max-height:34%;overflow:auto;background:#111A22;color:#F4F7F9;
  font:18px/1.45 Inter,Arial,sans-serif;padding:14px 20px;border-top:2px solid #C7FF35;display:none}}
#ayuda{{position:fixed;right:12px;top:10px;color:#84919D;font:13px Inter,Arial,sans-serif}}
@media print{{
  @page{{size:1920px 1080px;margin:0}}
  html,body{{overflow:visible;height:auto;background:#080D12}}
  #escena{{position:static;transform:none!important}}
  section{{position:relative;display:flex!important;page-break-after:always;break-after:page}}
  #notas,#ayuda{{display:none!important}}
  .in{{animation:none}}
}}
</style></head><body>
<div id="escena">
{laminas}
</div>
<div id="notas"></div>
<div id="ayuda">← → avanzar · N notas · Ctrl+P guardar como PDF</div>
<script>
const L=[...document.querySelectorAll('section')];let i=0;
const N=document.getElementById('notas'),E=document.getElementById('escena');
function ir(k){{i=Math.max(0,Math.min(L.length-1,k));L.forEach((s,j)=>s.classList.toggle('activa',j===i));
  const a=L[i].querySelector('aside');N.textContent=(i+1)+' / '+L.length+(a?' · '+a.textContent:'');location.hash=i+1;}}
function ajustar(){{const e=Math.min(innerWidth/1920,innerHeight/1080);E.style.transform='scale('+e+') translate(-50%,-50%)';}}
addEventListener('resize',ajustar);
addEventListener('keydown',ev=>{{if(['ArrowRight','PageDown',' '].includes(ev.key))ir(i+1);
  else if(['ArrowLeft','PageUp'].includes(ev.key))ir(i-1);
  else if(ev.key==='n'||ev.key==='N')N.style.display=N.style.display==='block'?'none':'block';}});
addEventListener('click',ev=>{{if(ev.target.closest('a'))return;ir(ev.clientX>innerWidth/2?i+1:i-1);}});
ajustar();ir((parseInt(location.hash.slice(1))||1)-1);
</script></body></html>
"""


def presentacion(destino: Path):
    css = (DECK / "deck.css").read_text()
    cuerpo = "\n".join(s.replace("project/ds/fotos/", "fotos/") for _, _, s in laminas())
    destino.mkdir(parents=True, exist_ok=True)
    (destino / "presentacion.html").write_text(VISOR.format(css=css, laminas=cuerpo))
    shutil.copytree(DECK / "ds" / "fotos", destino / "fotos", dirs_exist_ok=True)


def lamina_metodo(destino: Path):
    css = (DECK / "deck.css").read_text()
    s = (DECK / "slides" / "metodo.html").read_text()
    destino.mkdir(parents=True, exist_ok=True)
    (destino / "lamina_metodo.html").write_text(VISOR.format(css=css, laminas=s))
    texto = (PITCH / "PITCH.md").read_text()
    a = texto.index("## Lámina de método")
    b = texto.index("## Cifras citadas")
    (destino / "LAMINA_METODO.md").write_text("# Lámina de método · DHAR Capital\n\n" + texto[a:b].split("\n", 1)[1])


def copiar(origen, destino):
    destino = Path(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)
    if Path(origen).is_dir():
        shutil.copytree(origen, destino, dirs_exist_ok=True)
    else:
        shutil.copy2(origen, destino)


def main():
    palabras = regenerar_guion()
    if SALIDA.exists():
        for hijo in SALIDA.iterdir():
            if hijo.name != "README.md":
                shutil.rmtree(hijo) if hijo.is_dir() else hijo.unlink()
    v3 = RAIZ / "modelo_principal_v3"
    b = SALIDA / "01_backtest"
    copiar(v3 / "MODELO_PRINCIPAL.md", b / "MODELO_PRINCIPAL.md")
    copiar(v3 / "MODELO_PRINCIPAL.md5", b / "MODELO_PRINCIPAL.md5")
    copiar(v3 / "ATRIBUCION.md", b / "ATRIBUCION.md")
    copiar(v3 / "weights.csv", b / "weights.csv")
    for corrida in ("backtest_2007_base", "backtest_2007_estres", "backtest_2010_base", "backtest_2010_estres"):
        for f in ("resumen.json", "Register.csv", "motor.log"):
            copiar(v3 / "backtests" / corrida / f, b / corrida / f)
        for x in (v3 / "backtests" / corrida).glob("*.xlsx"):
            copiar(x, b / corrida / "resultados_backtest_engine.xlsx")
    for f in ("resumen.json", "Register.csv"):
        copiar(RAIZ / "perfil_moderado_v3" / "backtest_base" / f, b / "perfil_moderado_2007_base" / f)
    presentacion(SALIDA / "03_pitch")
    copiar(PITCH / "PITCH.md", SALIDA / "03_pitch" / "PITCH.md")
    lamina_metodo(SALIDA / "04_lamina_metodo")
    d = SALIDA / "05_demo"
    for f in ("reporte_ana.html", "datos.json", "extraer_datos.py"):
        copiar(PITCH / "demo" / f, d / f)
    copiar(PITCH / "fotos", d / "fotos_prueba_usuario")
    print(f"Listo: {SALIDA} · guion de {palabras} palabras")


if __name__ == "__main__":
    main()
