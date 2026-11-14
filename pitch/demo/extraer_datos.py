import re, zipfile, csv, json, datetime as dt, sys
def sheet10(path):
    z=zipfile.ZipFile(path); x=z.read('xl/worksheets/sheet10.xml').decode()
    out=[]
    for row in re.findall(r'<row r="(\d+)"[^>]*>(.*?)</row>', x):
        r=int(row[0])
        if r<4: continue
        cells=dict(re.findall(r'<c r="([A-H])\d+"[^>]*>(?:<v>([^<]*)</v>|<is>.*?</is>)</c>', row[1]))
        d=dt.date(1899,12,30)+dt.timedelta(days=int(float(cells['A'])))
        out.append((d.isoformat(), float(cells['C']), float(cells['E']), float(cells['G'])))
    return out
import glob
base=sheet10(glob.glob('modelo_principal_v3/backtests/backtest_2007_base/*.xlsx')[0])
mod={d:v for d,v,_,_ in sheet10(glob.glob('perfil_moderado_v3/backtest_base/*.xlsx')[0])}
# month-end points
pts={};dd={};pk=0;pkd=None;pkm=0;pkmd=None
for d,v,k,s in base:
    pts[d[:7]]=(d,v,k,s)
    if v>pk: pk,pkd=v,d
    mv=mod.get(d)
    if mv and mv>pkm: pkm,pkmd=mv,d
    dd[d[:7]]=(round(v/pk-1,4),pkd,round(mv/pkm-1,4) if mv else None,pkmd)
# weights targets
W=list(csv.reader(open('modelo_principal_v3/weights.csv')))
dates=W[0][1:]; tick=[r[0] for r in W[1:]]
targets={}
for j,d in enumerate(dates):
    h={tick[i]:float(W[i+1][j+1]) for i in range(len(tick)) if float(W[i+1][j+1])>0.0005}
    targets[d]=h
dec={r['fecha']:(float(r['prob']),r['decisión']) for r in csv.DictReader(open('modelo_principal_c2/decisiones_refugio.csv'))}
reg={r['operación']:r for r in csv.DictReader(open('resultados_regimen_m2/regimenes.csv'))}
months=[]
for m,(d,v,k,s) in sorted(pts.items()):
    # target effective in the month: last rebalance date <= d
    td=max(x for x in dates if x<=d)
    r=reg[max(x for x in reg if x<=td)]
    dz=dec.get(td)
    months.append(dict(m=m,d=d,v=round(v),k=round(k),s=round(s),mo=round(mod.get(d,0)) if d in mod else None,
        h={a:round(b,3) for a,b in sorted(targets[td].items(),key=lambda x:-x[1])},
        r=r.get('régimen'),t=r.get('tendencia_arriba')=='True',c=r.get('canario_ok')=='True',td=td,dd=dd[m][0],pd=dd[m][1],ddm=dd[m][2],pdm=dd[m][3],p=dz[0] if dz else None,dc=dz[1] if dz else None))
json.dump(months,open(sys.argv[1],'w'),separators=(',',':'),ensure_ascii=False)
print(len(months),months[0],months[-1],sep='\n')
print(sum(1 for x in months if x['mo'] is None),'sin moderado')
