from pathlib import Path
from urllib.request import Request, urlopen
import html as htmlmod
import json
import re
import subprocess

SOURCE_PAGE='https://freesound.org/people/rsn267/sounds/418780/'
SOURCE_TITLE='Indian Wedding Dhols'
SOURCE_AUTHOR='rsn267'


def fetch_bytes(url):
    req=Request(url,headers={
        'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36',
        'Referer':SOURCE_PAGE,
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
    })
    with urlopen(req,timeout=45) as r:
        return r.read()


def find_preview_url(page_text):
    text=htmlmod.unescape(page_text).replace('\\/','/')
    patterns=[
        r'"preview-hq-mp3"\s*:\s*"([^"]+)"',
        r'"preview-lq-mp3"\s*:\s*"([^"]+)"',
        r'(https://cdn\.freesound\.org/previews/[^"\'<>\s]+-hq\.mp3)',
        r'(https://cdn\.freesound\.org/previews/[^"\'<>\s]+-lq\.mp3)',
        r'(https://cdn\.freesound\.org/previews/[^"\'<>\s]+\.mp3)',
    ]
    for pat in patterns:
        m=re.search(pat,text,re.I)
        if m:
            return m.group(1)
    raise SystemExit('Could not locate Freesound preview URL')


page=fetch_bytes(SOURCE_PAGE).decode('utf-8','ignore')
preview=find_preview_url(page)
raw=fetch_bytes(preview)
Path('/tmp/india-dhol-source.mp3').write_bytes(raw)

outdir=Path('sounds/india')
outdir.mkdir(parents=True,exist_ok=True)
starts=[4.5,18.0,34.0,50.0]
for i,start in enumerate(starts,1):
    out=outdir/f'india-dhol-{i}.mp3'
    filt='highpass=f=55,lowpass=f=9000,acompressor=threshold=-18dB:ratio=2.5:attack=5:release=80,volume=1.15,afade=t=in:st=0:d=0.02,afade=t=out:st=0.93:d=0.15'
    subprocess.run([
        'ffmpeg','-hide_banner','-loglevel','error','-y',
        '-ss',str(start),'-i','/tmp/india-dhol-source.mp3','-t','1.08',
        '-af',filt,'-ar','44100','-ac','1','-b:a','96k',str(out)
    ],check=True)

p=Path('index.html')
s=p.read_text(encoding='utf-8')

s=s.replace('SLAP! Mobile 3.5 · Bhangra SFX','SLAP! Mobile 3.6 · India Dhol Pack')
s=s.replace('<span class="ver">3.5</span>','<span class="ver">3.6</span>')
s=s.replace('SLAP! Mobile 3.5 · Bhangra SFX · CC0 · Background Audio · PWA','SLAP! Mobile 3.6 · India Dhol Pack · CC0 · Background Audio · PWA')

if 'data-sound="indiaPerson"' not in s:
    old='<button class="preset" data-sound="desiChaos"><span>🎉</span>DESI CHAOS</button></div><div class="systemGestureNote">'
    new='<button class="preset" data-sound="desiChaos"><span>🎉</span>DESI CHAOS</button><button class="preset" data-sound="indiaPerson"><span>🇮🇳</span>印度人</button></div><div class="systemGestureNote">'
    if old not in s:
        raise SystemExit('Bhangra preset insertion point not found')
    s=s.replace(old,new,1)

if 'CC0 Indian Wedding Dhols' not in s:
    marker='<div class="systemGestureNote"><b>聲音設計：</b>參考你提供影片的高能量旁遮普舞曲氣氛，使用原創 dhol 類鼓點、短促「HA / HEY / OI」非語詞人聲合成與音高滑動；不取樣原曲、不重製原旋律或歌詞。</div>'
    extra=marker+'<div class="systemGestureNote"><b>🇮🇳 印度人按鈕：</b>使用 Freesound 的 CC0 <i>Indian Wedding Dhols</i> 實錄音效裁切成 4 個短擊版本，再疊加原創 Bhangra 合成層；不包含〈Tunak Tunak Tun〉原曲錄音。</div>'
    if marker in s:
        s=s.replace(marker,extra,1)

m=re.search(r'const sampleFiles=(\{.*?\});\nconst sampleBroken=',s,re.S)
if not m:
    raise SystemExit('sampleFiles object not found')
sample_files=json.loads(m.group(1))
sample_files['indiaPerson']=[f'./sounds/india/india-dhol-{i}.mp3' for i in range(1,5)]
obj=json.dumps(sample_files,ensure_ascii=False,separators=(',',':'))
s=s[:m.start(1)]+obj+s[m.end(1):]

old_play="const promise=el.play();if(promise&&promise.catch)promise.catch(()=>{sampleBroken.add(src);synthSound(power,kind)});"
new_play="const promise=el.play();if(kind==='indiaPerson'){try{playBhangraStyle('bhangra',Math.max(7,power*.82))}catch(e){}}if(promise&&promise.catch)promise.catch(()=>{sampleBroken.add(src);synthSound(power,kind)});"
if old_play in s and "kind==='indiaPerson'" not in s[s.find('function playSound'):s.find('let alarmInt')]:
    s=s.replace(old_play,new_play,1)

p.write_text(s,encoding='utf-8')

mp=Path('manifest.webmanifest')
if mp.exists():
    md=json.loads(mp.read_text(encoding='utf-8'))
    md['name']='SLAP! Mobile 3.6'
    md['description']='手機動作感測遊戲與防盜警戒，內建 CC0 人聲、印度 Dhol / Bhangra 音效、拍擊力度分級、挑戰模式與背景存活強化。'
    mp.write_text(json.dumps(md,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

swp=Path('sw.js')
if swp.exists():
    sw=swp.read_text(encoding='utf-8')
    sw=re.sub(r"const CACHE='[^']+';","const CACHE='slap-mobile-v8-india-dhol';",sw,count=1)
    am=re.search(r'const ASSETS=(\[.*?\]);',sw,re.S)
    if not am:
        raise SystemExit('Service worker ASSETS not found')
    assets=json.loads(am.group(1))
    for i in range(1,5):
        f=f'./sounds/india/india-dhol-{i}.mp3'
        if f not in assets: assets.append(f)
    sw=sw[:am.start(1)]+json.dumps(assets,ensure_ascii=False)+sw[am.end(1):]
    swp.write_text(sw,encoding='utf-8')

Path('INDIA_AUDIO_LICENSE.md').write_text(f'''# India Dhol Audio Pack\n\nThis app includes short edited clips derived from **{SOURCE_TITLE}** by **{SOURCE_AUTHOR}** on Freesound.\n\n- Source: {SOURCE_PAGE}\n- License shown on the source page: **Creative Commons 0 (CC0)**\n- The app stores four short edited MP3 clips locally under `sounds/india/`.\n- The `印度人` preset layers those CC0 Dhol clips with original Web Audio Bhangra-style synthesis created for this project.\n- No audio from Daler Mehndi's **Tunak Tunak Tun** is bundled.\n''',encoding='utf-8')
