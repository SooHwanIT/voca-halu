"""포카 수집 기능 화면을 고해상도로 찍는다 (capture.mjs 사용)."""
import json, os, subprocess

SEED = r"""
const d=JSON.parse(document.getElementById('data')?.textContent||'null');
"""
# 첫 로드 뒤 localStorage에 넣을 준비 코드 — Day 01 앨범 일부를 모은 상태, 일부 단어는 암기 완료(홀로)
PREP_SEED = r"""
localStorage.setItem('voca.days',JSON.stringify(['Day 01']));
const d=await (await fetch('/')).text();
const j=JSON.parse(d.match(/<script id="data" type="application\/json">([\s\S]*?)<\/script>/)[1]);
const W=j.words.filter(w=>w.d==='Day 01');const V=['cartoon','real','water','clay'];const cards={},done=[];
W.forEach((w,k)=>{[w,...(w.more||[])].forEach((x,jj)=>{if(x.i&&(k+jj)%3!==0){const n=(k%5===0)?4:1+((k+jj)%3);cards[x.i]={v:V.slice(0,n),t:'2026-09-2'+(k%9)};}});if(k%4===0)done.push(w.id);});
localStorage.setItem('voca.cards',JSON.stringify(cards));localStorage.setItem('voca.done',JSON.stringify(done));
localStorage.setItem('voca.packs',JSON.stringify({}));
"""
# 예문 빈칸 문제의 정답을 데이터에서 찾아 누른다
ANSWER = r"""
const D=JSON.parse(document.getElementById('data').textContent).words;
const norm=s=>s.replace(/\s+/g,' ').trim();
const ans=()=>{const pr=document.querySelector('#qPrompt');const t=norm(pr.textContent);
  for(const w of D){for(const x of [w,...(w.more||[])]){const m=x.ex.match(/^(.*)\[(.+?)\](.*)$/);if(m&&t.startsWith(norm(m[1]).slice(0,25))&&t.endsWith(norm(m[3]).slice(-12)))return w.w;}}return null;};
const pick=()=>{const a=ans();const b=[...document.querySelectorAll('#qChoices .choice')].find(c=>c.textContent.replace(/^\d/,'').trim()===a)||document.querySelector('#qChoices .choice');b.click();};
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
"""
WAITIMG = "const p=document.querySelector('#qPic');const t0=Date.now();while(!(p.complete&&p.naturalWidth)&&Date.now()-t0<8000)await sleep(150);"

scenes = [
    {"name": "b1_binder", "prep": PREP_SEED, "run": "document.querySelector('.bottomnav [data-view=binder]').click();await new Promise(r=>setTimeout(r,2500));", "wait": 1500},
    {"name": "b2_card_full", "prep": PREP_SEED, "run": "document.querySelector('.bottomnav [data-view=binder]').click();await new Promise(r=>setTimeout(r,800));document.querySelector('.slot.got.full').click();await new Promise(r=>setTimeout(r,1500));", "wait": 800},
    {"name": "b3_card_locked", "prep": PREP_SEED, "run": "document.querySelector('.bottomnav [data-view=binder]').click();await new Promise(r=>setTimeout(r,800));document.querySelector('.slot:not(.got)').click();", "wait": 800},
    {"name": "b4_quiz_pack", "prep": PREP_SEED, "run": "document.querySelector('.bottomnav [data-view=quiz]').click();", "wait": 800},
    {"name": "b5_quiz_gain", "prep": PREP_SEED, "run": ANSWER + "document.querySelector('.bottomnav [data-view=quiz]').click();await sleep(300);document.querySelector('[data-pack=open]').click();await sleep(500);" + WAITIMG + "pick();", "wait": 450},
    {"name": "b6_pack_result", "prep": PREP_SEED, "run": ANSWER + "document.querySelector('.bottomnav [data-view=quiz]').click();await sleep(300);document.querySelector('[data-pack=open]').click();await sleep(500);for(let k=0;k<10&&document.body.classList.contains('focus');k++){" + WAITIMG + "pick();await sleep(300);document.querySelector('#qNext').click();await sleep(400);}window.scrollTo(0,0);await sleep(1500);", "wait": 1200},
    {"name": "b7_list_owned", "prep": PREP_SEED, "run": "document.querySelectorAll('#wordList .row .more')[2].click();window.scrollTo(0,0);", "wait": 1800},
]
share = [{"name": "b8_share_card", "w": 1080, "h": 1350, "scale": 1, "prep": PREP_SEED,
          "run": ANSWER + "document.querySelector('.bottomnav [data-view=quiz]')?.click();document.querySelector('[data-view=quiz]').click();await sleep(300);document.querySelector('[data-pack=open]').click();await sleep(500);for(let k=0;k<10&&document.body.classList.contains('focus');k++){" + WAITIMG + "pick();await sleep(300);document.querySelector('#qNext').click();await sleep(400);}"
                 "const oc=URL.createObjectURL;let u=null;URL.createObjectURL=b=>{u=oc.call(URL,b);return u;};const ck=HTMLAnchorElement.prototype.click;HTMLAnchorElement.prototype.click=function(){};"
                 "Object.defineProperty(navigator,'canShare',{value:()=>false});document.querySelector('[data-pack=share]').click();await sleep(3000);HTMLAnchorElement.prototype.click=ck;"
                 "document.body.innerHTML='';document.body.style.cssText='margin:0;padding:0;background:#000';const im=document.createElement('img');im.src=u;im.style.cssText='display:block;width:1080px;height:1350px';document.body.appendChild(im);await sleep(800);", "wait": 500}]

env = dict(os.environ, SCENES=json.dumps(scenes + share))
r = subprocess.run(["node", "capture.mjs", "http://localhost:8766/", "D:/voca-mkt/shots"], env=env, capture_output=True, text=True, cwd=os.path.dirname(os.path.abspath(__file__)))
print(r.stdout[-800:], r.stderr[-800:])
