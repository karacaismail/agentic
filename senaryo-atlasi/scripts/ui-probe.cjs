const {chromium}=require('/Users/w6x/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const path=require('node:path');
(async()=>{
 const browser=await chromium.launch({channel:'chrome',headless:true});const page=await browser.newPage({viewport:{width:1440,height:1000}});
 const errors=[];page.on('pageerror',e=>errors.push(String(e)));let net=[];page.on('request',r=>{if(r.url().startsWith('http'))net.push(r.url())});
 await page.goto('file://'+path.resolve('senaryo-atlasi.html'));await page.getByRole('heading',{name:'Araştırmadanseçilebilir iş akışına.'}).waitFor({timeout:15000}).catch(()=>{});
 await page.screenshot({path:'audit/home-desktop.png',fullPage:true});
 console.log('HOME',await page.title(), await page.locator('h1').innerText(),errors,net);
 for(const route of ['tasarimci','simulasyon','diyagramlar','karar-modelleri','kanit','rapor']){
  await page.goto('file://'+path.resolve('senaryo-atlasi.html')+'#/'+route);await page.waitForTimeout(1000);
  if(route==='simulasyon'){await page.getByRole('button',{name:'Olayı değerlendir',exact:true}).click();console.log('SIM',await page.locator('main').innerText().then(x=>x.slice(-800)));}
  if(route==='diyagramlar'){await page.waitForTimeout(6000);console.log('DIAGRAM',await page.locator('.tuval-ic svg').count(),'errors',await page.getByText('Diyagram çizilemedi').count());await page.screenshot({path:'audit/diagrams.png',fullPage:false});}
  if(route==='rapor'){
   await page.locator('[data-report-ready="true"]').waitFor({timeout:30000});await page.emulateMedia({media:'print'});await page.pdf({path:'audit/ornek-karar-raporu.pdf',preferCSSPageSize:true,printBackground:true});await page.emulateMedia({media:'screen'});
   console.log('PDF ready');
  }
 }
 await page.setViewportSize({width:390,height:844});await page.goto('file://'+path.resolve('senaryo-atlasi.html'));await page.waitForTimeout(700);await page.screenshot({path:'audit/home-mobile.png',fullPage:true});
 console.log('ERRORS',errors);await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
