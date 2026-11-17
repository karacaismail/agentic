from pathlib import Path
import json,hashlib,datetime
root=Path(__file__).resolve().parent.parent
files=[]
for p in sorted(root.rglob('*')):
 rel=p.relative_to(root)
 if not p.is_file() or any(x in rel.parts for x in ['node_modules','.git','__pycache__']):continue
 if rel.parts[0]=='audit' or p.name=='DOSYA-MAP.json':continue
 files.append({'path':rel.as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(root/'DOSYA-MAP.json').write_text(json.dumps({'schema_version':1,'generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'entrypoint':'senaryo-atlasi.html','json_map':'data/map.json','readme':'README.md','current_review':'docs/KANIT-VE-KARAR-INCELEMESI.md','decision_evidence':'src/analiz/bulgular.json','research_report':'../reports/Senaryo ve karar arayüzü.md','research_notes':'../research_notes/Senaryo ve karar arayüzü','files':files,'validation':['audit/contracts-results.json','audit/ui-results.json','audit/evidence-ux-results.json','audit/protected-check.json','audit/pdf-review.json']},ensure_ascii=False,indent=2)+'\n')
print(f'File map: {len(files)} entries')
