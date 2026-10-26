const { chromium } = require(require('child_process').execSync('npm root -g').toString().trim() + '/playwright');
(async () => {
  const b = await chromium.launch(); const errs=[];
  const p = await b.newPage({ viewport: {width: 1366, height: 900} });
  p.on('pageerror', e => errs.push(e.message));
  const count = () => p.evaluate(() => [...document.querySelectorAll('.news-item')].filter(e => !e.hidden).length);
  for (const q of ['', '?thema=huurrecht', '?thema=europees', '?thema=sociale-zekerheid', '?gebied=arbeidsrecht&thema=europees']) {
    await p.goto('http://localhost:8765/nieuws.html' + q); console.log(q || 'alle', await count());
  }
  await p.goto('http://localhost:8765/nieuws.html');
  await p.click('[data-filter=thema][data-value=huurrecht]'); console.log('click huur', await count(), p.url());
  await p.evaluate(() => document.querySelectorAll('.reveal').forEach(e => e.classList.add('in'))); await p.waitForTimeout(800);
  await p.screenshot({ path: process.argv[2] + '/nieuws-huur.png', fullPage: false });
  const m = await b.newPage({ viewport: {width: 390, height: 844} });
  await m.goto('http://localhost:8765/nieuws.html?thema=europees');
  await m.evaluate(() => document.querySelectorAll('.reveal').forEach(e => e.classList.add('in'))); await m.waitForTimeout(800);
  console.log('mobile overflow', await m.evaluate(() => document.documentElement.scrollWidth));
  await m.screenshot({ path: process.argv[2] + '/nieuws-m.png', clip: {x:0,y:300,width:390,height:1300}, fullPage: true });
  console.log(errs.join('\n') || 'no errors'); await b.close();
})();
