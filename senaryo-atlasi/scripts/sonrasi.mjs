// Build sonrası: cikti/index.html -> senaryo-atlasi.html (uygulama klasörünün kökünde tek dosya)
import { renameSync, rmSync, statSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const kok = join(dirname(fileURLToPath(import.meta.url)), '..');
const kaynak = join(kok, 'cikti', 'index.html');
const hedef = join(kok, 'senaryo-atlasi.html');
renameSync(kaynak, hedef);
rmSync(join(kok, 'cikti'), { recursive: true, force: true });
const mb = (statSync(hedef).size / 1024 / 1024).toFixed(2);
console.log(`Hazır: senaryo-atlasi.html (${mb} MB)`);
