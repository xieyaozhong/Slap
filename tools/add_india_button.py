from pathlib import Path
import json
import math
import random
import re
import struct
import wave

RATE=22050
DUR=1.12
OUTDIR=Path('sounds/india')
OUTDIR.mkdir(parents=True,exist_ok=True)


def env_decay(t,decay):
    return math.exp(-t/decay) if t>=0 else 0.0


def add_low_dhol(buf,start,amp=0.9,pitch=150,end=58,decay=.16):
    s0=int(start*RATE)
    length=int(.28*RATE)
    phase=0.0
    for j in range(length):
        i=s0+j
        if i>=len(buf): break
        t=j/RATE
        f=pitch*((end/pitch)**min(1,t/.16))
        phase += 2*math.pi*f/RATE
        e=env_decay(t,decay)
        noise=(random.random()*2-1)*.10*e
        buf[i]+=amp*(math.sin(phase)*e+noise)


def add_high_dhol(buf,start,amp=.5,pitch=240):
    s0=int(start*RATE)
    length=int(.12*RATE)
    phase=0.0
    for j in range(length):
        i=s0+j
        if i>=len(buf): break
        t=j/RATE
        phase += 2*math.pi*(pitch*(1-.35*min(1,t/.09)))/RATE
        e=env_decay(t,.055)
        noise=(random.random()*2-1)*.34*e
        buf[i]+=amp*(.55*math.sin(phase)*e+noise)


def add_chirp(buf,start,amp=.13,base=420):
    s0=int(start*RATE)
    length=int(.18*RATE)
    phase=0.0
    for j in range(length):
        i=s0+j
        if i>=len(buf): break
        t=j/RATE
        f=base*(1+1.15*t/.18)
        phase += 2*math.pi*f/RATE
        e=env_decay(t,.075)
        buf[i]+=amp*math.sin(phase)*e


def make_variant(seed,pattern):
    random.seed(seed)
    n=int(RATE*DUR)
    buf=[0.0]*n
    for kind,t,amp in pattern:
        if kind=='L': add_low_dhol(buf,t,amp=amp,pitch=145+random.randint(-12,18),end=52+random.randint(0,12))
        elif kind=='H': add_high_dhol(buf,t,amp=amp,pitch=225+random.randint(-20,35))
        else: add_chirp(buf,t,amp=amp,base=390+random.randint(-25,70))
    peak=max(1e-6,max(abs(x) for x in buf))
    gain=.91/peak
    pcm=[]
    for x in buf:
        y=max(-1,min(1,x*gain))
        pcm.append(struct.pack('<h',int(y*32767)))
    return b''.join(pcm)

patterns=[
    [('L',0.00,.95),('H',.115,.54),('L',.245,.80),('C',.39,.12)],
    [('H',0.00,.62),('L',.075,.96),('H',.205,.48),('L',.335,.76)],
    [('L',0.00,.90),('L',.135,.72),('H',.265,.60),('C',.42,.15)],
    [('H',0.00,.55),('L',.055,1.0),('H',.17,.50),('L',.285,.78),('C',.47,.13)],
]

for i,pattern in enumerate(patterns,1):
    path=OUTDIR/f'india-dhol-{i}.wav'
    with wave.open(str(path),'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(make_variant(4200+i,pattern))

p=Path('index.html')
s=p.read_text(encoding='utf-8')

s=s.replace('SLAP! Mobile 3.5 · Bhangra SFX','SLAP! Mobile 3.6 · India Dhol Pack')
s=s.replace('<span class="ver">3.5</span>','<span class="ver">3.6</span>')
s=s.replace('SLAP! Mobile 3.5 · Bhangra SFX · CC0 · Background Audio · PWA','SLAP! Mobile 3.6 · India Dhol Pack · Original Audio · Background Audio · PWA')

if 'data-sound="indiaPerson"' not in s:
    old='<button class="preset" data-sound="desiChaos"><span>🎉</span>DESI CHAOS</button></div><div class="systemGestureNote">'
    new='<button class="preset" data-sound="desiChaos"><span>🎉</span>DESI CHAOS</button><button class="preset" data-sound="indiaPerson"><span>🇮🇳</span>印度人</button></div><div class="systemGestureNote">'
    if old not in s:
        raise SystemExit('Bhangra preset insertion point not found')
    s=s.replace(old,new,1)

if '印度人按鈕' not in s:
    marker='<div class="systemGestureNote"><b>聲音設計：</b>參考你提供影片的高能量旁遮普舞曲氣氛，使用原創 dhol 類鼓點、短促「HA / HEY / OI」非語詞人聲合成與音高滑動；不取樣原曲、不重製原旋律或歌詞。</div>'
    extra=marker+'<div class="systemGestureNote"><b>🇮🇳 印度人按鈕：</b>內建 4 個原創 Dhol 短擊 WAV，再疊加目前的 Bhangra 人聲／節奏合成；完全離線，不包含〈Tunak Tunak Tun〉原曲錄音。</div>'
    if marker in s:
        s=s.replace(marker,extra,1)

m=re.search(r'const sampleFiles=(\{.*?\});\nconst sampleBroken=',s,re.S)
if not m:
    raise SystemExit('sampleFiles object not found')
sample_files=json.loads(m.group(1))
sample_files['indiaPerson']=[f'./sounds/india/india-dhol-{i}.wav' for i in range(1,5)]
obj=json.dumps(sample_files,ensure_ascii=False,separators=(',',':'))
s=s[:m.start(1)]+obj+s[m.end(1):]

old_play="const promise=el.play();if(promise&&promise.catch)promise.catch(()=>{sampleBroken.add(src);synthSound(power,kind)});"
new_play="const promise=el.play();if(kind==='indiaPerson'){try{playBhangraStyle('bhangra',Math.max(7,power*.82))}catch(e){}}if(promise&&promise.catch)promise.catch(()=>{sampleBroken.add(src);synthSound(power,kind)});"
segment=s[s.find('function playSound'):s.find('let alarmInt')]
if old_play in s and "kind==='indiaPerson'" not in segment:
    s=s.replace(old_play,new_play,1)

p.write_text(s,encoding='utf-8')

mp=Path('manifest.webmanifest')
if mp.exists():
    md=json.loads(mp.read_text(encoding='utf-8'))
    md['name']='SLAP! Mobile 3.6'
    md['description']='手機動作感測遊戲與防盜警戒，內建人聲、原創印度 Dhol / Bhangra 音效、拍擊力度分級、挑戰模式與背景存活強化。'
    mp.write_text(json.dumps(md,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

swp=Path('sw.js')
if swp.exists():
    sw=swp.read_text(encoding='utf-8')
    sw=re.sub(r"const CACHE='[^']+';","const CACHE='slap-mobile-v8-india-dhol';",sw,count=1)
    am=re.search(r'const ASSETS=(\[.*?\]);',sw,re.S)
    if not am:
        raise SystemExit('Service worker ASSETS not found')
    assets=json.loads(am.group(1))
    assets=[x for x in assets if not x.startswith('./sounds/india/india-dhol-')]
    for i in range(1,5): assets.append(f'./sounds/india/india-dhol-{i}.wav')
    sw=sw[:am.start(1)]+json.dumps(assets,ensure_ascii=False)+sw[am.end(1):]
    swp.write_text(sw,encoding='utf-8')

Path('INDIA_AUDIO_LICENSE.md').write_text('''# India / Bhangra Audio Pack\n\nThe four files under `sounds/india/` are original synthesized Dhol-style effects generated by `tools/add_india_button.py` for this project.\n\nThey do **not** contain audio, melody, lyrics, or samples from Daler Mehndi's **Tunak Tunak Tun**. The app layers these original WAV files with the project's original Web Audio Bhangra-style synthesis.\n\nFor open-audio reference research, Freesound's **Indian Wedding Dhols** by `rsn267` is marked Creative Commons 0 (CC0), but that external recording is not bundled in this version.\n''',encoding='utf-8')
