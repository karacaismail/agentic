#!/usr/bin/env python3
"""İhtiyaç haritası JSON dosyalarını tek bir HTML görselleştirmesine gömer.

Kullanım:  python3 gorsel/uret.py
Çıktı:     gorsel/ihtiyac-haritasi.html  (sablon.html + veri)
JSON dosyaları değiştiğinde yeniden çalıştırın.
"""
import glob, json, os

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GORSEL = os.path.join(KOK, "gorsel")

def oku(rel):
    with open(os.path.join(KOK, rel), encoding="utf-8") as f:
        return json.load(f)

kumeler, ihtiyaclar = [], []
for p in sorted(glob.glob(os.path.join(KOK, "02-ihtiyac-kumeleri", "*", "*.json"))):
    d = json.load(open(p, encoding="utf-8"))
    k = d["kume"]
    k["sayi"] = len(d["ihtiyaclar"])
    kumeler.append(k)
    for n in d["ihtiyaclar"]:
        n["kume"] = k["id"]
        n["alan"] = k["alan"]
        ihtiyaclar.append(n)

yerel = oku("01-cerceve/kaynak-envanteri.json")["kaynaklar"]
dis = oku("01-cerceve/dis-kaynaklar.json")["kaynaklar"]

veri = {
    "indeks": oku("00-indeks.json"),
    "amac": oku("01-cerceve/ana-amac.json"),
    "org": oku("01-cerceve/organizasyon-modeli.json"),
    "belirsizlik": oku("01-cerceve/belirsizlik-parametreleri.json")["parametreler"],
    "yetenek": oku("01-cerceve/yetenek-siniflari.json"),
    "kaynak": yerel,
    "dis": dis,
    "sozluk": oku("01-cerceve/sozluk.json")["terimler"],
    "kumeler": kumeler,
    "ihtiyaclar": ihtiyaclar,
    "bilinmeyen": oku("03-analizler/bilinmeyenler-analizi.json"),
    "gap": oku("03-analizler/gap-analizi.json"),
    "cember": oku("03-analizler/cember-analizi.json"),
    "celiski": oku("03-analizler/celiskiler.json")["celiskiler"],
    "soru": oku("03-analizler/acik-sorular.json"),
    "varsayim": oku("03-analizler/varsayimlar.json")["varsayimlar"],
    "risk": oku("03-analizler/risk-kaydi.json"),
    "karar": oku("04-projelendirme-girdileri/bekleyen-kararlar.json")["kararlar"],
    "kapi": oku("04-projelendirme-girdileri/hazirlik-kapilari.json")["kapilar"],
    "olcek": oku("04-projelendirme-girdileri/olcek-senaryolari.json"),
}

gomulu = json.dumps(veri, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
sablon = open(os.path.join(GORSEL, "sablon.html"), encoding="utf-8").read()
cikti = sablon.replace("__VERI__", gomulu)
hedef = os.path.join(GORSEL, "ihtiyac-haritasi.html")
open(hedef, "w", encoding="utf-8").write(cikti)
print(f"{hedef}  ({len(cikti)/1024:.0f} KB, {len(ihtiyaclar)} ihtiyaç)")
