const {chromium}=require('/Users/w6x/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const path=require('node:path');const fs=require('node:fs');const assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({channel:'chrome',headless:true}); const page=await browser.newPage({viewport:{width:1440,height:1000}});
 const base='file://'+path.resolve('senaryo-atlasi.html');const results=[];const errors=[];const requests=[];
 page.on('pageerror',e=>errors.push(String(e)));page.on('request',r=>{if(/^https?:/.test(r.url()))requests.push(r.url())});
 const done=(name)=>results.push({name,status:'passed'});
 const route=async(r)=>{await page.goto(base+'#/'+r);await page.locator('main').waitFor();};
 await route('baslangic');await page.getByRole('heading',{level:1}).waitFor();done('Offline single HTML renders');await page.screenshot({path:'audit/home-desktop.png',fullPage:true});
 await route('tasarimci');const count=await page.locator('.senaryo-karti').count();assert.equal(count,10);
 for(let i=0;i<count;i++){
  await page.locator('.senaryo-karti').nth(i).click();
  await page.waitForFunction(()=>!!document.querySelector('.tuval-ic svg'));
  const current=await page.evaluate(()=>JSON.parse(localStorage.getItem('senaryo-atlasi:durum:v1'))?.senaryoId);
  assert.ok(current);done('Preset selection: '+current);
 }
 await page.locator('.senaryo-karti').first().click();
 await route('tasarimci?sekme=kurallar&kural=R17');const budget=page.getByRole('textbox',{name:'Görev maliyet tavanı'});await budget.fill('40');await budget.press('Tab');
 assert.equal(await page.evaluate(()=>JSON.parse(localStorage.getItem('senaryo-atlasi:durum:v1')).kurallar.R17.degerler.tavan),40);done('Numeric ECA parameter changes state');
 await page.reload();await budget.waitFor();assert.ok((await budget.inputValue()).startsWith('40'));done('Selection survives reload');
 const dlp=page.waitForEvent('download');await page.getByRole('button',{name:'Kararları indir (JSON)'}).click();const dl=await dlp;const state=JSON.parse(fs.readFileSync(await dl.path(),'utf8'));assert.equal(state.durum.kurallar.R17.degerler.tavan,40);assert.equal(state.kanit.length,82);assert.equal(state.eca.length,79);assert.equal(state.qualification,'not_run');fs.writeFileSync('audit/export-example.json',JSON.stringify(state,null,2));done('Decision bundle exports selected state, ECA and evidence');
 await page.locator('input[type=file]').setInputFiles({name:'bad.json',mimeType:'application/json',buffer:Buffer.from('{"surum":1,"senaryoId":"tek-gorev","kararlar":null}')});await page.getByText('Dosya bu merkezin karar dosyası değil.').waitFor();done('Malformed import rejected without crash');
 await page.locator('input[type=file]').setInputFiles({name:'restore.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify(state))});await page.waitForTimeout(200);assert.equal(await page.getByText('Dosya bu merkezin karar dosyası değil.').count(),0);done('Full decision package round trips');
 await route('simulasyon');await page.getByRole('button',{name:'Olayı değerlendir',exact:true}).click();await page.getByText('RESIZE',{exact:true}).first().waitFor();done('OOM plan simulation uses selected ECA');
 await page.getByRole('switch',{name:'OOM sayacı artmış'}).uncheck();assert.equal(await page.getByText('RESIZE',{exact:true}).count(),0);await page.getByRole('button',{name:'Olayı değerlendir',exact:true}).click();await page.getByText('DIAGNOSE',{exact:true}).first().waitFor();done('Input change invalidates stale simulation; no OOM proof means diagnose');
 await route('karar-modelleri');assert.equal(await page.locator('.mantine-Accordion-item').count(),19);await page.getByRole('button',{name:/Laya.*Kaynak incelendi/}).click();await page.getByRole('button',{name:'Karar katmanında seç',exact:true}).filter({visible:true}).click();assert.equal(await page.evaluate(()=>JSON.parse(localStorage.getItem('senaryo-atlasi:durum:v1')).kararlar.kararModeli),'laya');done('Laya identity and scenario selection');
 for(const r of ['kanit','kaynaklar','uyarlama','ajanlar','belgeler','istatistikler','sorunlar','teknolojiler']){await route(r);await page.waitForTimeout(120);assert.ok(await page.locator('main').innerText());done('Navigation: '+r);}
 await route('diyagramlar');await page.waitForFunction(()=>document.querySelectorAll('.tuval-ic svg').length===7,{timeout:30000});assert.equal(await page.getByText('Diyagram çizilemedi').count(),0);
 const svgDL=page.waitForEvent('download');await page.getByRole('button',{name:'SVG',exact:true}).first().click();const svg=await svgDL;assert.match(fs.readFileSync(await svg.path(),'utf8'),/<svg/);done('Seven diagrams render and SVG downloads');await page.screenshot({path:'audit/diagrams.png',fullPage:false});
 await route('tasarimci');await page.locator('.senaryo-karti').first().click(); await page.getByRole('button',{name:'Sıfırla',exact:true}).click(); assert.equal(await page.evaluate(()=>JSON.parse(localStorage.getItem('senaryo-atlasi:durum:v1')).kurallar.R17.degerler.tavan),25); // final PDF is default
 await route('rapor');await page.locator('[data-report-ready="true"]').waitFor({timeout:30000});assert.ok(await page.getByRole('button',{name:'PDF olarak kaydet',exact:true}).isEnabled());done('Print waits for current diagrams and fonts');
 fs.mkdirSync('output/pdf',{recursive:true});await page.emulateMedia({media:'print'});await page.pdf({path:'output/pdf/ornek-karar-raporu.pdf',preferCSSPageSize:true,printBackground:true});await page.emulateMedia({media:'screen'});done('A4 PDF generated');
 await page.setViewportSize({width:390,height:844});await route('baslangic');await page.waitForTimeout(400);await page.screenshot({path:'audit/home-mobile.png',fullPage:true});assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+2),false);done('390px mobile home fits viewport');
 await page.getByRole('button',{name:'Menü',exact:true}).click();await page.getByText('Olay laboratuvarı',{exact:true}).first().click();await page.getByRole('heading',{name:'Olay laboratuvarı'}).waitFor();done('Mobile navigation works');
 assert.deepEqual(errors,[]);assert.deepEqual(requests,[]);done('No runtime JS errors or external requests');
 fs.writeFileSync('audit/ui-results.json',JSON.stringify({at:new Date().toISOString(),environment:'Chrome headless, file:// offline, desktop 1440x1000 and mobile 390x844',errors,external_requests:requests,results},null,2));console.log(results.length+' UI checks passed');await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
