from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen
import json
import re
import shutil
import subprocess

ROOT = Path('.')
INDEX = ROOT / 'index.html'
MANIFEST = ROOT / 'manifest.webmanifest'
SW = ROOT / 'sw.js'
VOICE_DIR = ROOT / 'sounds' / 'voices'
SOURCE_REPO = 'https://github.com/Wh1teDuke/WilhelmSFX'
TREE_API = 'https://api.github.com/repos/Wh1teDuke/WilhelmSFX/git/trees/master?recursive=1'
RAW_ROOT = 'https://raw.githubusercontent.com/Wh1teDuke/WilhelmSFX/master/'
TARGET_NEW = 30
MIN_NEW = 24

INCLUDE = (
    'scream', 'screaming', 'grunt', 'grunts', 'groan', 'pain',
    'hurt', 'agony', 'yell', 'gasp', 'ouch'
)
EXCLUDE = (
    'animal', 'dog', 'cat', 'wolf', 'horse', 'pig', 'bird', 'bear',
    'zombie', 'monster', 'mutant', 'demon', 'orc', 'creature', 'dinosaur', 'dragon', 'alien',
    'ghost', 'robot', 'engine', 'car_', 'tire', 'metal', 'music',
    'song', 'guitar', 'synth', 'gun', 'rifle', 'explosion'
)
FEMALE_MARKERS = ('female', 'girl', 'woman', 'mujer', 'lady')
MALE_MARKERS = ('male', 'man-', '_man', 'young-man', 'boy', 'soldier', 'military')
AUDIO_EXT = {'.wav', '.ogg', '.mp3', '.flac', '.aif', '.aiff'}


def request_bytes(url: str) -> bytes:
    req = Request(url, headers={
        'User-Agent': 'SLAP-Mobile-CC0-Vendor/3.8',
        'Accept': '*/*',
    })
    with urlopen(req, timeout=90) as response:
        return response.read()


def fetch_tree():
    return json.loads(request_bytes(TREE_API).decode('utf-8'))['tree']


def classify(path: str) -> str:
    text = path.lower()
    if any(k in text for k in FEMALE_MARKERS):
        return 'female'
    if any(k in text for k in MALE_MARKERS):
        return 'male'
    return 'hurt'


def relevance(path: str) -> tuple:
    text = path.lower()
    strong = sum(k in text for k in ('pain', 'hurt', 'agony', 'grunt', 'groan'))
    scream = sum(k in text for k in ('scream', 'screaming', 'yell', 'ouch'))
    gender = 1 if classify(path) != 'hurt' else 0
    return (-strong, -scream, -gender, text)


def discover_candidates():
    candidates = []
    for item in fetch_tree():
        if item.get('type') != 'blob':
            continue
        path = item.get('path', '')
        if not path.startswith('Samples/') or Path(path).suffix.lower() not in AUDIO_EXT:
            continue
        text = path.lower()
        if not any(k in text for k in INCLUDE):
            continue
        if any(k in text for k in EXCLUDE):
            continue
        candidates.append(path)

    candidates = sorted(set(candidates), key=relevance)
    female = [p for p in candidates if classify(p) == 'female']
    male = [p for p in candidates if classify(p) == 'male']
    hurt = [p for p in candidates if classify(p) == 'hurt']

    # Put a balanced set first, then leave all remaining candidates as fallbacks.
    ordered = female[:10] + male[:12] + hurt[:8]
    ordered += [p for p in candidates if p not in ordered]
    return ordered


def convert_to_mp3(src: Path, dest: Path):
    filt = (
        'silenceremove=start_periods=1:start_silence=0.015:start_threshold=-44dB:'
        'stop_periods=1:stop_silence=0.05:stop_threshold=-44dB,'
        'highpass=f=65,lowpass=f=12500,loudnorm=I=-16:TP=-1.3:LRA=9'
    )
    subprocess.run([
        'ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', str(src),
        '-af', filt, '-ar', '44100', '-ac', '1', '-b:a', '96k', str(dest)
    ], check=True)


def vendor_voices():
    VOICE_DIR.mkdir(parents=True, exist_ok=True)
    for pattern in ('extra-*.mp3', 'wilhelm-*.mp3'):
        for old in VOICE_DIR.glob(pattern):
            old.unlink()

    temp_dir = Path('/tmp/slap-wilhelm')
    temp_dir.mkdir(parents=True, exist_ok=True)
    counters = {'female': 0, 'male': 0, 'hurt': 0}
    groups = {'female': [], 'male': [], 'hurt': []}
    sources = []

    for path in discover_candidates():
        if len(sources) >= TARGET_NEW:
            break
        group = classify(path)
        raw = temp_dir / Path(path).name
        try:
            raw.write_bytes(request_bytes(RAW_ROOT + quote(path, safe='/')))
            counters[group] += 1
            dest = VOICE_DIR / f'wilhelm-{group}-{counters[group]:02d}.mp3'
            convert_to_mp3(raw, dest)
            rel = './' + dest.as_posix()
            groups[group].append(rel)
            sources.append(path)
            print(f'added {group}: {path}')
        except Exception as exc:
            counters[group] -= 1
            print(f'skip {path}: {exc}')
            if 'dest' in locals() and dest.exists():
                dest.unlink()

    if len(sources) < MIN_NEW:
        raise SystemExit(f'Only {len(sources)} CC0 human clips converted; require at least {MIN_NEW}')
    return groups, sources


groups, selected_sources = vendor_voices()
female_new = groups['female']
male_new = groups['male']
hurt_new = groups['hurt']
all_new = female_new + male_new + hurt_new

# Remove the previous India/Bhangra assets and generated license note.
india_dir = ROOT / 'sounds' / 'india'
if india_dir.exists():
    shutil.rmtree(india_dir)
for name in ('INDIA_AUDIO_LICENSE.md',):
    p = ROOT / name
    if p.exists():
        p.unlink()

s = INDEX.read_text(encoding='utf-8')

# Version labels.
s = s.replace('SLAP! Mobile 3.7 · India Hit Chant', 'SLAP! Mobile 3.8 · Human Hit Pack II')
s = s.replace('<span class="ver">3.7</span>', '<span class="ver">3.8</span>')
s = s.replace('SLAP! Mobile 3.7 · India Hit Chant · CC0 · Background Audio · PWA',
              'SLAP! Mobile 3.8 · Human Hit Pack II · CC0 · Background Audio · PWA')

# Remove the complete India/Bhangra UI card.
s = re.sub(
    r'\n<div class="card" id="bhangraSfx">.*?</div>\n</section>\n<section class="view" id="gameView">',
    '\n</section>\n<section class="view" id="gameView">',
    s, flags=re.S, count=1
)

# Remove the dedicated Dhol/chant synthesis helper block.
if 'function drumNoise(' in s:
    s = re.sub(r'\nfunction drumNoise\(.*?\nconst sampleFiles=',
               '\nconst sampleFiles=', s, flags=re.S, count=1)

# Parse the existing JSON-compatible audio map.
m = re.search(r'const sampleFiles=(\{.*?\});\nconst sampleBroken=', s, re.S)
if not m:
    raise SystemExit('sampleFiles object not found')
sample_files = json.loads(m.group(1))
sample_files.pop('indiaPerson', None)

# Clear stale expansion paths before rebuilding arrays.
for key, arr in list(sample_files.items()):
    sample_files[key] = [
        v for v in arr
        if '/extra-' not in v and '/sounds/india/' not in v and '/wilhelm-' not in v
    ]


def extend_unique(key, values):
    arr = sample_files.setdefault(key, [])
    for value in values:
        if value not in arr:
            arr.append(value)


extend_unique('human', all_new)
extend_unique('humanMale', male_new + hurt_new)
extend_unique('humanFemale', female_new)
extend_unique('humanShort', hurt_new + male_new[-3:] + female_new[-2:])
extend_unique('humanYell', male_new + female_new + hurt_new[:4])
extend_unique('humanHeavy', hurt_new + male_new[:4] + female_new[:3])

total_human = len(sample_files.get('human', []))
obj = json.dumps(sample_files, ensure_ascii=False, separators=(',', ':'))
s = s[:m.start(1)] + obj + s[m.end(1):]

# Remove India/Bhangra-only code from synthSound even when formatting changes.
start = "function synthSound(power=10,kind=state.sound){"
body_start = 'const p=Math.min(1.5,Math.max(.45,power/14));'
si = s.find(start)
bi = s.find(body_start, si + len(start)) if si >= 0 else -1
if si >= 0 and bi >= 0:
    s = s[:si] + start + s[bi:]

# Avoid immediate sample repetition for every random preset.
old = "const sampleBroken=new Set();\nfunction samplePath(kind,power){const arr=sampleFiles[kind];if(!arr||!arr.length)return null;if(kind==='slap'){const r=power/state.threshold;return arr[r<1.3?0:r<1.9?1:2]}return arr[Math.floor(Math.random()*arr.length)]}"
new = "const sampleBroken=new Set(),lastSampleByKind={};\nfunction samplePath(kind,power){const arr=sampleFiles[kind];if(!arr||!arr.length)return null;if(kind==='slap'){const r=power/state.threshold;return arr[r<1.3?0:r<1.9?1:2]}let pick=arr[Math.floor(Math.random()*arr.length)];if(arr.length>1){for(let i=0;i<5&&pick===lastSampleByKind[kind];i++)pick=arr[Math.floor(Math.random()*arr.length)]}lastSampleByKind[kind]=pick;return pick}"
if old in s:
    s = s.replace(old, new, 1)

# Update the visible pack count with the actual number successfully bundled.
s = re.sub(r'CC0 VOICE PACK(?: · \d+\+? CLIPS)?', f'CC0 VOICE PACK · {total_human} CLIPS', s)
note = (
    f'<div class="systemGestureNote" id="humanPackNote"><b>CC0 真人聲擴充：</b>'
    f'目前內建 {total_human} 個真人受擊／疼痛／慘叫／悶哼音效；本次新增 {len(all_new)} 個。'
    '已移除 Dhol、唱段與印度主題合成音。RANDOM HUMAN 會從完整聲庫抽樣，且避免連續重複同一檔。</div>'
)
if 'id="humanPackNote"' in s:
    s = re.sub(r'<div class="systemGestureNote" id="humanPackNote">.*?</div>', note, s, flags=re.S, count=1)
else:
    s = re.sub(
        r'(<button class="mini" id="voiceTest">試聽人聲</button></div>)(</div>)',
        r'\1' + note + r'\2', s, count=1
    )

# Hard verification: none of the previous themed controls/functions may survive.
for forbidden in ('indiaPerson', 'playBhangraStyle', 'id="bhangraSfx"', "data-sound=\"bhangra\"", "data-sound=\"dhol\""):
    if forbidden in s:
        raise SystemExit(f'India/Bhangra remnant still present: {forbidden}')
INDEX.write_text(s, encoding='utf-8')

# Manifest.
if MANIFEST.exists():
    md = json.loads(MANIFEST.read_text(encoding='utf-8'))
    md['name'] = 'SLAP! Mobile 3.8'
    md['short_name'] = 'SLAP! 3.8'
    md['description'] = (
        f'手機動作感測遊戲與防盜警戒，內建 {total_human} 個真人受擊、疼痛、悶哼與慘叫音效，'
        '支援背景音訊強化、力度分級與挑戰模式。'
    )
    MANIFEST.write_text(json.dumps(md, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

# Force a fresh PWA cache and pre-cache the new local voice files.
if SW.exists():
    sw = SW.read_text(encoding='utf-8')
    sw = re.sub(r"const CACHE='[^']+';", "const CACHE='slap-mobile-v10-human-hit-2';", sw, count=1)
    am = re.search(r'const ASSETS=(\[.*?\]);', sw, re.S)
    if not am:
        raise SystemExit('Service worker ASSETS not found')
    assets = json.loads(am.group(1))
    assets = [
        a for a in assets
        if '/sounds/india/' not in a and '/extra-' not in a and '/wilhelm-' not in a
    ]
    for f in all_new:
        if f not in assets:
            assets.append(f)
    sw = sw[:am.start(1)] + json.dumps(assets, ensure_ascii=False) + sw[am.end(1):]
    SW.write_text(sw, encoding='utf-8')

# CC0 source record with exactly the files that were successfully converted.
Path('HUMAN_AUDIO_SOURCES_2.md').write_text(
    '# Additional Human Hit Voice Sources\n\n'
    '## WilhelmSFX CC0 sound bank\n'
    f'- Repository: {SOURCE_REPO}\n'
    '- Repository license: CC0 1.0 Universal\n'
    '- Selection rule: human scream / pain / hurt / agony / grunt / groan / yell / gasp reactions; animal, creature, music and weapon sounds excluded.\n'
    f'- Added local derivatives: `{len(all_new)}` files under `sounds/voices/wilhelm-*.mp3`\n'
    '- Processing: trim leading/trailing silence, mono conversion, high/low-pass cleanup, loudness normalization, MP3 conversion for iPhone/web compatibility.\n\n'
    '### Selected source files\n' + ''.join(f'- `{x}`\n' for x in selected_sources) +
    '\nThe previous generated India/Dhol/chant assets are removed. No song, melody, Dhol layer, or synthetic chant is included in the human hit presets.\n',
    encoding='utf-8'
)

print(f'Added {len(all_new)} CC0 human clips; total human library: {total_human}')
