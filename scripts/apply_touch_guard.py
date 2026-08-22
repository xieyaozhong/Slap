from pathlib import Path
import re

INDEX = Path("index.html")
MANIFEST = Path("manifest.webmanifest")
SW = Path("sw.js")

s = INDEX.read_text(encoding="utf-8")

# Version labels
s = s.replace("SLAP! Mobile 3.2 · Human Hit Pack", "SLAP! Mobile 3.3 · Touch Guard")
s = s.replace('<span class="ver">3.2</span>', '<span class="ver">3.3</span>')
s = s.replace(
    "SLAP! Mobile 3.2 · Human Hit Pack · CC0 · Background Audio · PWA",
    "SLAP! Mobile 3.3 · Human Hit Pack · Touch Guard · Background Audio · PWA",
)

# CSS protection layer
if ".touchShield{" not in s:
    css = r'''
/* Touch Guard 3.3 */
html,body{-webkit-user-select:none;user-select:none;-webkit-touch-callout:none;overscroll-behavior:none}
body{-webkit-text-size-adjust:100%}
button,.btn,.mini,.preset,.tab,label,select,input{touch-action:manipulation}
.hero,.orbWrap,.orb,.rings,.meter{touch-action:none;-webkit-user-select:none;user-select:none}
img,svg{-webkit-user-drag:none;user-drag:none}
.touchGuardBar{display:flex;align-items:center;justify-content:space-between;gap:10px;margin:0 0 10px;padding:9px 11px;border:1px solid var(--line);border-radius:16px;background:#0f1318}
.touchGuardBar .tgState{font-size:10px;color:var(--muted);font-weight:900;letter-spacing:.05em}
.touchGuardBar .tgState.on{color:var(--acid)}
.touchLockBtn{min-width:120px}
.touchShield{position:fixed;inset:0;z-index:9999;display:none;touch-action:none;overscroll-behavior:none;background:linear-gradient(180deg,rgba(7,9,12,.09),rgba(7,9,12,.18));-webkit-backdrop-filter:blur(.5px);backdrop-filter:blur(.5px)}
.touchShield.show{display:block}
.touchShieldTop{position:absolute;left:50%;top:calc(env(safe-area-inset-top) + 16px);transform:translateX(-50%);display:flex;align-items:center;gap:8px;padding:9px 13px;border-radius:999px;background:rgba(10,13,17,.84);border:1px solid rgba(217,255,67,.26);color:#eaffad;font-size:10px;font-weight:950;white-space:nowrap;box-shadow:0 10px 35px rgba(0,0,0,.24)}
.touchUnlockWrap{position:absolute;left:50%;bottom:calc(env(safe-area-inset-bottom) + 24px);transform:translateX(-50%);width:min(320px,calc(100vw - 36px));text-align:center}
.touchUnlock{position:relative;width:100%;min-height:58px;overflow:hidden;border:1px solid rgba(255,255,255,.12);border-radius:20px;background:rgba(14,18,23,.92);color:white;font-weight:950;touch-action:none}
.touchUnlock:before{content:"";position:absolute;left:0;top:0;bottom:0;width:var(--hold,0%);background:rgba(217,255,67,.22);transition:width .08s linear;pointer-events:none}
.touchUnlock span{position:relative;z-index:2}
.touchUnlockHint{margin-top:8px;color:#aab2bd;font-size:9.5px;font-weight:800}
html.touch-locked,html.touch-locked body{overflow:hidden!important;overscroll-behavior:none!important;touch-action:none!important}
body.touch-locked{position:fixed;inset:0;width:100%;height:100%}
.systemGestureNote{margin-top:9px;padding:10px 11px;border-radius:14px;background:rgba(92,225,230,.055);border:1px solid rgba(92,225,230,.14);font-size:10px;color:#aeb8c4;line-height:1.55}
'''
    s = s.replace("</style>", css + "\n</style>", 1)

# Quick lock control above the motion visual
if 'id="touchLockBtn"' not in s:
    quick = (
        '<div class="touchGuardBar">'
        '<button class="mini touchLockBtn" id="touchLockBtn">🔒 鎖定操作</button>'
        '<span class="tgState" id="touchGuardState">防誤觸 OFF</span>'
        '</div>\n'
    )
    s = s.replace('<section class="hero"', quick + '<section class="hero"', 1)

# Settings / explanation card
if 'id="autoTouchLock"' not in s:
    card = '''<div class="card"><h2>防誤觸與系統手勢</h2><div class="row"><div class="rowText"><b>啟動感測後自動鎖定操作</b><small>動作感測啟動後自動蓋上觸控盾牌，避免手掌、衣物、雙擊與滑動誤觸按鈕。</small></div><label class="switch"><input id="autoTouchLock" type="checkbox" checked><span></span></label></div><div class="row"><div class="rowText"><b>鎖定時停用頁面手勢</b><small>阻擋長按選單、文字選取、雙擊縮放、拖曳、下拉更新與頁面滑動。</small></div><b class="ok" style="font-size:11px">ACTIVE</b></div><div class="systemGestureNote"><b>iPhone 建議：</b>加入主畫面後執行可減少 Safari 介面干擾。Home 指示條、控制中心、通知中心與系統「背面輕點」屬於 iOS 層級，網頁不能強制關閉；若拍擊時會觸發 iPhone 快捷指令，請到「設定 → 輔助使用 → 觸控 → 背面輕點」關閉雙點／三點動作。需要更完整的單一 App 鎖定可搭配 iOS「引導使用模式」。</div></div>\n'''
    s = s.replace('<div class="footer">', card + '<div class="footer">', 1)

# Full-screen transparent shield
if 'id="touchShield"' not in s:
    shield = '''</main><div class="touchShield" id="touchShield" aria-hidden="true"><div class="touchShieldTop">🔒 TOUCH GUARD · 感測仍持續</div><div class="touchUnlockWrap"><button class="touchUnlock" id="touchUnlock"><span>長按 1.2 秒解除鎖定</span></button><div class="touchUnlockHint">一般點擊、雙擊與滑動不會解除</div></div></div><div class="toast" id="toast"></div>'''
    s = s.replace('</main><div class="toast" id="toast"></div>', shield, 1)

# Auto-lock shortly after motion permission/start succeeds
old_start = "toast('動作感測已啟動')}"
new_start = "toast('動作感測已啟動');if(autoTouchLock)setTimeout(()=>setTouchLock(true),520)}"
if old_start in s and "setTimeout(()=>setTouchLock(true),520)" not in s:
    s = s.replace(old_start, new_start, 1)

# Runtime gesture guard
if "let touchLocked=false" not in s:
    js = r'''
let touchLocked=false,lockScrollY=0,holdTimer=null,holdRAF=null,holdStarted=0;
let autoTouchLock=localStorage.getItem('slapAutoTouchLock')!=='0';
const touchShield=$('touchShield'),touchUnlock=$('touchUnlock'),touchGuardState=$('touchGuardState'),touchLockBtn=$('touchLockBtn');
if($('autoTouchLock')){$('autoTouchLock').checked=autoTouchLock;$('autoTouchLock').onchange=e=>{autoTouchLock=e.target.checked;localStorage.setItem('slapAutoTouchLock',autoTouchLock?'1':'0');toast(autoTouchLock?'已開啟自動操作鎖定':'已關閉自動操作鎖定')}}
function updateTouchGuardUI(){if(!touchGuardState||!touchLockBtn)return;touchGuardState.textContent=touchLocked?'防誤觸 ON':'防誤觸 OFF';touchGuardState.classList.toggle('on',touchLocked);touchLockBtn.textContent=touchLocked?'🔒 已鎖定':'🔒 鎖定操作'}
function setTouchLock(on){touchLocked=!!on;if(touchLocked){lockScrollY=window.scrollY||0;document.documentElement.classList.add('touch-locked');document.body.classList.add('touch-locked');document.body.style.top=(-lockScrollY)+'px';touchShield.classList.add('show');touchShield.setAttribute('aria-hidden','false');try{if(document.documentElement.requestFullscreen&&!document.fullscreenElement)document.documentElement.requestFullscreen().catch(()=>{})}catch(e){}try{if(screen.orientation&&screen.orientation.lock)screen.orientation.lock('portrait').catch(()=>{})}catch(e){}toast('操作已鎖定 · 動作感測持續')}else{touchShield.classList.remove('show');touchShield.setAttribute('aria-hidden','true');document.documentElement.classList.remove('touch-locked');document.body.classList.remove('touch-locked');document.body.style.top='';window.scrollTo(0,lockScrollY);try{if(document.fullscreenElement&&document.exitFullscreen)document.exitFullscreen().catch(()=>{})}catch(e){}toast('操作已解除鎖定')}updateTouchGuardUI()}
if(touchLockBtn)touchLockBtn.onclick=()=>{if(!touchLocked)setTouchLock(true)};
function cancelUnlockHold(){clearTimeout(holdTimer);holdTimer=null;cancelAnimationFrame(holdRAF);holdRAF=null;holdStarted=0;if(touchUnlock)touchUnlock.style.setProperty('--hold','0%')}
function drawUnlockHold(){if(!holdStarted)return;const pct=Math.min(100,(performance.now()-holdStarted)/1200*100);touchUnlock.style.setProperty('--hold',pct+'%');if(pct<100)holdRAF=requestAnimationFrame(drawUnlockHold)}
function beginUnlockHold(e){e.preventDefault();e.stopPropagation();cancelUnlockHold();holdStarted=performance.now();drawUnlockHold();holdTimer=setTimeout(()=>{cancelUnlockHold();setTouchLock(false)},1200)}
if(touchUnlock){touchUnlock.addEventListener('pointerdown',beginUnlockHold);['pointerup','pointercancel','pointerleave'].forEach(n=>touchUnlock.addEventListener(n,cancelUnlockHold));touchUnlock.addEventListener('contextmenu',e=>e.preventDefault())}
['gesturestart','gesturechange','gestureend'].forEach(n=>document.addEventListener(n,e=>e.preventDefault(),{passive:false}));
document.addEventListener('contextmenu',e=>{if(!e.target.closest('input,textarea'))e.preventDefault()});
document.addEventListener('selectstart',e=>{if(touchLocked||!e.target.closest('input,textarea'))e.preventDefault()});
document.addEventListener('dragstart',e=>e.preventDefault());
document.addEventListener('dblclick',e=>e.preventDefault(),{passive:false});
document.addEventListener('touchmove',e=>{if(touchLocked)e.preventDefault()},{passive:false});
if(touchShield){['touchstart','touchmove','touchend'].forEach(n=>touchShield.addEventListener(n,e=>{if(!e.target.closest('#touchUnlock'))e.preventDefault()},{passive:false}));touchShield.addEventListener('pointerdown',e=>{if(e.target===touchShield)e.preventDefault()})}
document.addEventListener('keydown',e=>{if(touchLocked&&e.key==='Escape')e.preventDefault()});
updateTouchGuardUI();
'''
    marker = "window.addEventListener('beforeinstallprompt'"
    if marker not in s:
        raise RuntimeError("beforeinstallprompt marker not found")
    s = s.replace(marker, js + "\n" + marker, 1)

INDEX.write_text(s, encoding="utf-8")

if MANIFEST.exists():
    m = MANIFEST.read_text(encoding="utf-8")
    m = re.sub(r'"name"\s*:\s*"SLAP! Mobile [^"]+"', '"name": "SLAP! Mobile 3.3"', m, count=1)
    m = m.replace(
        "手機動作感測遊戲與防盜警戒：拍擊偵測、30 秒挑戰、自動校正與事件紀錄。",
        "手機動作感測遊戲與防盜警戒：人聲受擊音效、拍擊偵測、Touch Guard 防誤觸、挑戰模式與事件紀錄。",
    )
    MANIFEST.write_text(m, encoding="utf-8")

if SW.exists():
    sw = SW.read_text(encoding="utf-8")
    sw = re.sub(r"const CACHE='[^']+';", "const CACHE='slap-mobile-v6-touch-guard';", sw, count=1)
    SW.write_text(sw, encoding="utf-8")

# Export inline JS for node --check in CI
match = re.search(r"<script>\s*(.*?)\s*</script>", s, re.S)
if not match:
    raise RuntimeError("inline script not found")
Path("/tmp/slap-inline.js").write_text(match.group(1), encoding="utf-8")
print("Touch Guard 3.3 patch prepared")
