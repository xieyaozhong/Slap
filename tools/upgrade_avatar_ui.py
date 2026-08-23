from pathlib import Path
from urllib.request import Request, urlopen
import json
import re

ROOT = Path('.')
INDEX = ROOT / 'index.html'
MANIFEST = ROOT / 'manifest.webmanifest'
SW = ROOT / 'sw.js'
AVATAR_DIR = ROOT / 'assets' / 'avatars'
AVATAR_DIR.mkdir(parents=True, exist_ok=True)

TABLER_RAW = 'https://raw.githubusercontent.com/tabler/tabler-icons/main/icons/outline/'
ICONS = {
    'avatar-random.svg': 'users.svg',
    'avatar-male.svg': 'gender-male.svg',
    'avatar-female.svg': 'gender-female.svg',
    'avatar-short-hurt.svg': 'mood-sad-dizzy.svg',
    'avatar-yell.svg': 'mood-surprised.svg',
    'avatar-heavy-hit.svg': 'mood-sad-squint.svg',
}


def get_text(url: str) -> str:
    req = Request(url, headers={'User-Agent': 'SLAP-Mobile-Avatar-Pack/3.9'})
    with urlopen(req, timeout=60) as r:
        return r.read().decode('utf-8')


# Vendor Tabler icons locally and adapt their stroke for the dark UI.
for local_name, upstream_name in ICONS.items():
    svg = get_text(TABLER_RAW + upstream_name)
    svg = re.sub(r'<!--.*?-->', '', svg, flags=re.S).strip()
    svg = svg.replace('stroke="currentColor"', 'stroke="#f7f8fa"')
    svg = svg.replace('width="24"', 'width="64"', 1).replace('height="24"', 'height="64"', 1)
    (AVATAR_DIR / local_name).write_text(svg + '\n', encoding='utf-8')

Path('ICON_SOURCES.md').write_text(
    '# Avatar Icon Sources\n\n'
    'The avatar UI uses icons from **Tabler Icons**.\n\n'
    '- Upstream: https://github.com/tabler/tabler-icons\n'
    '- License: MIT\n'
    '- Copyright: Paweł Kuna / Tabler Icons contributors\n'
    '- Local modifications: SVG comments removed, display size changed to 64×64, stroke color adapted for the SLAP dark UI.\n\n'
    '## Included icons\n\n' +
    ''.join(f'- `{local}` ← `{upstream}`\n' for local, upstream in ICONS.items()) +
    '\nThe MIT license text is available in the upstream repository.\n',
    encoding='utf-8'
)

s = INDEX.read_text(encoding='utf-8')

# Version.
s = s.replace('SLAP! Mobile 3.8 · Human Hit Pack II', 'SLAP! Mobile 3.9 · Avatar Voice Pack')
s = s.replace('<span class="ver">3.8</span>', '<span class="ver">3.9</span>')
s = s.replace('SLAP! Mobile 3.8 · Human Hit Pack II · CC0 · Background Audio · PWA',
              'SLAP! Mobile 3.9 · Avatar Voice Pack · CC0 Voices · MIT Icons · PWA')

# Remove the old built-in selectable sound-effect card.
s = re.sub(
    r'<div class="card"><h2>內建 CC0 音效 .*?</div></div>\s*',
    '', s, flags=re.S, count=1
)

# Replace the six human preset buttons with avatar cards.
avatar_grid = '''<div class="presetGrid avatarGrid" id="humanPresets">
<button class="preset avatarPreset" data-sound="human"><span class="avatarArt avatarRandom"><img src="./assets/avatars/avatar-random.svg" alt="隨機人聲"></span><b>RANDOM</b><small>隨機人聲</small></button>
<button class="preset avatarPreset" data-sound="humanMale"><span class="avatarArt avatarMale"><img src="./assets/avatars/avatar-male.svg" alt="男性受擊"></span><b>MALE</b><small>男性受擊</small></button>
<button class="preset avatarPreset" data-sound="humanFemale"><span class="avatarArt avatarFemale"><img src="./assets/avatars/avatar-female.svg" alt="女性受擊"></span><b>FEMALE</b><small>女性受擊</small></button>
<button class="preset avatarPreset" data-sound="humanShort"><span class="avatarArt avatarShort"><img src="./assets/avatars/avatar-short-hurt.svg" alt="短促疼痛"></span><b>SHORT HURT</b><small>短促疼痛</small></button>
<button class="preset avatarPreset" data-sound="humanYell"><span class="avatarArt avatarYell"><img src="./assets/avatars/avatar-yell.svg" alt="大聲慘叫"></span><b>YELL</b><small>大聲慘叫</small></button>
<button class="preset avatarPreset" data-sound="humanHeavy"><span class="avatarArt avatarHeavy"><img src="./assets/avatars/avatar-heavy-hit.svg" alt="重擊反應"></span><b>HEAVY HIT</b><small>重擊反應</small></button>
</div>'''
s, n = re.subn(r'<div class="presetGrid" id="humanPresets">.*?</div>', avatar_grid, s, flags=re.S, count=1)
if n != 1:
    raise SystemExit('humanPresets grid not found')

s = s.replace('人聲受擊音效 <small style="font-size:9px;color:#7f8996;font-weight:800">CC0 VOICE PACK · 67 CLIPS</small>',
              '人聲受擊頭像 <small style="font-size:9px;color:#7f8996;font-weight:800">AVATAR VOICE PACK · 67 CLIPS</small>')
s = s.replace('目前內建 67 個真人受擊／疼痛／慘叫／悶哼音效；本次新增 30 個。已移除 Dhol、唱段與印度主題合成音。',
              '目前內建 67 個真人受擊／疼痛／慘叫／悶哼音效；自由模式只保留真人聲。每一種受擊分類改用對應頭像顯示。')

# Avatar card styles.
marker = '/* Avatar Voice Pack 3.9 */'
if marker not in s:
    avatar_css = r'''

/* Avatar Voice Pack 3.9 */
.avatarGrid{grid-template-columns:repeat(3,1fr);gap:10px}
.avatarPreset{position:relative;min-height:148px;padding:13px 9px 12px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:7px;overflow:hidden;background:linear-gradient(180deg,#191f27,#12161c);transition:transform .16s ease,border-color .16s ease,background .16s ease}
.avatarPreset:active{transform:scale(.97)}
.avatarPreset .avatarArt{width:76px;height:76px;margin:0 0 2px;border-radius:50%;display:grid;place-items:center;border:1px solid rgba(255,255,255,.11);box-shadow:inset 0 1px 0 rgba(255,255,255,.06),0 13px 28px rgba(0,0,0,.28)}
.avatarPreset .avatarArt img{display:block;width:46px;height:46px;margin:0;opacity:.96;filter:drop-shadow(0 5px 10px rgba(0,0,0,.24))}
.avatarPreset b{font-size:10.5px;letter-spacing:.045em;line-height:1.1}
.avatarPreset small{display:block;font-size:9px;color:#858f9d;font-weight:800;line-height:1.15}
.avatarPreset.active{background:linear-gradient(180deg,rgba(217,255,67,.14),rgba(217,255,67,.055));border-color:rgba(217,255,67,.48);box-shadow:0 0 0 1px rgba(217,255,67,.08) inset,0 12px 34px rgba(217,255,67,.06)}
.avatarPreset.active .avatarArt{border-color:rgba(217,255,67,.42);box-shadow:0 0 0 4px rgba(217,255,67,.07),0 13px 30px rgba(0,0,0,.3)}
.avatarRandom{background:radial-gradient(circle at 35% 25%,rgba(92,225,230,.25),rgba(92,225,230,.06) 55%,rgba(255,255,255,.02))}
.avatarMale{background:radial-gradient(circle at 35% 25%,rgba(90,142,255,.28),rgba(90,142,255,.06) 55%,rgba(255,255,255,.02))}
.avatarFemale{background:radial-gradient(circle at 35% 25%,rgba(255,102,171,.28),rgba(255,102,171,.06) 55%,rgba(255,255,255,.02))}
.avatarShort{background:radial-gradient(circle at 35% 25%,rgba(255,176,46,.28),rgba(255,176,46,.06) 55%,rgba(255,255,255,.02))}
.avatarYell{background:radial-gradient(circle at 35% 25%,rgba(255,73,111,.28),rgba(255,73,111,.06) 55%,rgba(255,255,255,.02))}
.avatarHeavy{background:radial-gradient(circle at 35% 25%,rgba(185,120,255,.3),rgba(185,120,255,.06) 55%,rgba(255,255,255,.02))}
@media(max-width:420px){.avatarGrid{grid-template-columns:repeat(2,1fr)}.avatarPreset{min-height:140px}.avatarPreset .avatarArt{width:70px;height:70px}.avatarPreset .avatarArt img{width:43px;height:43px}}
'''
    s = s.replace('</style>', avatar_css + '\n</style>', 1)

# Human voice is the only selectable impact preset. Also normalize old saved settings.
s = s.replace("sound:'slap'", "sound:'human'", 1)
s = s.replace("sound:settings.sound||'slap'", "sound:(settings.sound&&settings.sound.startsWith('human'))?settings.sound:'human'", 1)

# Remove old selectable sample groups while retaining siren for guard mode.
m = re.search(r'const sampleFiles=(\{.*?\});\nconst sampleBroken=', s, re.S)
if not m:
    raise SystemExit('sampleFiles object not found')
samples = json.loads(m.group(1))
for key in ['slap', 'bonk', 'cat', 'crash', 'arcade']:
    samples.pop(key, None)
obj = json.dumps(samples, ensure_ascii=False, separators=(',', ':'))
s = s[:m.start(1)] + obj + s[m.end(1):]

# Challenge mode should no longer play the removed arcade effect.
s = s.replace("playSound(8,'arcade');", "if(navigator.vibrate)navigator.vibrate(30);")
s = s.replace("playSound(13,'arcade');", "if(navigator.vibrate)navigator.vibrate([40,50,40]);")

# Sanity checks.
if 'id="presets"' in s or '內建 CC0 音效' in s:
    raise SystemExit('built-in preset UI still present')
if 'data-sound="slap"' in s or 'data-sound="bonk"' in s or 'data-sound="cat"' in s:
    raise SystemExit('legacy selectable sounds still present')
if s.count('class="preset avatarPreset"') != 6:
    raise SystemExit('expected 6 avatar presets')

INDEX.write_text(s, encoding='utf-8')

# Remove obsolete selectable audio assets from the repository checkout.
for rel in [
    'sounds/bell.ogg', 'sounds/bonk.ogg', 'sounds/cat.ogg', 'sounds/crash.ogg',
    'sounds/slap-soft.ogg', 'sounds/slap-medium.ogg', 'sounds/slap-heavy.ogg'
]:
    p = ROOT / rel
    if p.exists():
        p.unlink()

# Manifest 3.9.
if MANIFEST.exists():
    md = json.loads(MANIFEST.read_text(encoding='utf-8'))
    md['name'] = 'SLAP! Mobile 3.9'
    md['short_name'] = 'SLAP! 3.9'
    md['description'] = '手機動作感測受擊音效工具，內建 67 個真人 CC0 人聲，採用 MIT 開源頭像圖示、背景音訊強化、力度分級與挑戰模式。'
    MANIFEST.write_text(json.dumps(md, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

# Service worker: remove old selectable audio, add avatar assets, bump cache.
if SW.exists():
    sw = SW.read_text(encoding='utf-8')
    sw = re.sub(r"const CACHE='[^']+';", "const CACHE='slap-mobile-v11-avatar-voice-ui';", sw, count=1)
    am = re.search(r'const ASSETS=(\[.*?\]);', sw, re.S)
    if not am:
        raise SystemExit('service worker ASSETS not found')
    assets = json.loads(am.group(1))
    obsolete = {
        './sounds/bell.ogg','./sounds/bonk.ogg','./sounds/cat.ogg','./sounds/crash.ogg',
        './sounds/slap-soft.ogg','./sounds/slap-medium.ogg','./sounds/slap-heavy.ogg'
    }
    assets = [a for a in assets if a not in obsolete]
    for local_name in ICONS:
        path = './assets/avatars/' + local_name
        if path not in assets:
            assets.append(path)
    sw = sw[:am.start(1)] + json.dumps(assets, ensure_ascii=False) + sw[am.end(1):]
    SW.write_text(sw, encoding='utf-8')

print('Upgraded SLAP Mobile to 3.9 Avatar Voice Pack')
