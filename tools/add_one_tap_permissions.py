from pathlib import Path
import json

ROOT=Path('.')
INDEX=ROOT/'index.html'
MANIFEST=ROOT/'manifest.webmanifest'
SW=ROOT/'sw.js'

html=INDEX.read_text(encoding='utf-8')

html=html.replace('SLAP! Mobile 3.10 · Custom Scream Lab','SLAP! Mobile 3.11 · One-Tap Permissions')
html=html.replace('SLAP! Mobile 3.10 · Custom Scream Lab · CC0 · Background Audio · PWA','SLAP! Mobile 3.11 · One-Tap Permissions · CC0 · PWA')

css=r'''

/* One-Tap Permissions 3.11 */
.permissionHub{margin:11px 0 12px;padding:15px;border:1px solid rgba(92,225,230,.2);border-radius:22px;background:linear-gradient(145deg,rgba(92,225,230,.075),rgba(217,255,67,.035))}
.permissionHubHead{display:flex;align-items:flex-start;justify-content:space-between;gap:12px;margin-bottom:12px}
.permissionHubHead b{display:block;font-size:14px}.permissionHubHead small{display:block;margin-top:4px;color:var(--muted);font-size:10.5px;line-height:1.45}
.permissionMaster{width:100%;min-height:58px;border:0;border-radius:17px;background:linear-gradient(135deg,var(--acid),#bfff4c);color:#080b0d;font-weight:950;font-size:14px;box-shadow:0 12px 30px rgba(217,255,67,.12)}
.permissionMaster.busy{opacity:.72}.permissionMaster.done{background:#eaffad}
.permissionGrid{display:grid;grid-template-columns:repeat(4,1fr);gap:7px;margin-top:10px}
.permissionChip{padding:9px 6px;border-radius:13px;border:1px solid var(--line);background:#12171d;text-align:center;min-width:0}
.permissionChip span{display:block;font-size:9px;color:var(--muted);font-weight:850;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.permissionChip b{display:block;margin-top:3px;font-size:10px;color:#b8c0cb}.permissionChip.ok{border-color:rgba(217,255,67,.28);background:rgba(217,255,67,.07)}.permissionChip.ok b{color:var(--acid)}.permissionChip.bad{border-color:rgba(255,73,111,.28);background:rgba(255,73,111,.07)}.permissionChip.bad b{color:#ff8ca3}.permissionChip.na b{color:#8b94a3}
.permissionHint{margin-top:9px;color:#737d8b;font-size:9.5px;line-height:1.45}
@media(max-width:420px){.permissionGrid{grid-template-columns:repeat(2,1fr)}}
'''
if '/* One-Tap Permissions 3.11 */' not in html:
    html=html.replace('</style>',css+'\n</style>',1)

panel=r'''
<div class="permissionHub" id="permissionHub">
  <div class="permissionHubHead"><div><b>一鍵啟用所有權限</b><small>一次處理 SLAP 目前需要的動作感測、麥克風、音訊播放與螢幕喚醒，並開啟 iPhone 背景存活強化。</small></div><span class="localBadge">1 TAP</span></div>
  <button class="permissionMaster" id="grantAllBtn" type="button">⚡ 一鍵啟用全部權限</button>
  <div class="permissionGrid">
    <div class="permissionChip" id="permMotion"><span>MOTION</span><b>待授權</b></div>
    <div class="permissionChip" id="permMic"><span>MIC</span><b>待授權</b></div>
    <div class="permissionChip" id="permAudio"><span>AUDIO</span><b>待啟用</b></div>
    <div class="permissionChip" id="permWake"><span>WAKE</span><b>待啟用</b></div>
  </div>
  <div class="permissionHint" id="permissionHint">iPhone 仍會顯示 Apple / Safari 的系統授權視窗；網頁不能代替你按「允許」。若曾選擇拒絕，可能需要到 Safari 的網站權限設定重新開啟。</div>
</div>
'''
anchor='<section class="view show" id="freeView">'
if 'id="permissionHub"' not in html:
    html=html.replace(anchor,anchor+'\n'+panel,1)

js=r'''

// One-Tap Permissions 3.11
function setPermissionChip(id,stateText,mode=''){
  const el=$(id);if(!el)return;const b=el.querySelector('b');if(b)b.textContent=stateText;el.className='permissionChip'+(mode?' '+mode:'');
}
async function requestMotionForAll(){
  if(!('DeviceMotionEvent'in window)){setPermissionChip('permMotion','不支援','na');return false}
  try{
    if(typeof DeviceMotionEvent.requestPermission==='function'){
      const r=await DeviceMotionEvent.requestPermission();const ok=r==='granted';setPermissionChip('permMotion',ok?'已允許':'被拒絕',ok?'ok':'bad');return ok;
    }
    setPermissionChip('permMotion','可使用','ok');return true;
  }catch(e){setPermissionChip('permMotion','被拒絕','bad');return false}
}
async function requestMicForAll(){
  if(!navigator.mediaDevices||!navigator.mediaDevices.getUserMedia){setPermissionChip('permMic','不支援','na');return false}
  try{const s=await navigator.mediaDevices.getUserMedia({audio:true,video:false});s.getTracks().forEach(t=>t.stop());setPermissionChip('permMic','已允許','ok');return true}catch(e){setPermissionChip('permMic','被拒絕','bad');return false}
}
async function startSensorAfterGrant(){
  if(state.running)return true;
  if(!('DeviceMotionEvent'in window))return false;
  try{audio();window.removeEventListener('devicemotion',onMotion);window.addEventListener('devicemotion',onMotion,{passive:true});state.running=true;setStatus('感測中','on');$('startBtn').textContent='停止感測';$('startBtn').classList.add('stop');setBgState('bgMotionState','LIVE','bgAlive');if(autoTouchLock)setTimeout(()=>setTouchLock(true),520);return true}catch(e){return false}
}
async function enableWakeForAll(){
  if($('wake'))$('wake').checked=true;
  if(!('wakeLock'in navigator)){setPermissionChip('permWake','不支援','na');return false}
  try{if(state.wakeLock)try{await state.wakeLock.release()}catch(e){}state.wakeLock=await navigator.wakeLock.request('screen');setPermissionChip('permWake','已啟用','ok');return true}catch(e){setPermissionChip('permWake','暫不可用','bad');return false}
}
async function grantAllPermissions(){
  const btn=$('grantAllBtn');if(!btn||btn.disabled)return;btn.disabled=true;btn.classList.add('busy');btn.textContent='正在啟用…';
  // Start audio/background work synchronously from the tap before permission prompts consume transient activation.
  try{const a=audio();if(a.state==='suspended')a.resume();setPermissionChip('permAudio','已啟用','ok')}catch(e){setPermissionChip('permAudio','失敗','bad')}
  backgroundAudioMode=true;localStorage.setItem('slapBackgroundAudio','1');if($('backgroundAudio'))$('backgroundAudio').checked=true;applyAudioSession();setupMediaSession();
  let survivalPromise=null;try{if($('iosSurvival'))$('iosSurvival').checked=true;survivalPromise=startIosSurvival()}catch(e){}
  const motionOK=await requestMotionForAll();
  const micOK=await requestMicForAll();
  if(motionOK)await startSensorAfterGrant();
  await enableWakeForAll();
  try{if(survivalPromise)await survivalPromise}catch(e){}
  const audioOK=$('permAudio')?.classList.contains('ok');const wakeOK=$('permWake')?.classList.contains('ok')||$('permWake')?.classList.contains('na');
  const allOK=motionOK&&micOK&&audioOK&&wakeOK;
  btn.disabled=false;btn.classList.remove('busy');btn.classList.toggle('done',!!allOK);btn.textContent=allOK?'✓ 權限與強化已完成':'↻ 再試一次未完成項目';
  const hint=$('permissionHint');if(hint)hint.textContent=allOK?'完成：動作感測、麥克風、音訊、背景強化與螢幕喚醒已初始化。':'有項目未完成。若系統已記住「不允許」，請到 Safari / iPhone 的網站權限設定重新允許後再按一次。';
  toast(allOK?'全部可用權限已啟用':'部分權限未開啟，請看狀態');
}
if($('grantAllBtn'))$('grantAllBtn').addEventListener('click',grantAllPermissions);
if(!('DeviceMotionEvent'in window))setPermissionChip('permMotion','不支援','na');
if(!navigator.mediaDevices?.getUserMedia)setPermissionChip('permMic','不支援','na');
if(!('wakeLock'in navigator))setPermissionChip('permWake','不支援','na');
'''
if '// One-Tap Permissions 3.11' not in html:
    html=html.replace("let touchLocked=false,lockScrollY=0,holdTimer=null,holdRAF=null,holdStarted=0;",js+"\nlet touchLocked=false,lockScrollY=0,holdTimer=null,holdRAF=null,holdStarted=0;",1)

INDEX.write_text(html,encoding='utf-8')

m=json.loads(MANIFEST.read_text(encoding='utf-8'))
m['name']='SLAP! Mobile 3.11'
m['short_name']='SLAP! 3.11'
m['description']='手機動作感測受擊音效工具，提供一鍵請求動作感測與麥克風權限、音訊解鎖、螢幕喚醒、iPhone 背景存活強化，以及 67 個真人 CC0 人聲與自錄慘叫變聲實驗室。'
MANIFEST.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

sw=SW.read_text(encoding='utf-8')
import re
sw=re.sub(r"const CACHE='[^']+';","const CACHE='slap-mobile-v13-one-tap-permissions';",sw,count=1)
SW.write_text(sw,encoding='utf-8')
print('Upgraded to 3.11 one-tap permissions')
