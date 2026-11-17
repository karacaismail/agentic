import {useMemo} from 'react';
import {marked} from 'marked';
import DOMPurify from 'dompurify';
import {Code} from '@mantine/core';
import kanit from '../veri/kanitlar.json';
export function BelgeOkuyucu({icerik,yol}:{icerik:string;yol:string}){
 const html=useMemo(()=>{
  if(!/\.md$/i.test(yol))return '';
  const parsed=marked.parse(icerik,{async:false});
  const safe=DOMPurify.sanitize(parsed,{FORBID_TAGS:['img','iframe','style','form','input','button'],FORBID_ATTR:['style']});
  const doc=new DOMParser().parseFromString(safe,'text/html');
  doc.querySelectorAll('a').forEach(a=>{
   const href=a.getAttribute('href')??'';
   if(/^https?:\/\//i.test(href)){a.target='_blank';a.rel='noreferrer noopener';}
   else {
    let target='';try {target=decodeURIComponent(new URL(href,'https://local.invalid'+yol).pathname).replace(/:\d+$/,'');}catch{}
    const f=kanit.dosyalar.find(f=>f.yol===target);
    if(f){a.href=`#/kaynaklar?dosya=${encodeURIComponent(f.yol)}`;}
    else {a.removeAttribute('href');a.title=`Bağlı dosya bu HTML içinde değil: ${href}`;a.className='unavailable-link';}
   }
  });
  return doc.body.innerHTML;
 },[icerik,yol]);
 return html?<div className="document-prose" dangerouslySetInnerHTML={{__html:html}}/>:<Code block className="document-json">{icerik}</Code>;
}
