from pathlib import Path
import re

p=Path('index.html')
s=p.read_text(encoding='utf-8')

# Version labels
s=s.replace('SLAP! Mobile 3.4 · iOS Background Survival','SLAP! Mobile 3.5 · Bhangra SFX')
s=s.replace('<span class="ver">3.4</span>','<span class="ver">3.5</span>')
s=s.replace('SLAP! Mobile 3.4 · iOS Background Survival · Touch Guard · CC0 · PWA','SLAP! Mobile 3.5 · Bhangra SFX · iOS Background Survival · Touch Guard · PWA')

# Add original Punjabi/Bhangra-inspired sound controls to Free mode.
if 'id="bhangraSfx"' not in s:
    card='''<div class="card" id="bhangraSfx"><h2>旁遮普 / Bhangra 派對音效 <small style="font-size:9px;color:#7f8996;font-weight:800">ORIGINAL SYNTH</small></h2><div class="presetGrid"><button class="preset" data-sound="bhangra"><span>🥁</span>BHANGRA HIT</button><button class="preset" data-sound="dhol"><span>🪘</span>DHOL HIT</button><button class="preset" data-sound="festival"><span>🗣️</span>FESTIVAL HEY</button><button class="preset" data-sound="desiChaos"><span>🎉</span>DESI CHAOS</button></div><div class="systemGestureNote"><b>聲音設計：</b>參考你提供影片的高能量旁遮普舞曲氣氛，使用原創 dhol 類鼓點、短促「HA / HEY / OI」非語詞人聲合成與音高滑動；不取樣原曲、不重製原旋律或歌詞。</div></div>\n'''
    marker='</section>\n<section class="view" id="gameView">'
    s=s.replace(marker,card+marker,1)

# Original Web Audio synthesis engine. No copyrighted audio or melody is embedded.
if 'function playBhangraStyle(' not in s:
    js=r'''
function drumNoise(delay=0,dur=.055,gain=.11,center=1900){
  const a=audio(),len=Math.max(1,a.sampleRate*dur|0),buf=a.createBuffer(1,len,a.sampleRate),d=buf.getChannelData(0);
  for(let i=0;i<len;i++)d[i]=(Math.random()*2-1)*(1-i/len);
  const src=a.createBufferSource(),bp=a.createBiquadFilter(),g=a.createGain(),t=a.currentTime+delay;
  src.buffer=buf;bp.type='bandpass';bp.frequency.value=center;bp.Q.value=.8;g.gain.setValueAtTime(.001,t);g.gain.linearRampToValueAtTime(gain,t+.005);g.gain.exponentialRampToValueAtTime(.001,t+dur);
  src.connect(bp);bp.connect(g);g.connect(a.destination);src.start(t);src.stop(t+dur+.02);
}
function dholHit(power=1,delay=0,high=false){
  const a=audio(),t=a.currentTime+delay,o=a.createOscillator(),g=a.createGain(),o2=a.createOscillator(),g2=a.createGain();
  const start=high?190:145,end=high?72:52;
  o.type='sine';o.frequency.setValueAtTime(start,t);o.frequency.exponentialRampToValueAtTime(end,t+.13);
  g.gain.setValueAtTime(.001,t);g.gain.linearRampToValueAtTime(.32*power,t+.006);g.gain.exponentialRampToValueAtTime(.001,t+.18);
  o2.type='triangle';o2.frequency.setValueAtTime(start*1.9,t);o2.frequency.exponentialRampToValueAtTime(end*1.35,t+.09);
  g2.gain.setValueAtTime(.001,t);g2.gain.linearRampToValueAtTime(.10*power,t+.004);g2.gain.exponentialRampToValueAtTime(.001,t+.105);
  o.connect(g);g.connect(a.destination);o2.connect(g2);g2.connect(a.destination);o.start(t);o.stop(t+.2);o2.start(t);o2.stop(t+.12);drumNoise(delay,.05,.075*power,high?2350:1500);
}
function vocalBurst(power=1,vowel='a',delay=0,rise=true){
  const a=audio(),t=a.currentTime+delay,dur=.25,o=a.createOscillator(),master=a.createGain();
  const forms={a:[780,1160,2850],e:[520,1710,2480],o:[460,820,2760],i:[340,2050,2960]};
  const fs=forms[vowel]||forms.a,base=118+Math.random()*24;
  o.type='sawtooth';o.frequency.setValueAtTime(base,t);o.frequency.exponentialRampToValueAtTime((rise?1.34:.84)*base,t+dur*.82);
  master.gain.setValueAtTime(.001,t);master.gain.linearRampToValueAtTime(.13*power,t+.014);master.gain.setValueAtTime(.12*power,t+.085);master.gain.exponentialRampToValueAtTime(.001,t+dur);
  fs.forEach((f,i)=>{const bp=a.createBiquadFilter(),fg=a.createGain();bp.type='bandpass';bp.frequency.value=f;bp.Q.value=i===0?4.5:6;fg.gain.value=[1,.62,.32][i];o.connect(bp);bp.connect(fg);fg.connect(master)});
  master.connect(a.destination);o.start(t);o.stop(t+dur+.03);
  drumNoise(delay+.004,.035,.025*power,3200);
}
function festiveChirp(power=1,delay=0){
  const a=audio(),notes=[392,523,659],times=[0,.065,.13];
  notes.forEach((f,i)=>{const o=a.createOscillator(),g=a.createGain(),t=a.currentTime+delay+times[i];o.type='square';o.frequency.value=f;g.gain.setValueAtTime(.001,t);g.gain.linearRampToValueAtTime(.055*power,t+.006);g.gain.exponentialRampToValueAtTime(.001,t+.075);o.connect(g);g.connect(a.destination);o.start(t);o.stop(t+.085)});
}
function playBhangraStyle(kind,power=10){
  const p=Math.max(.65,Math.min(1.35,power/13));
  if(kind==='dhol'){dholHit(p,0,false);dholHit(p*.86,.105,true);dholHit(p*.94,.215,false);return}
  if(kind==='festival'){vocalBurst(p,'e',0,true);dholHit(p*.8,.045,true);festiveChirp(p,.12);return}
  if(kind==='desiChaos'){
    const r=Math.random();
    if(r<.34){dholHit(p,0,false);vocalBurst(p,'a',.035,true);dholHit(p*.8,.16,true)}
    else if(r<.68){vocalBurst(p,'o',0,false);dholHit(p,.055,false);festiveChirp(p,.14)}
    else{dholHit(p,0,true);dholHit(p*.9,.09,false);vocalBurst(p,'e',.11,true);vocalBurst(p*.72,'a',.27,false)}
    return
  }
  dholHit(p,0,false);vocalBurst(p,'a',.035,true);dholHit(p*.82,.13,true);festiveChirp(p*.72,.205);
}
'''
    s=s.replace('const sampleFiles=',js+'\nconst sampleFiles=',1)

# Route new preset kinds to the original synthesis engine.
old="function synthSound(power=10,kind=state.sound){const p=Math.min(1.5,Math.max(.45,power/14));"
new="function synthSound(power=10,kind=state.sound){if(kind==='bhangra'||kind==='dhol'||kind==='festival'||kind==='desiChaos'){playBhangraStyle(kind,power);return}const p=Math.min(1.5,Math.max(.45,power/14));"
if old in s:
    s=s.replace(old,new,1)

p.write_text(s,encoding='utf-8')

# PWA metadata/cache bump.
mp=Path('manifest.webmanifest')
if mp.exists():
    m=mp.read_text(encoding='utf-8')
    m=m.replace('SLAP! Mobile 3.4','SLAP! Mobile 3.5')
    m=m.replace('手機動作感測遊戲與防盜警戒，內建 CC0 真實音效、拍擊力度分級、30 秒挑戰、自動校正與事件紀錄。','手機動作感測遊戲與防盜警戒，內建 CC0 人聲、原創 Bhangra 派對音效、iOS 背景存活強化、Touch Guard 與挑戰模式。')
    mp.write_text(m,encoding='utf-8')

swp=Path('sw.js')
if swp.exists():
    sw=swp.read_text(encoding='utf-8')
    sw=re.sub(r"const CACHE='[^']+';","const CACHE='slap-mobile-v8-bhangra-sfx';",sw,count=1)
    swp.write_text(sw,encoding='utf-8')
