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

ARCHIVE_URL='https://opengameart.org/sites/default/files/slightscreams.7z'
ARCHIVE_PAGE='https://opengameart.org/content/15-vocal-male-strainhurtpainjump-sounds'
HORROR_URL='https://opengameart.org/sites/default/files/scream_horror1_0.mp3'
HORROR_PAGE='https://opengameart.org/content/horror-scream1'


def download(url: str, dest: Path):
    req=Request(url,headers={'User-Agent':'Mozilla/5.0','Accept':'*/*'})
    with urlopen(req,timeout=90) as r:
        dest.write_bytes(r.read())


def convert_to_mp3(src: Path, dest: Path):
    filt=(
        'silenceremove=start_periods=1:start_silence=0.02:start_threshold=-42dB:'
        'stop_periods=1:stop_silence=0.06:stop_threshold=-42dB,'
        'highpass=f=70,lowpass=f=12000,loudnorm=I=-17:TP=-1.5:LRA=10'
    )
    subprocess.run([
        'ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(src),
        '-af',filt,'-ar','44100','-ac','1','-b:a','96k',str(dest)
    ],check=True)


VOICE_DIR.mkdir(parents=True,exist_ok=True)
for old in VOICE_DIR.glob('extra-*.mp3'):
    old.unlink()

# Download and extract CC0 male strain/hurt/pain voice pack.
archive=Path('/tmp/slightscreams.7z')
extract_dir=Path('/tmp/slightscreams')
if extract_dir.exists(): shutil.rmtree(extract_dir)
extract_dir.mkdir(parents=True)
download(ARCHIVE_URL,archive)
subprocess.run(['7z','x','-y',f'-o{extract_dir}',str(archive)],check=True,stdout=subprocess.DEVNULL)

exts={'.wav','.ogg','.mp3','.flac','.aiff','.aif'}
sources=sorted([p for p in extract_dir.rglob('*') if p.is_file() and p.suffix.lower() in exts])
if not sources:
    raise SystemExit('No audio files extracted from slightscreams.7z')

male_extra=[]
for i,src in enumerate(sources,1):
    out=VOICE_DIR/f'extra-male-{i:02d}.mp3'
    convert_to_mp3(src,out)
    male_extra.append('./'+out.as_posix())

# Download one additional CC0 human-like horror/pain scream and normalize it.
horror_raw=Path('/tmp/scream_horror1.mp3')
download(HORROR_URL,horror_raw)
horror_out=VOICE_DIR/'extra-horror-01.mp3'
convert_to_mp3(horror_raw,horror_out)
horror='./'+horror_out.as_posix()

# Remove the previous India/Bhangra generated audio assets.
india_dir=ROOT/'sounds'/'india'
if india_dir.exists(): shutil.rmtree(india_dir)
for f in ['INDIA_AUDIO_LICENSE.md']:
    p=ROOT/f
    if p.exists(): p.unlink()

s=INDEX.read_text(encoding='utf-8')

# Version and copy.
s=s.replace('SLAP! Mobile 3.7 · India Hit Chant','SLAP! Mobile 3.8 · Human Hit Pack II')
s=s.replace('<span class="ver">3.7</span>','<span class="ver">3.8</span>')
s=s.replace('SLAP! Mobile 3.7 · India Hit Chant · CC0 · Background Audio · PWA','SLAP! Mobile 3.8 · Human Hit Pack II · CC0 · Background Audio · PWA')
s=s.replace('CC0 VOICE PACK','CC0 VOICE PACK · 50+ CLIPS')

# Remove the full Bhangra/India UI card.
s=re.sub(
    r'\n<div class="card" id="bhangraSfx">.*?</div>\n</section>\n<section class="view" id="gameView">',
    '\n</section>\n<section class="view" id="gameView">',
    s,flags=re.S,count=1
)

# Remove Bhangra synthesis helper block while preserving the regular physical SFX synth.
s=re.sub(r'\nfunction drumNoise\(.*?\nconst sampleFiles=', '\nconst sampleFiles=', s, flags=re.S, count=1)

# Update voice sample registry.
m=re.search(r'const sampleFiles=(\{.*?\});\nconst sampleBroken=',s,re.S)
if not m:
    raise SystemExit('sampleFiles object not found')
sample_files=json.loads(m.group(1))
sample_files.pop('indiaPerson',None)

# Preserve existing order and append only if missing.
def extend_unique(key, vals):
    arr=sample_files.setdefault(key,[])
    for v in vals:
        if v not in arr: arr.append(v)

extend_unique('human',male_extra+[horror])
extend_unique('humanMale',male_extra)
extend_unique('humanShort',male_extra[:min(10,len(male_extra))])
extend_unique('humanYell',male_extra[-min(5,len(male_extra)):] + [horror])
extend_unique('humanHeavy',male_extra[-min(7,len(male_extra)):] + [horror])
obj=json.dumps(sample_files,ensure_ascii=False,separators=(',',':'))
s=s[:m.start(1)]+obj+s[m.end(1):]

# Remove any old Bhangra/India play hooks that may still remain.
s=s.replace("if(kind==='bhangra'||kind==='dhol'||kind==='festival'||kind==='desiChaos'){playBhangraStyle(kind,power);return}","")
s=s.replace("if(kind==='indiaPerson'){try{playBhangraStyle('bhangra',Math.max(7,power*.82))}catch(e){}}","")

# Make random selection avoid immediate repeats for a more natural hit reaction pool.
old="const sampleBroken=new Set();\nfunction samplePath(kind,power){const arr=sampleFiles[kind];if(!arr||!arr.length)return null;if(kind==='slap'){const r=power/state.threshold;return arr[r<1.3?0:r<1.9?1:2]}return arr[Math.floor(Math.random()*arr.length)]}"
new="const sampleBroken=new Set(),lastSampleByKind={};\nfunction samplePath(kind,power){const arr=sampleFiles[kind];if(!arr||!arr.length)return null;if(kind==='slap'){const r=power/state.threshold;return arr[r<1.3?0:r<1.9?1:2]}let pick=arr[Math.floor(Math.random()*arr.length)];if(arr.length>1){for(let i=0;i<5&&pick===lastSampleByKind[kind];i++)pick=arr[Math.floor(Math.random()*arr.length)]}lastSampleByKind[kind]=pick;return pick}"
if old in s:
    s=s.replace(old,new,1)

# Add a concise source note under the voice card if absent.
voice_marker='<div class="row"><div class="rowText"><b>人聲隨機化</b><small>每次有效拍擊從目前分類隨機抽一個聲音，並加入輕微音高差異，避免一直重複同一聲。</small></div><button class="mini" id="voiceTest">試聽人聲</button></div></div>'
if voice_marker in s and '新增 CC0 人聲' not in s:
    note='<div class="systemGestureNote"><b>新增 CC0 人聲：</b>加入更多男性受傷／吃力／疼痛短聲與一組額外慘叫；已移除上一版 Dhol、唱段與印度主題合成音，只保留真人受擊聲。</div>'
    s=s.replace(voice_marker,voice_marker[:-6]+note+'</div>',1)

if 'indiaPerson' in s or 'playBhangraStyle' in s or 'id="bhangraSfx"' in s:
    raise SystemExit('India/Bhangra remnants still present in index.html')
INDEX.write_text(s,encoding='utf-8')

# Manifest.
if MANIFEST.exists():
    md=json.loads(MANIFEST.read_text(encoding='utf-8'))
    md['name']='SLAP! Mobile 3.8'
    md['description']='手機動作感測遊戲與防盜警戒，內建 50+ CC0 真人受擊、疼痛、悶哼與慘叫音效，支援背景音訊強化、力度分級與挑戰模式。'
    MANIFEST.write_text(json.dumps(md,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

# Service worker cache: drop India assets, include the new MP3s.
if SW.exists():
    sw=SW.read_text(encoding='utf-8')
    sw=re.sub(r"const CACHE='[^']+';","const CACHE='slap-mobile-v10-human-voices';",sw,count=1)
    am=re.search(r'const ASSETS=(\[.*?\]);',sw,re.S)
    if not am: raise SystemExit('Service worker ASSETS not found')
    assets=json.loads(am.group(1))
    assets=[a for a in assets if '/sounds/india/' not in a]
    for f in male_extra+[horror]:
        if f not in assets: assets.append(f)
    sw=sw[:am.start(1)]+json.dumps(assets,ensure_ascii=False)+sw[am.end(1):]
    SW.write_text(sw,encoding='utf-8')

# Source/license record.
Path('HUMAN_AUDIO_SOURCES_2.md').write_text(f'''# Additional Human Hit Voice Sources\n\nAll assets added by this upgrade are used from OpenGameArt pages that display **CC0** licensing.\n\n## 15 vocal male strain/hurt/pain/jump sounds\n- Author: qubodup\n- Source page: {ARCHIVE_PAGE}\n- Source archive: {ARCHIVE_URL}\n- License displayed on source page: CC0\n- Local derivative files: `sounds/voices/extra-male-*.mp3`\n- Processing: trim leading/trailing silence, mono, high/low-pass cleanup, loudness normalization, MP3 conversion.\n\n## Horror scream1\n- Author: Vinrax\n- Source page: {HORROR_PAGE}\n- Source file: {HORROR_URL}\n- License displayed on source page: CC0\n- Local derivative file: `sounds/voices/extra-horror-01.mp3`\n- Processing: trim leading/trailing silence, mono, high/low-pass cleanup, loudness normalization, MP3 conversion.\n\nNo Daler Mehndi / Tunak Tunak Tun audio, melody, or derived song recording is included. The previous generated India/Dhol/chant assets were removed in this upgrade.\n''',encoding='utf-8')

print(f'Added {len(male_extra)} extra male CC0 voice clips + 1 horror scream')
