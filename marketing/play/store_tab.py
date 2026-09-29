import json, os, re, subprocess, random
s=open(r"C:/Users/happy/Downloads/비밀과외 VOCA 단어암기장-20260915T012833Z-1-001/비밀과외 VOCA 단어암기장/voca-site/public/index.html",encoding='utf-8').read()
j=json.loads(re.search(r'<script id="data" type="application/json">(.*?)</script>',s,re.S).group(1))
main=[d for d in dict.fromkeys(w['d'] for w in j['words']) if d.startswith('Day')]
C1=[]
for d in main[:5]:
    for w in j['words']:
        if w['d']==d:
            for x in [w]+(w.get('more') or []):
                if x.get('i') and x['i'] not in C1: C1.append(x['i'])
random.seed(3)
V=['cartoon','real','water','clay']
cards={}
for k,i in enumerate(C1[:64]):
    cards[i]={"v":[V[k%4]]+([V[(k+1)%4]] if k%3==0 else []),"t":"2026-09-20","b":1+(k%3),"r":"2026-09-2%d"%(k%9),"x":[0,4,9,16,26][k%5],"p":0}
pend={i:{"v":"cartoon","t":"2026-09-29"} for i in C1[64:67]}
import datetime
td=datetime.date(2026,9,30);log={str(td-datetime.timedelta(days=d)):{"q":8+d%5,"ok":6+d%4,"sec":600} for d in range(0,12)}
prep=("localStorage.setItem('voca.tut','99');localStorage.setItem('voca.intro','1');localStorage.setItem('voca.cards',%s);localStorage.setItem('voca.pending',%s);localStorage.setItem('voca.log',%s);localStorage.setItem('voca.stkSeen','12');localStorage.setItem('voca.exp',JSON.stringify('ex1'));localStorage.setItem('voca.charge',JSON.stringify({n:4,t:Date.now()-240000}));localStorage.setItem('voca.seen',JSON.stringify(%s));localStorage.setItem('voca.unlk',JSON.stringify(['ex1','ex2','sp1','sp2']));localStorage.setItem('voca.notif',JSON.stringify({on:true,ask:9}));"
      %(json.dumps(json.dumps(cards)),json.dumps(json.dumps(pend)),json.dumps(json.dumps(log)),json.dumps(list(cards))))
W="await new Promise(r=>setTimeout(r,%d));"
Q="const q=s=>document.querySelector(s);"
TEAR="q('#shelfOpen').click();"+W%1100+"const st=q('#oStage'),r=st.getBoundingClientRect(),y=r.top+r.height/2,P=(t,x)=>st.dispatchEvent(new PointerEvent(t,{bubbles:true,clientX:x,clientY:y,pointerId:1,pointerType:'touch',isPrimary:true}));P('pointerdown',r.left+20);for(let k=1;k<=12;k++){P('pointermove',r.left+20+k*r.width/10);"+W%30+"}P('pointerup',r.right);"+W%1400+"const T=()=>{P('pointerdown',r.left+r.width/2);P('pointerup',r.left+r.width/2);};"
# 새 카드가 뒤집힐 때까지
NEWCARD="for(let n=0;n<10;n++){const cur=[...document.querySelectorAll('#oStage .ocard')].find(x=>x.classList.contains('cur'));if(cur&&cur.classList.contains('isnew')){T();"+W%1300+"break;}T();"+W%900+"if(q('#oQuiz')&&!q('#oQuiz').hidden){const oc=[...document.querySelectorAll('.oq-c:not(:disabled)')];if(oc.length){oc[0].click();"+W%500+"q('#oQuiz .oq-go').click();"+W%700+"}}else{T();"+W%700+"}}"
ASK="for(let n=0;n<10;n++){if(q('#oQuiz')&&!q('#oQuiz').hidden&&document.querySelector('.oq-c:not(:disabled)'))break;T();"+W%900+"if(q('#oQuiz')&&!q('#oQuiz').hidden)break;T();"+W%700+"}"

def tab(prefix,w,h):
    return [{"name":prefix+"1_today","prep":prep,"w":w,"h":h,"scale":2,"pre":900},
            {"name":prefix+"2_new","prep":prep,"w":w,"h":h,"scale":2,"run":Q+TEAR+NEWCARD,"wait":10,"pre":1200},
            {"name":prefix+"3_quiz","prep":prep,"w":w,"h":h,"scale":2,"run":Q+TEAR+ASK,"wait":10,"pre":900},
            {"name":prefix+"4_binder","prep":prep,"w":w,"h":h,"scale":2,"run":Q+"q('#switcher [data-view=binder]').click();","wait":1200,"pre":900}]
sc=tab("t7_",600,1067)+tab("t10_",800,1422)
env=dict(os.environ,SCENES=json.dumps(sc))
r=subprocess.run(["node","capture.mjs","https://voca-halu.suhwanit.workers.dev/","D:/voca-mkt/store"],env=env,capture_output=True,text=True,encoding='utf-8')
print(r.stdout[-300:],r.stderr[-300:])
