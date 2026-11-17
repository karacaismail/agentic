"""Read-only research snapshot. Only writes this application's generated JSON."""
from pathlib import Path
import json, hashlib, datetime, re
APP=Path(__file__).resolve().parent.parent
ROOT=APP.parent
CODEX=ROOT.parent/'otomasyon coding 2'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
records=[]; files={}
for folder,key,group in [(CODEX/'kestra-gecmis-incelemesi/bulgular','findings','Yerel geçmiş'),(CODEX/'dunya-vakalari/kumeler','cases','Dünya vakaları'),(CODEX/'agentic-sistem/data/15_derin_inceleme','records','Mimari inceleme')]:
 for p in sorted(folder.glob('*.json')):
  if group=='Mimari inceleme' and not p.name.startswith('01_'): continue
  data=json.loads(p.read_text()); items=data.get(key,[])
  for i,r in enumerate(items):
   records.append({'id':r['id'],'grup':group,'baslik':r.get('title',r.get('symptom',r['id'])),'kaynak':str(p),'sha256':sha(p),'pointer':f'/{key}/{i}','ham':r})
  files[str(p)]={'yol':str(p),'sha256':sha(p),'icerik':p.read_text(),'tur':'application/json'}
# All text references explicitly in the UI directory, plus original evidence registries.
source_ts=(APP/'src/veri/kaynaklar.ts').read_text()
paths=list((ROOT/'mimari-haritasi/arastirma').glob('*'))
paths+=list((APP/'docs').glob('*.md'))
paths += [CODEX/'kestra-gecmis-incelemesi/kaynaklar/kanitlar.json',CODEX/'kestra-gecmis-incelemesi/RAPOR.md',CODEX/'dunya-vakalari/kaynaklar.json',CODEX/'dunya-vakalari/kanit-sinirlari.json',CODEX/'dunya-vakalari/kabul-deneyleri.json']
paths+=list((CODEX/'agentic-sistem/data/15_derin_inceleme').glob('*.json'))
paths+=list((ROOT/'research_notes/Senaryo ve karar arayüzü').glob('*'))
paths+=list((ROOT/'reports').glob('Senaryo ve karar arayüzü.md'))
paths+=list((CODEX/'devir-teslim').glob('*.md'))
paths+=list((CODEX/'reports').glob('Karşılaştırmada kaçan*.md'))
# index maps give navigation to larger corpora, not an unbounded archive.
paths += [ROOT/'mimari-haritasi/pilot-dersleri.json',ROOT/'ihtiyac-haritasi/00-indeks.json',ROOT/'arac-haritasi/00-harita.json',ROOT/'risk-haritasi/00-risk-haritasi.json',ROOT/'mimari-haritasi/00-mimari.json',ROOT/'devir-teslim/DEVIR-TESLIM.md']
for p in paths:
 if p.is_file() and p.suffix in ['.md','.json'] and p.stat().st_size<2_000_000:
  files[str(p)]={'yol':str(p),'sha256':sha(p),'icerik':p.read_text(),'tur':'application/json' if p.suffix=='.json' else 'text/markdown'}
result={'surum':1,'uretildi':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sinir':'82 kayıt 82 bağımsız olay değildir. Tarihî kaynak iddiaları güncel ürün durumunu ispatlamaz. Deneylerin çoğu çalıştırılmadı.','kayitlar':records,'dosyalar':list(files.values())}
assert len(records)==82, len(records)
(APP/'src/veri/kanitlar.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(f'Kanıt: {len(records)} özgün kayıt, {len(files)} gömülü belge.')
