from pathlib import Path
import re

p=Path('index.html')
s=p.read_text(encoding='utf-8')

# Version labels
s=s.replace('SLAP! Mobile 3.3 · Touch Guard','SLAP! Mobile 3.4 · iOS Background Survival')
s=s.replace('<span class="ver">3.3</span>','<span class="ver">3.4</span>')
s=s.replace('SLAP! Mobile 3.3 · Touch Guard · CC0 · Background Audio · PWA','SLAP! Mobile 3.4 · iOS Background Survival · Touch Guard · CC0 · PWA')

# UI styles
if '.bgSurvivalGrid{' not in s:
    css='''\n.bgSurvivalGrid{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-top:10px}.bgSurvivalGrid>div{padding:10px 8px;border:1px solid var(--line);border-radius:14px;background:#171c23;text-align:center}.bgSurvivalGrid small{display:block;color:var(--muted);font-size:8.5px;font-weight:800}.bgSurvivalGrid b{display:block;margin-top:3px;font-size:10px}.bgAlive{color:var(--acid)}.bgWarn{color:var(--orange)}.bgDead{color:var(--hot)}\n'''
    s=s.replace('</style>',css+'\n</style>',1)

# Add stronger background survival row after existing background audio row.
if 'id="iosSurvival"' not in s:
    marker='<div class="row"><div class="rowText"><b>人聲隨機化</b>'
    panel='''<div class="row"><div class="rowText"><b>iPhone 背景存活強化</b><small>維持低功耗 HTML Audio 載波、Audio Session playback、Media Session 與自動恢復。可提高切到其他 App／鎖屏後存活機率，但 iOS 仍可能停止 Motion。</small></div><label class="switch"><input id="iosSurvival" type="checkbox"><span></span></label></div><div class="bgSurvivalGrid"><div><small>AUDIO</small><b id="bgAudioState">OFF</b></div><div><small>MOTION</small><b id="bgMotionState">WAIT</b></div><div><small>APP STATE</small><b id="bgAppState">FOREGROUND</b></div></div>\n'''
    s=s.replace(marker,panel+marker,1)

# Add iOS usage note.
if '背景測試方式' not in s:
    note='<div class="systemGestureNote"><b>背景測試方式：</b>先啟動動作感測 → 開啟「背景音訊模式」與「iPhone 背景存活強化」→ 加入主畫面執行 → 再鎖屏或切 App。回來後 App 會顯示 Motion 是否曾被 iOS 暫停。</div>'
    s=s.replace('<div class="footer">',note+'\n<div class="footer">',1)

# Track last motion timestamp.
s=s.replace('function onMotion(e){const v=motionValue(e);','function onMotion(e){lastMotionAt=performance.now();const v=motionValue(e);',1)

# Stronger background runtime before install prompt.
if 'let iosSurvivalMode=' not in s:
    js=r'''
let iosSurvivalMode=localStorage.getItem('slapIosSurvival')==='1';
let bgCarrier=null,bgCarrierURL=null,lastMotionAt=performance.now(),backgroundEnteredAt=0,bgRecoverTimer=null;
const isiOS=/iphone|ipad|ipod/i.test(navigator.userAgent)||(/Macintosh/i.test(navigator.userAgent)&&navigator.maxTouchPoints>1);
function setBgState(id,text,cls=''){const el=$(id);if(!el)return;el.textContent=text;el.className=cls}
function makeCarrierURL(){
  if(bgCarrierURL)return bgCarrierURL;
  const rate=8000,secs=1,samples=rate*secs,bytes=44+samples*2,buf=new ArrayBuffer(bytes),v=new DataView(buf);
  const w=(o,t)=>{for(let i=0;i<t.length;i++)v.setUint8(o+i,t.charCodeAt(i))};
  w(0,'RIFF');v.setUint32(4,bytes-8,true);w(8,'WAVE');w(12,'fmt ');v.setUint32(16,16,true);v.setUint16(20,1,true);v.setUint16(22,1,true);v.setUint32(24,rate,true);v.setUint32(28,rate*2,true);v.setUint16(32,2,true);v.setUint16(34,16,true);w(36,'data');v.setUint32(40,samples*2,true);
  for(let i=0;i<samples;i++){const d=(i%97===0?3:(i%53===0?-3:0));v.setInt16(44+i*2,d,true)}
  bgCarrierURL=URL.createObjectURL(new Blob([buf],{type:'audio/wav'}));return bgCarrierURL;
}
function ensureCarrier(){
  if(bgCarrier)return bgCarrier;
  bgCarrier=document.createElement('audio');bgCarrier.loop=true;bgCarrier.preload='auto';bgCarrier.playsInline=true;bgCarrier.setAttribute('playsinline','');bgCarrier.setAttribute('webkit-playsinline','');bgCarrier.src=makeCarrierURL();bgCarrier.volume=1;bgCarrier.style.display='none';document.body.appendChild(bgCarrier);
  bgCarrier.addEventListener('playing',()=>setBgState('bgAudioState','ALIVE','bgAlive'));
  bgCarrier.addEventListener('pause',()=>{if(iosSurvivalMode)setBgState('bgAudioState','PAUSED','bgWarn')});
  bgCarrier.addEventListener('error',()=>setBgState('bgAudioState','ERROR','bgDead'));
  return bgCarrier;
}
async function startIosSurvival(){
  iosSurvivalMode=true;localStorage.setItem('slapIosSurvival','1');backgroundAudioMode=true;localStorage.setItem('slapBackgroundAudio','1');if($('backgroundAudio'))$('backgroundAudio').checked=true;
  try{audio()}catch(e){}applyAudioSession();setupMediaSession();
  const c=ensureCarrier();try{await c.play()}catch(e){setBgState('bgAudioState','TAP AGAIN','bgWarn');toast('請再點一次背景強化開關以允許音訊')}
  try{if('mediaSession'in navigator)navigator.mediaSession.playbackState='playing'}catch(e){}
  setBgState('bgMotionState',state.running?'LIVE':'START SENSOR',state.running?'bgAlive':'bgWarn');
  toast('iPhone 背景存活強化已開啟');
}
function stopIosSurvival(){
  iosSurvivalMode=false;localStorage.setItem('slapIosSurvival','0');if(bgCarrier){bgCarrier.pause();try{bgCarrier.currentTime=0}catch(e){}}setBgState('bgAudioState','OFF');setBgState('bgMotionState','WAIT');toast('背景存活強化已關閉');
}
async function recoverForeground(){
  if(!iosSurvivalMode)return;
  applyAudioSession();try{if(state.audio&&state.audio.state==='suspended')await state.audio.resume()}catch(e){}
  try{if(bgCarrier&&bgCarrier.paused)await bgCarrier.play()}catch(e){}
  if(state.running){window.removeEventListener('devicemotion',onMotion);window.addEventListener('devicemotion',onMotion,{passive:true});if($('wake').checked)requestWake()}
  clearTimeout(bgRecoverTimer);bgRecoverTimer=setTimeout(()=>{const age=performance.now()-lastMotionAt;if(state.running){if(age<2500)setBgState('bgMotionState','LIVE','bgAlive');else setBgState('bgMotionState','RESUMED','bgWarn')}},900);
}
if($('iosSurvival')){$('iosSurvival').checked=iosSurvivalMode;$('iosSurvival').onchange=e=>e.target.checked?startIosSurvival():stopIosSurvival()}
if(iosSurvivalMode){setBgState('bgAudioState','READY','bgWarn');setBgState('bgMotionState',state.running?'LIVE':'START SENSOR',state.running?'bgAlive':'bgWarn')}
document.addEventListener('visibilitychange',()=>{
  if(document.visibilityState==='hidden'){
    backgroundEnteredAt=performance.now();setBgState('bgAppState','BACKGROUND','bgWarn');
    if(iosSurvivalMode){applyAudioSession();try{if(bgCarrier&&bgCarrier.paused)bgCarrier.play().catch(()=>{})}catch(e){}}
  }else{
    setBgState('bgAppState','FOREGROUND','bgAlive');
    const gap=backgroundEnteredAt?performance.now()-backgroundEnteredAt:0;
    if(iosSurvivalMode&&state.running){const motionGap=performance.now()-lastMotionAt;if(gap>2500&&motionGap>Math.min(gap*.75,5000))setBgState('bgMotionState','iOS SUSPENDED','bgDead');else setBgState('bgMotionState','SURVIVED','bgAlive')}
    recoverForeground();
  }
});
window.addEventListener('pageshow',()=>recoverForeground());window.addEventListener('focus',()=>recoverForeground());
if('mediaSession'in navigator){try{navigator.mediaSession.setActionHandler('play',()=>{if(iosSurvivalMode)startIosSurvival();else if(lastMedia)lastMedia.play().catch(()=>{})});navigator.mediaSession.setActionHandler('pause',()=>{mediaPool.forEach(a=>a.pause());if(bgCarrier)bgCarrier.pause()})}catch(e){}}
'''
    s=s.replace("window.addEventListener('beforeinstallprompt'",js+"\nwindow.addEventListener('beforeinstallprompt'",1)

# When sensor starts, update motion status.
s=s.replace("toast('動作感測已啟動');if(autoTouchLock)","toast('動作感測已啟動');setBgState('bgMotionState','LIVE','bgAlive');if(autoTouchLock)",1)

p.write_text(s,encoding='utf-8')

mp=Path('manifest.webmanifest')
if mp.exists():
    m=mp.read_text(encoding='utf-8')
    m=m.replace('SLAP! Mobile 3.3','SLAP! Mobile 3.4')
    m=m.replace('Touch Guard 防誤觸、挑戰模式與事件紀錄。','Touch Guard 防誤觸、iPhone 背景存活強化、挑戰模式與事件紀錄。')
    mp.write_text(m,encoding='utf-8')

swp=Path('sw.js')
if swp.exists():
    sw=swp.read_text(encoding='utf-8')
    sw=re.sub(r"const CACHE='[^']+';","const CACHE='slap-mobile-v7-ios-background';",sw,count=1)
    swp.write_text(sw,encoding='utf-8')
