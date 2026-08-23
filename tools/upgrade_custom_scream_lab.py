from pathlib import Path
import json, re

ROOT=Path('.')
INDEX=ROOT/'index.html'
MANIFEST=ROOT/'manifest.webmanifest'
SW=ROOT/'sw.js'
ICON_SOURCES=ROOT/'ICON_SOURCES.md'
AVATARS=ROOT/'assets'/'avatars'

s=INDEX.read_text(encoding='utf-8')

# Version labels.
s=s.replace('SLAP! Mobile 3.9 · Avatar Voice Pack','SLAP! Mobile 3.10 · Custom Scream Lab')
s=s.replace('<span class="ver">3.9</span>','<span class="ver">3.10</span>')
s=s.replace('SLAP! Mobile 3.9 · Avatar Voice Pack · CC0 · Background Audio · PWA','SLAP! Mobile 3.10 · Custom Scream Lab · LOCAL MIC · PWA')

# Allow customScream to persist as the selected sound.
s=s.replace("sound:(settings.sound&&settings.sound.startsWith('human'))?settings.sound:'human'", "sound:(settings.sound&&(settings.sound.startsWith('human')||settings.sound==='customScream'))?settings.sound:'human'")

# Add recorder avatar button once.
heavy='''<button class="preset avatarPreset" data-sound="humanHeavy"><span class="avatarArt avatarHeavy"><img src="./assets/avatars/avatar-heavy-hit.svg" alt="重擊反應"></span><b>HEAVY HIT</b><small>重擊反應</small></button>'''
record='''<button class="preset avatarPreset recordPreset" data-sound="customScream" id="customScreamPreset"><span class="avatarArt avatarRecord"><img src="./assets/avatars/avatar-record.svg" alt="自己錄音"></span><b>MY SCREAM</b><small>自己錄音變聲</small></button>'''
if 'id="customScreamPreset"' not in s:
    if heavy not in s: raise SystemExit('heavy avatar button not found')
    s=s.replace(heavy, heavy+'\n'+record,1)

# Add recorder lab below the human pack note.
lab='''
<div class="customScreamLab" id="customScreamLab">
  <div class="customLabHead"><div><b>🎙️ 自錄慘叫實驗室</b><small>錄 1–6 秒自己的聲音，再套用不同變聲效果。聲音只保存在這台裝置的瀏覽器，不會上傳。</small></div><span class="localBadge">LOCAL ONLY</span></div>
  <div class="recordStrip">
    <button class="recordVoiceBtn" id="recordVoiceBtn" type="button"><span class="recordDot"></span><b>開始錄音</b></button>
    <div class="recordReadout"><b id="recordStatus">尚未錄音</b><small id="recordTime">最多 6.0 秒</small></div>
  </div>
  <div class="voiceFxGrid" id="voiceFxGrid">
    <button class="voiceFx active" type="button" data-voicefx="random"><b>🎲 RANDOM</b><small>每次受擊隨機變聲</small></button>
    <button class="voiceFx" type="button" data-voicefx="raw"><b>🙂 ORIGINAL</b><small>接近原始錄音</small></button>
    <button class="voiceFx" type="button" data-voicefx="shriek"><b>😱 SHARP</b><small>尖銳高音慘叫</small></button>
    <button class="voiceFx" type="button" data-voicefx="panic"><b>⚡ PANIC</b><small>快速驚慌尖叫</small></button>
    <button class="voiceFx" type="button" data-voicefx="crush"><b>💥 CRUSHED</b><small>破音重擊慘叫</small></button>
    <button class="voiceFx" type="button" data-voicefx="ghost"><b>👻 GHOST</b><small>拖尾幽靈尖叫</small></button>
    <button class="voiceFx" type="button" data-voicefx="growl"><b>🗿 DEEP</b><small>低沉疼痛呻吟</small></button>
  </div>
  <div class="customLabActions"><button class="mini" id="previewCustomVoice" type="button">試聽目前效果</button><button class="mini" id="clearCustomVoice" type="button">刪除我的錄音</button></div>
  <div class="micPrivacy">需要麥克風權限。錄音完成後會使用 Web Audio 在本機即時變調、濾波、失真與延遲；不會送到伺服器。</div>
</div>'''
if 'id="customScreamLab"' not in s:
    pat=r'(<div class="systemGestureNote" id="humanPackNote">.*?</div>)(</div>\s*</section>)'
    if not re.search(pat,s,re.S): raise SystemExit('human pack note anchor not found')
    s=re.sub(pat,lambda m:m.group(1)+lab+m.group(2),s,count=1,flags=re.S)

# Add styling.
css=r'''
/* Custom Scream Lab 3.10 */
.avatarRecord{background:radial-gradient(circle at 35% 25%,rgba(217,255,67,.3),rgba(217,255,67,.065) 55%,rgba(255,255,255,.02))}
.recordPreset{border-style:dashed}
.customScreamLab{display:none;margin-top:14px;padding:14px;border-radius:20px;background:#0d1116;border:1px solid rgba(217,255,67,.15)}
.customScreamLab.show{display:block}
.customLabHead{display:flex;align-items:flex-start;justify-content:space-between;gap:12px;margin-bottom:13px}.customLabHead b{font-size:13px}.customLabHead small{display:block;margin-top:4px;color:var(--muted);font-size:10px;line-height:1.45}.localBadge{flex:none;border:1px solid rgba(217,255,67,.25);background:rgba(217,255,67,.07);color:var(--acid);border-radius:999px;padding:6px 8px;font-size:8px;font-weight:950;letter-spacing:.08em}.recordStrip{display:grid;grid-template-columns:minmax(0,1fr) 112px;gap:9px;align-items:stretch}.recordVoiceBtn{min-height:58px;border:1px solid rgba(255,73,111,.24);border-radius:17px;background:rgba(255,73,111,.08);display:flex;align-items:center;justify-content:center;gap:9px;font-size:12px;font-weight:950}.recordVoiceBtn.recording{background:rgba(255,73,111,.18);border-color:rgba(255,73,111,.5)}.recordDot{width:10px;height:10px;border-radius:50%;background:var(--hot);box-shadow:0 0 0 5px rgba(255,73,111,.08)}.recordVoiceBtn.recording .recordDot{animation:recordPulse .8s ease-in-out infinite alternate}.recordReadout{border:1px solid var(--line);border-radius:17px;padding:9px 10px;background:#141920;display:flex;flex-direction:column;justify-content:center}.recordReadout b{font-size:10px}.recordReadout small{font-size:9px;color:var(--muted);margin-top:3px}.voiceFxGrid{display:grid;grid-template-columns:repeat(2,1fr);gap:7px;margin-top:10px}.voiceFx{min-height:54px;text-align:left;border:1px solid var(--line);border-radius:14px;background:#171c23;padding:9px 10px;color:#b9c1cb}.voiceFx b{display:block;font-size:9.5px}.voiceFx small{display:block;margin-top:3px;color:#737d89;font-size:8.5px;line-height:1.25}.voiceFx.active{border-color:rgba(217,255,67,.38);background:rgba(217,255,67,.08);color:#eaffad}.customLabActions{display:flex;gap:7px;flex-wrap:wrap;margin-top:10px}.micPrivacy{margin-top:10px;color:#727c89;font-size:9px;line-height:1.45}.recordReady{color:var(--acid)!important}@keyframes recordPulse{to{transform:scale(1.28);box-shadow:0 0 0 8px rgba(255,73,111,.12)}}
@media(max-width:420px){.recordStrip{grid-template-columns:1fr}.recordReadout{min-height:48px}.customLabHead{display:block}.localBadge{display:inline-block;margin-top:8px}}
'''
if '/* Custom Scream Lab 3.10 */' not in s:
    s=s.replace('</style>',css+'\n</style>',1)

# Custom recording + FX engine. Insert before the media pool declaration.
engine=r'''
let customVoiceBuffer=null,voiceRecorder=null,voiceStream=null,voiceChunks=[],voiceAutoStop=null,voiceTick=null,voiceStarted=0;
let customVoiceFx=localStorage.getItem('slapCustomVoiceFx')||'random';
const customFxList=['shriek','panic','crush','ghost','growl'];
function voiceDB(){return new Promise((resolve,reject)=>{try{const q=indexedDB.open('slap-custom-voice',1);q.onupgradeneeded=()=>{if(!q.result.objectStoreNames.contains('clips'))q.result.createObjectStore('clips',{keyPath:'id'})};q.onsuccess=()=>resolve(q.result);q.onerror=()=>reject(q.error)}catch(e){reject(e)}})}
async function storeVoiceBlob(blob){try{const db=await voiceDB();await new Promise((resolve,reject)=>{const tx=db.transaction('clips','readwrite');tx.objectStore('clips').put({id:'main',blob,mime:blob.type,ts:Date.now()});tx.oncomplete=resolve;tx.onerror=()=>reject(tx.error)});db.close()}catch(e){}}
async function fetchVoiceBlob(){try{const db=await voiceDB();const item=await new Promise((resolve,reject)=>{const tx=db.transaction('clips','readonly'),q=tx.objectStore('clips').get('main');q.onsuccess=()=>resolve(q.result);q.onerror=()=>reject(q.error)});db.close();return item&&item.blob?item.blob:null}catch(e){return null}}
async function deleteVoiceBlob(){try{const db=await voiceDB();await new Promise((resolve,reject)=>{const tx=db.transaction('clips','readwrite');tx.objectStore('clips').delete('main');tx.oncomplete=resolve;tx.onerror=()=>reject(tx.error)});db.close()}catch(e){}}
function setRecordStatus(text,ready=false){if($('recordStatus')){$('recordStatus').textContent=text;$('recordStatus').classList.toggle('recordReady',ready)}}
async function decodeCustomVoice(blob,persist=false){try{const arr=await blob.arrayBuffer();customVoiceBuffer=await audio().decodeAudioData(arr.slice(0));setRecordStatus('錄音已就緒',true);if($('recordTime'))$('recordTime').textContent=(customVoiceBuffer.duration||0).toFixed(1)+' 秒 · 本機保存';if(persist)await storeVoiceBlob(blob);return true}catch(e){customVoiceBuffer=null;setRecordStatus('錄音格式無法解碼');toast('這次錄音無法解碼，請重新錄一次');return false}}
function pickVoiceMime(){const list=['audio/mp4;codecs=alac','audio/mp4','audio/webm;codecs=opus','audio/webm'];if(!window.MediaRecorder||!MediaRecorder.isTypeSupported)return '';for(const x of list)if(MediaRecorder.isTypeSupported(x))return x;return ''}
function selectCustomPreset(){state.sound='customScream';document.querySelectorAll('.preset').forEach(x=>x.classList.toggle('active',x.dataset.sound==='customScream'));if($('customScreamLab'))$('customScreamLab').classList.add('show');save()}
function stopVoiceRecording(){if(voiceRecorder&&voiceRecorder.state==='recording')voiceRecorder.stop()}
async function startVoiceRecording(){if(voiceRecorder&&voiceRecorder.state==='recording'){stopVoiceRecording();return}if(!navigator.mediaDevices||!navigator.mediaDevices.getUserMedia||!window.MediaRecorder){toast('這個瀏覽器不支援麥克風錄音');return}try{voiceStream=await navigator.mediaDevices.getUserMedia({audio:{echoCancellation:false,noiseSuppression:false,autoGainControl:true},video:false});voiceChunks=[];const mime=pickVoiceMime();voiceRecorder=mime?new MediaRecorder(voiceStream,{mimeType:mime}):new MediaRecorder(voiceStream);voiceRecorder.ondataavailable=e=>{if(e.data&&e.data.size)voiceChunks.push(e.data)};voiceRecorder.onstop=async()=>{clearTimeout(voiceAutoStop);clearInterval(voiceTick);voiceAutoStop=voiceTick=null;if(voiceStream){voiceStream.getTracks().forEach(t=>t.stop());voiceStream=null}if($('recordVoiceBtn')){$('recordVoiceBtn').classList.remove('recording');$('recordVoiceBtn').querySelector('b').textContent='開始錄音'}const blob=new Blob(voiceChunks,{type:voiceRecorder.mimeType||mime||'audio/webm'});if(blob.size<512){setRecordStatus('錄音太短');return}if(await decodeCustomVoice(blob,true)){selectCustomPreset();toast('錄音完成，可直接用拍擊測試')}};voiceRecorder.start(180);voiceStarted=performance.now();setRecordStatus('正在錄音…');if($('recordVoiceBtn')){$('recordVoiceBtn').classList.add('recording');$('recordVoiceBtn').querySelector('b').textContent='停止錄音'}voiceTick=setInterval(()=>{const t=Math.min(6,(performance.now()-voiceStarted)/1000);if($('recordTime'))$('recordTime').textContent=t.toFixed(1)+' / 6.0 秒'},100);voiceAutoStop=setTimeout(stopVoiceRecording,6000)}catch(e){if(voiceStream){voiceStream.getTracks().forEach(t=>t.stop());voiceStream=null}setRecordStatus('需要麥克風權限');toast('請允許麥克風權限後再試一次')}}
function distortionCurve(amount=35){const n=1024,c=new Float32Array(n),k=amount;for(let i=0;i<n;i++){const x=i*2/n-1;c[i]=(3+k)*x*20*Math.PI/180/(Math.PI+k*Math.abs(x))}return c}
function resolveCustomFx(){return customVoiceFx==='random'?customFxList[Math.floor(Math.random()*customFxList.length)]:customVoiceFx}
function playCustomScream(power=10){if(!customVoiceBuffer){toast('先錄一段自己的聲音');if($('customScreamLab'))$('customScreamLab').classList.add('show');return}const a=audio(),src=a.createBufferSource(),out=a.createGain(),fx=resolveCustomFx();src.buffer=customVoiceBuffer;out.gain.value=Math.min(1,.62+power/42);let last=src;if(fx==='shriek'){src.playbackRate.value=1.38;const f=a.createBiquadFilter();f.type='highpass';f.frequency.value=720;f.Q.value=.8;last.connect(f);last=f}else if(fx==='panic'){src.playbackRate.value=1.62;const f=a.createBiquadFilter();f.type='bandpass';f.frequency.value=1850;f.Q.value=.72;last.connect(f);last=f}else if(fx==='crush'){src.playbackRate.value=1.18;const sh=a.createWaveShaper();sh.curve=distortionCurve(58);sh.oversample='2x';const f=a.createBiquadFilter();f.type='highpass';f.frequency.value=360;last.connect(sh);sh.connect(f);last=f}else if(fx==='ghost'){src.playbackRate.value=1.08;const f=a.createBiquadFilter();f.type='bandpass';f.frequency.value=1250;f.Q.value=.45;const delay=a.createDelay(.8),wet=a.createGain(),fb=a.createGain();delay.delayTime.value=.16;wet.gain.value=.34;fb.gain.value=.24;last.connect(f);f.connect(out);f.connect(delay);delay.connect(wet);wet.connect(out);delay.connect(fb);fb.connect(delay);out.connect(a.destination);src.start();return}else if(fx==='growl'){src.playbackRate.value=.68;const f=a.createBiquadFilter();f.type='lowpass';f.frequency.value=1450;f.Q.value=.55;last.connect(f);last=f}else{src.playbackRate.value=1}last.connect(out);out.connect(a.destination);src.start()}
async function restoreCustomVoice(){const blob=await fetchVoiceBlob();if(blob)await decodeCustomVoice(blob,false);document.querySelectorAll('[data-voicefx]').forEach(b=>b.classList.toggle('active',b.dataset.voicefx===customVoiceFx));if(state.sound==='customScream'&&$('customScreamLab'))$('customScreamLab').classList.add('show')}
'''
if 'function playCustomScream' not in s:
    anchor='const mediaPool=Array.from({length:6}'
    if anchor not in s: raise SystemExit('mediaPool anchor not found')
    s=s.replace(anchor,engine+'\n'+anchor,1)

# Route custom sound before normal sample playback.
old="function playSound(power=10,kind=state.sound){const src=samplePath(kind,power);"
new="function playSound(power=10,kind=state.sound){if(kind==='customScream'){playCustomScream(power);return}const src=samplePath(kind,power);"
if old in s: s=s.replace(old,new,1)
elif "function playSound(power=10,kind=state.sound){if(kind==='customScream')" not in s: raise SystemExit('playSound anchor not found')

# Make preset selection open the lab and avoid a confusing silent preview before recording exists.
old_handler="document.querySelectorAll('.preset').forEach(b=>{if(b.dataset.sound===state.sound)b.classList.add('active');else b.classList.remove('active');b.onclick=()=>{state.sound=b.dataset.sound;document.querySelectorAll('.preset').forEach(x=>x.classList.toggle('active',x===b));save();playSound(11,state.sound)}});"
new_handler="document.querySelectorAll('.preset').forEach(b=>{if(b.dataset.sound===state.sound)b.classList.add('active');else b.classList.remove('active');b.onclick=()=>{state.sound=b.dataset.sound;document.querySelectorAll('.preset').forEach(x=>x.classList.toggle('active',x===b));if($('customScreamLab'))$('customScreamLab').classList.toggle('show',state.sound==='customScream');save();if(state.sound==='customScream'&&!customVoiceBuffer){toast('先錄一段自己的聲音');return}playSound(11,state.sound)}});"
if old_handler in s: s=s.replace(old_handler,new_handler,1)
elif "classList.toggle('show',state.sound==='customScream')" not in s: raise SystemExit('preset handler anchor not found')

# Bind recorder UI and make voice test support the custom recording.
old_voice="if($('voiceTest'))$('voiceTest').onclick=()=>{audio();playSound(Math.max(state.threshold+4,14),state.sound.startsWith('human')?state.sound:'human')};document.addEventListener('visibilitychange',()=>{if(backgroundAudioMode)applyAudioSession()});"
new_voice="if($('voiceTest'))$('voiceTest').onclick=()=>{audio();playSound(Math.max(state.threshold+4,14),(state.sound.startsWith('human')||state.sound==='customScream')?state.sound:'human')};if($('recordVoiceBtn'))$('recordVoiceBtn').onclick=startVoiceRecording;if($('previewCustomVoice'))$('previewCustomVoice').onclick=()=>{audio();playCustomScream(Math.max(state.threshold+4,14))};if($('clearCustomVoice'))$('clearCustomVoice').onclick=async()=>{customVoiceBuffer=null;await deleteVoiceBlob();setRecordStatus('尚未錄音');if($('recordTime'))$('recordTime').textContent='最多 6.0 秒';if(state.sound==='customScream'){state.sound='human';save();document.querySelectorAll('.preset').forEach(x=>x.classList.toggle('active',x.dataset.sound==='human'))}toast('本機錄音已刪除')};document.querySelectorAll('[data-voicefx]').forEach(b=>b.onclick=()=>{customVoiceFx=b.dataset.voicefx;localStorage.setItem('slapCustomVoiceFx',customVoiceFx);document.querySelectorAll('[data-voicefx]').forEach(x=>x.classList.toggle('active',x===b));if(customVoiceBuffer)playCustomScream(Math.max(state.threshold+3,13))});restoreCustomVoice();document.addEventListener('visibilitychange',()=>{if(backgroundAudioMode)applyAudioSession()});"
if old_voice in s: s=s.replace(old_voice,new_voice,1)
elif "$('recordVoiceBtn').onclick=startVoiceRecording" not in s: raise SystemExit('voice binding anchor not found')

INDEX.write_text(s,encoding='utf-8')

# Local Tabler microphone icon (MIT).
AVATARS.mkdir(parents=True,exist_ok=True)
(AVATARS/'avatar-record.svg').write_text('''<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="#d9ff43" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M9 5a3 3 0 0 1 3 -3a3 3 0 0 1 3 3v5a3 3 0 0 1 -3 3a3 3 0 0 1 -3 -3l0 -5"/><path d="M5 10a7 7 0 0 0 14 0"/><path d="M8 21l8 0"/><path d="M12 17l0 4"/></svg>\n''',encoding='utf-8')

# Record icon attribution.
if ICON_SOURCES.exists():
    txt=ICON_SOURCES.read_text(encoding='utf-8')
    if 'avatar-record.svg' not in txt:
        txt += '\n- `avatar-record.svg` ← `microphone.svg`\n'
        ICON_SOURCES.write_text(txt,encoding='utf-8')

# Manifest.
if MANIFEST.exists():
    md=json.loads(MANIFEST.read_text(encoding='utf-8'))
    md['name']='SLAP! Mobile 3.10'
    md['short_name']='SLAP! 3.10'
    md['description']='手機動作感測受擊音效工具，內建 67 個真人 CC0 人聲與本機自錄慘叫變聲實驗室，支援 iPhone 麥克風錄音、Web Audio 變調與背景音訊強化。'
    MANIFEST.write_text(json.dumps(md,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

# Service worker cache + new local icon.
if SW.exists():
    sw=SW.read_text(encoding='utf-8')
    sw=re.sub(r"const CACHE='[^']+';","const CACHE='slap-mobile-v12-custom-scream-lab';",sw,count=1)
    m=re.search(r'const ASSETS=(\[.*?\]);',sw,re.S)
    if not m: raise SystemExit('SW ASSETS not found')
    assets=json.loads(m.group(1))
    rec='./assets/avatars/avatar-record.svg'
    if rec not in assets: assets.append(rec)
    sw=sw[:m.start(1)]+json.dumps(assets,ensure_ascii=False)+sw[m.end(1):]
    SW.write_text(sw,encoding='utf-8')

print('Upgraded to SLAP Mobile 3.10 Custom Scream Lab')
