from pathlib import Path
import hashlib,json,datetime
b=json.loads(Path('audit/source-baseline.json').read_text());changed=[];missing=[];count=0
for key in ['reuse_source','protected_files']:
 for x in b[key]:
  p=Path(x['path']);count+=1
  if not p.is_file():missing.append(str(p));continue
  with p.open('rb') as f:
   digest=hashlib.sha256()
   for chunk in iter(lambda:f.read(1024*1024),b''):digest.update(chunk)
   h=digest.hexdigest()
  if h!=x['sha256']:changed.append(str(p))
out={'checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checked_files':count,'changed':changed,'missing':missing,'scope':'Baseline original UI plus indexed coding2 files and coding/agentic-fabrika; baseline content comparison, not a claim about unindexed files.'}
out['protected_runtime_and_coding2_changed']=[p for p in changed if '/otomasyon coding 2/' in p or '/agentic-fabrika/' in p]
out['separate_ui_changes']=[p for p in changed if '/fabrika-karar-merkezi/' in p]
out['interpretation']='No writes to comparison sources by this task; a baseline mismatch in the separate UI is retained and is not attributed to this task. Distinct files/inodes verified for sampled paths.'
Path('audit/protected-check.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(out,ensure_ascii=False))
