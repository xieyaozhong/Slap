from pathlib import Path
import json, math, random, re, struct, wave

RATE=44100
OUTDIR=Path('sounds/india')
OUTDIR.mkdir(parents=True,exist_ok=True)

# Original, non-infringing pitch shapes. The repeated "du" syllables are generic vocal syllables,
# not a transcription of Tunak Tunak Tun or any other copyrighted melody.
PATTERNS=[
    [196,233,208,262],
    [185,220,247,208],
    [208,247,220,294],
    [174,208,233,196],
]


def env(t,dur,attack=.015,release=.08):
    if t<0 or t>=dur: return 0.0
    if t<attack: return t/attack
    if t>dur-release: return max(0.0,(dur-t)/release)
    return 1.0


def add_tone(buf,start,dur,freq,amp=.25,harmonics=(1,.45,.22,.12),slide=1.0):
    s0=int(start*RATE); n=int(dur*RATE)
    phase=0.0
    for i in range(n):
        t=i/RATE
        f=freq*(1+(slide-1)*(t/dur))
        phase += 2*math.pi*f/RATE
        x=0.0
        for h,a in enumerate(harmonics,1):
            x += a*math.sin(phase*h)
        x*=amp*env(t,dur)
        j=s0+i
        if 0<=j<len(buf): buf[j]+=x


def add_du(buf,start,freq,amp=.28):
    dur=.18
    s0=int(start*RATE); n=int(dur*RATE)
    phase=0.0
    for i in range(n):
        t=i/RATE
        # slight pitch rise gives a sung syllable feel without copying any known tune
        f=freq*(1+0.025*math.sin(math.pi*t/dur))
        phase += 2*math.pi*f/RATE
        # harmonic-rich glottal source + darker "u"-like spectral emphasis
        src=(math.sin(phase)+.48*math.sin(2*phase)+.22*math.sin(3*phase)+.10*math.sin(4*phase))
        wob=1+.035*math.sin(2*math.pi*5.2*t)
        x=src*wob*amp*env(t,dur,.012,.055)
        j=s0+i
        if 0<=j<len(buf): buf[j]+=x


def add_dhol(buf,start,pitch=78,amp=.42):
    dur=.22; s0=int(start*RATE); n=int(dur*RATE)
    phase=0.0
    rng=random.Random(int(start*1000)+int(pitch*10))
    for i in range(n):
        t=i/RATE
        f=pitch*(1.9-1.15*(t/dur))
        phase += 2*math.pi*max(35,f)/RATE
        body=math.sin(phase)*math.exp(-t*15)
        click=(rng.random()*2-1)*math.exp(-t*70)*.35
        x=(body+click)*amp
        j=s0+i
        if 0<=j<len(buf): buf[j]+=x


def make_reaction(path,pattern,variant):
    total=1.62
    buf=[0.0]*int(total*RATE)
    # hit + shouted reaction
    add_dhol(buf,0.0,70+variant*4,.48)
    add_tone(buf,.025,.20,128+variant*7,.32,(1,.65,.32,.18),slide=1.28)
    # original sung du-du-du phrase
    starts=[.30,.52,.74,.96]
    for st,f in zip(starts,pattern):
        add_du(buf,st,f,.30)
        add_dhol(buf,st+.015,96+(f%45),.18)
    # energetic final answer + drum tail
    add_tone(buf,1.18,.20,156+variant*8,.20,(1,.38,.16),slide=.86)
    add_dhol(buf,1.20,74+variant*3,.44)
    add_dhol(buf,1.39,104+variant*3,.28)
    peak=max(1e-9,max(abs(x) for x in buf))
    scale=.92/peak
    pcm=[max(-32767,min(32767,int(x*scale*32767))) for x in buf]
    with wave.open(str(path),'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(RATE)
        w.writeframes(b''.join(struct.pack('<h',x) for x in pcm))

for i,pat in enumerate(PATTERNS,1):
    make_reaction(OUTDIR/f'india-reaction-{i}.wav',pat,i)

p=Path('index.html')
s=p.read_text(encoding='utf-8')
s=s.replace('SLAP! Mobile 3.6 · India Dhol Pack','SLAP! Mobile 3.7 · India Hit Chant')
s=s.replace('<span class="ver">3.6</span>','<span class="ver">3.7</span>')
s=s.replace('SLAP! Mobile 3.6 · India Dhol Pack · CC0 · Background Audio · PWA','SLAP! Mobile 3.7 · India Hit Chant · Background Audio · PWA')
s=s.replace('內建 4 個原創 Dhol 短擊 WAV，再疊加目前的 Bhangra 人聲／節奏合成；完全離線，不包含〈Tunak Tunak Tun〉原曲錄音。','每次有效拍擊會先「叫一聲」，接著唱一段明顯的原創「嘟・嘟・嘟・嘟」短句，再用 Dhol 收尾；共 4 種變化隨機抽取。保留你要的喜劇節奏感，但不重製〈Tunak Tunak Tun〉的旋律。')

m=re.search(r'const sampleFiles=(\{.*?\});\nconst sampleBroken=',s,re.S)
if not m: raise SystemExit('sampleFiles object not found')
files=json.loads(m.group(1))
files['indiaPerson']=[f'./sounds/india/india-reaction-{i}.wav' for i in range(1,5)]
obj=json.dumps(files,ensure_ascii=False,separators=(',',':'))
s=s[:m.start(1)]+obj+s[m.end(1):]

# The WAV already contains shout + chant + drums, so avoid double-layering the old Bhangra synth.
s=s.replace("if(kind==='indiaPerson'){try{playBhangraStyle('bhangra',Math.max(7,power*.82))}catch(e){}}","")

# If the local WAV ever fails, provide a procedural fallback with the same interaction shape.
old="function synthSound(power=10,kind=state.sound){if(kind==='bhangra'||kind==='dhol'||kind==='festival'||kind==='desiChaos'){playBhangraStyle(kind,power);return}"
new="function synthSound(power=10,kind=state.sound){if(kind==='indiaPerson'){const p=Math.max(.7,Math.min(1.35,power/13));vocalBurst(p,'a',0,true);dholHit(p,.02,false);[0,.16,.32,.48].forEach((d,i)=>{vocalBurst(p*.78,i%2?'u':'o',.26+d,true);dholHit(p*.36,.28+d,i%2===0)});return}if(kind==='bhangra'||kind==='dhol'||kind==='festival'||kind==='desiChaos'){playBhangraStyle(kind,power);return}"
if old in s:
    s=s.replace(old,new,1)

p.write_text(s,encoding='utf-8')

mp=Path('manifest.webmanifest')
if mp.exists():
    md=json.loads(mp.read_text(encoding='utf-8'))
    md['name']='SLAP! Mobile 3.7'
    md['description']='手機動作感測遊戲，內建人聲、印度 Dhol 與原創 du-du-du 受擊唱段、挑戰模式、Touch Guard 與 iPhone 背景存活強化。'
    mp.write_text(json.dumps(md,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

swp=Path('sw.js')
if swp.exists():
    sw=swp.read_text(encoding='utf-8')
    sw=re.sub(r"const CACHE='[^']+';","const CACHE='slap-mobile-v9-india-hit-chant';",sw,count=1)
    am=re.search(r'const ASSETS=(\[.*?\]);',sw,re.S)
    if not am: raise SystemExit('ASSETS not found')
    assets=json.loads(am.group(1))
    assets=[a for a in assets if 'sounds/india/india-dhol-' not in a]
    for i in range(1,5):
        f=f'./sounds/india/india-reaction-{i}.wav'
        if f not in assets: assets.append(f)
    sw=sw[:am.start(1)]+json.dumps(assets,ensure_ascii=False)+sw[am.end(1):]
    swp.write_text(sw,encoding='utf-8')

lic=Path('INDIA_AUDIO_LICENSE.md')
lic.write_text('''# India Hit Chant Audio Pack\n\nThe `印度人` preset uses four **original procedurally generated** WAV files created for this project:\n\n- `sounds/india/india-reaction-1.wav`\n- `sounds/india/india-reaction-2.wav`\n- `sounds/india/india-reaction-3.wav`\n- `sounds/india/india-reaction-4.wav`\n\nEach file follows the interaction pattern: impact → short vocal exclamation → original repeated “du” syllable chant → Dhol-style drum ending.\n\nThe pitch patterns and synthesis are original and are **not a transcription, sample, or recreation of Daler Mehndi's “Tunak Tunak Tun.”** No recording from that song is bundled.\n''',encoding='utf-8')
