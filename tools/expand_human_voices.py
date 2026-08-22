from pathlib import Path
from urllib.request import Request, urlopen
import json
import re
import shutil
import subprocess

ROOT=Path('.')
INDEX=ROOT/'index.html'
MANIFEST=ROOT/'manifest.webmanifest'
SW=ROOT/'sw.js'
VOICE_DIR=ROOT/'sounds'/'voices'
RAW_BASE='https://raw.githubusercontent.com/Wh1teDuke/WilhelmSFX/master/Samples'
SOURCE_REPO='https://github.com/Wh1teDuke/WilhelmSFX'

MALE_SCREAM=[
 '759458__akridiy__a-single-scream-of-a-young-male',
 '523216__feed__death-scream',
 '219719__mariateresa_garcia__man-screaming',
 '813310__qubodup__victim-screaming',
 '222648__mariallinas__wild-scream',
 '813308__qubodup__wilhelm-scream',
]
MALE_AGONY=[
 '272023__aldenroth2__male-scream',
 '823508__riippumattog__pain-yell-male',
 '267480__islandan__male-scream',
 '546123__pepsimanfan__young-man-being-hurt',
 '528839__th3romeo__human-roar-1',
 '265554__augustsandberg__studio-roar',
]
MALE_GRUNT=[
 '416838__tonsil5__grunt2-death-pain',
 '416839__tonsil5__grunt1-death-pain',
 '90164__snaginneb__gruntsound',
 '547209__mrfossy__voice_adultmale_paingrunts_09',
 '166944__qubodup__grunts-of-pain-by-military-soldiers_a',
 '166944__qubodup__grunts-of-pain-by-military-soldiers_b',
]
FEMALE_SCREAM=[
 '400183__tomattka__girl-screaming_01',
 '235592__tcrocker68__girl_scream',
 '169811__missozzy__female-scream-02',
 '344013__reitanna__high-pitched-ah2',
 '235595__tcrocker68__girl_two_screams_a',
 '235595__tcrocker68__girl_two_screams_b',
 '625318__darknightprincess__female-startled-scream-sound-effect-voiced-by-darknightprincess',
]
FEMALE_AGONY=[
 '219656__annatabernero__young-girl-scream',
 '220644__ritola27__grito_mujer2',
]
FEMALE_GRUNT=[
 '344004__reitanna__heavy-grunt',
 '218908__martian__female-grunts-breaths_a',
 '218908__martian__female-grunts-breaths_b',
]


def download(url: str, dest: Path):
    req=Request(url,headers={'User-Agent':'Mozilla/5.0','Accept':'*/*'})
    with urlopen(req,timeout=90) as r:
        dest.write_bytes(r.read())


def convert_to_mp3(src: Path, dest: Path):
    filt=(
        'silenceremove=start_periods=1:start_silence=0.015:start_threshold=-44dB:'
        'stop_periods=1:stop_silence=0.05:stop_threshold=-44dB,'
        'highpass=f=65,lowpass=f=12500,loudnorm=I=-16:TP=-1.3:LRA=9'
    )
    subprocess.run([
        'ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(src),
        '-af',filt,'-ar','44100','-ac','1','-b:a','96k',str(dest)
    ],check=True)


def vendor_group(prefix, names):
    out=[]
    for i,name in enumerate(names,1):
        raw=Path('/tmp')/(name+'.wav')
        download(f'{RAW_BASE}/{name}.wav',raw)
        dest=VOICE_DIR/f'wilhelm-{prefix}-{i:02d}.mp3'
        convert_to_mp3(raw,dest)
        out.append('./'+dest.as_posix())
    return out


VOICE_DIR.mkdir(parents=True,exist_ok=True)
for pat in ['extra-*.mp3','wilhelm-*.mp3']:
    for old in VOICE_DIR.glob(pat): old.unlink()

male_scream=vendor_group('male-scream',MALE_SCREAM)
male_agony=vendor_group('male-agony',MALE_AGONY)
male_grunt=vendor_group('male-grunt',MALE_GRUNT)
female_scream=vendor_group('female-scream',FEMALE_SCREAM)
female_agony=vendor_group('female-agony',FEMALE_AGONY)
female_grunt=vendor_group('female-grunt',FEMALE_GRUNT)
all_new=male_scream+male_agony+male_grunt+female_scream+female_agony+female_grunt

# Remove previous India/Bhangra generated audio assets and license note.
india_dir=ROOT/'sounds'/'india'
if india_dir.exists(): shutil.rmtree(india_dir)
for f in ['INDIA_AUDIO_LICENSE.md']:
    p=ROOT/f
    if p.exists(): p.unlink()

s=INDEX.read_text(encoding='utf-8')

# Version labels (handles either 3.7 source or an already-partially-upgraded 3.8 page).
s=s.replace('SLAP! Mobile 3.7 · India Hit Chant','SLAP! Mobile 3.8 · Human Hit Pack II')
s=s.replace('<span class="ver">3.7</span>','<span class="ver">3.8</span>')
s=s.replace('SLAP! Mobile 3.7 · India Hit Chant · CC0 · Background Audio · PWA','SLAP! Mobile 3.8 · Human Hit Pack II · CC0 · Background Audio · PWA')
s=s.replace('CC0 VOICE PACK · 50+ CLIPS','CC0 VOICE PACK · 60+ CLIPS')
s=s.replace('CC0 VOICE PACK','CC0 VOICE PACK · 60+ CLIPS')

# Remove the Bhangra / India UI card.
s=re.sub(
    r'\n<div class="card" id="bhangraSfx">.*?</div>\n</section>\n<section class="view" id="gameView">',
    '\n</section>\n<section class="view" id="gameView">',
    s,flags=re.S,count=1
)

# Remove the Bhangra synthesis helper block while preserving regular SFX synth functions.
s=re.sub(r'\nfunction drumNoise\(.*?\nconst sampleFiles=', '\nconst sampleFiles=', s, flags=re.S, count=1)

m=re.search(r'const sampleFiles=(\{.*?\});\nconst sampleBroken=',s,re.S)
if not m:
    raise SystemExit('sampleFiles object not found')
sample_files=json.loads(m.group(1))
sample_files.pop('indiaPerson',None)

# Drop stale files from the prior failed/experimental expansion if they exist in arrays.
for key,arr in list(sample_files.items()):
    sample_files[key]=[v for v in arr if '/extra-' not in v and '/sounds/india/' not in v and '/wilhelm-' not in v]

def extend_unique(key, vals):
    arr=sample_files.setdefault(key,[])
    for v in vals:
        if v not in arr: arr.append(v)

extend_unique('human',all_new)
extend_unique('humanMale',male_scream+male_agony+male_grunt)
extend_unique('humanFemale',female_scream+female_agony+female_grunt)
extend_unique('humanShort',male_grunt+female_grunt)
extend_unique('humanYell',male_scream+male_agony+female_scream+female_agony)
extend_unique('humanHeavy',male_agony+female_agony+male_grunt[-2:]+female_grunt[:1])
obj=json.dumps(sample_files,ensure_ascii=False,separators=(',',':'))
s=s[:m.start(1)]+obj+s[m.end(1):]

# Remove old India/Bhangra hooks if present.
s=s.replace("if(kind==='bhangra'||kind==='dhol'||kind==='festival'||kind==='desiChaos'){playBhangraStyle(kind,power);return}","")
s=s.replace("if(kind==='indiaPerson'){try{playBhangraStyle('bhangra',Math.max(7,power*.82))}catch(e){}}","")

# Avoid immediate sample repetition.
old="const sampleBroken=new Set();\nfunction samplePath(kind,power){const arr=sampleFiles[kind];if(!arr||!arr.length)return null;if(kind==='slap'){const r=power/state.threshold;return arr[r<1.3?0:r<1.9?1:2]}return arr[Math.floor(Math.random()*arr.length)]}"
new="const sampleBroken=new Set(),lastSampleByKind={};\nfunction samplePath(kind,power){const arr=sampleFiles[kind];if(!arr||!arr.length)return null;if(kind==='slap'){const r=power/state.threshold;return arr[r<1.3?0:r<1.9?1:2]}let pick=arr[Math.floor(Math.random()*arr.length)];if(arr.length>1){for(let i=0;i<5&&pick===lastSampleByKind[kind];i++)pick=arr[Math.floor(Math.random()*arr.length)]}lastSampleByKind[kind]=pick;return pick}"
if old in s: s=s.replace(old,new,1)

# Refresh the human voice explanatory note.
s=re.sub(r'<div class="systemGestureNote"><b>新增 CC0 人聲：</b>.*?</div>','',s,flags=re.S)
voice_end='<div class="row"><div class="rowText"><b>人聲隨機化</b><small>每次有效拍擊從目前分類隨機抽一個聲音，並加入輕微音高差異，避免一直重複同一聲。</small></div><button class="mini" id="voiceTest">試聽人聲</button></div></div>'
if voice_end in s:
    note='<div class="systemGestureNote"><b>新增 CC0 真人聲：</b>再加入 30 個男性／女性慘叫、疼痛、Agony 與短促悶哼；已移除 Dhol、唱段與印度主題合成音。RANDOM HUMAN 會從完整聲庫抽樣，且避免連續重複同一檔。</div>'
    s=s.replace(voice_end,voice_end[:-6]+note+'</div>',1)

if 'indiaPerson' in s or 'playBhangraStyle' in s or 'id="bhangraSfx"' in s:
    raise SystemExit('India/Bhangra remnants still present')
INDEX.write_text(s,encoding='utf-8')

# Manifest.
if MANIFEST.exists():
    md=json.loads(MANIFEST.read_text(encoding='utf-8'))
    md['name']='SLAP! Mobile 3.8'
    md['description']='手機動作感測遊戲與防盜警戒，內建 60+ 真人受擊、疼痛、悶哼與慘叫音效，支援背景音訊強化、力度分級與挑戰模式。'
    MANIFEST.write_text(json.dumps(md,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

# Service worker cache.
if SW.exists():
    sw=SW.read_text(encoding='utf-8')
    sw=re.sub(r"const CACHE='[^']+';","const CACHE='slap-mobile-v10-human-voices';",sw,count=1)
    am=re.search(r'const ASSETS=(\[.*?\]);',sw,re.S)
    if not am: raise SystemExit('Service worker ASSETS not found')
    assets=json.loads(am.group(1))
    assets=[a for a in assets if '/sounds/india/' not in a and '/extra-' not in a and '/wilhelm-' not in a]
    for f in all_new:
        if f not in assets: assets.append(f)
    sw=sw[:am.start(1)]+json.dumps(assets,ensure_ascii=False)+sw[am.end(1):]
    SW.write_text(sw,encoding='utf-8')

# Source/license record.
Path('HUMAN_AUDIO_SOURCES_2.md').write_text(f'''# Additional Human Hit Voice Sources\n\n## WilhelmSFX CC0 sound bank\n- Repository: {SOURCE_REPO}\n- Repository license: CC0 1.0 Universal\n- Selected categories: Male Scream, Male Agony, Male Grunt, Female Scream, Female Agony, Female Grunt\n- Added local derivatives: `sounds/voices/wilhelm-*.mp3`\n- Count added by this upgrade: {len(all_new)}\n- Processing: trim leading/trailing silence, mono conversion, high/low-pass cleanup, loudness normalization, MP3 conversion for iPhone/web compatibility.\n\nSelected source stems:\n'''+''.join(f'- `{x}`\n' for x in MALE_SCREAM+MALE_AGONY+MALE_GRUNT+FEMALE_SCREAM+FEMALE_AGONY+FEMALE_GRUNT)+'''\nThe previous generated India/Dhol/chant assets are removed. No song, melody, Dhol layer, or synthetic chant is included in the human hit preset.\n''',encoding='utf-8')

print(f'Added {len(all_new)} human voice clips from WilhelmSFX')
