"""试卷导出服务 - 接收 papers JSON，返回独立交互 HTML"""
from flask import Flask, request, send_file, make_response
import json, io

app = Flask(__name__)

CSS = ':root{--bg:#f5f4f0;--card:#fff;--text:#2c2c2c;--muted:#6b6b6b;--border:#e0ded8;--accent:#2c5f8a;--al:#e8f0f7;--green:#2d7d46;--gb:#edf7f0;--red:#c0392b;--rb:#fef0ef}*{box-sizing:border-box;margin:0;padding:0}body{font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;background:var(--bg);color:var(--text);line-height:1.7;font-size:15px}.c{max-width:860px;margin:0 auto;padding:24px 16px 60px}h1{font-size:21px;text-align:center;margin:20px 0 6px}.sub{text-align:center;color:var(--muted);font-size:13px;margin-bottom:18px}.tabs{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:18px;position:sticky;top:0;z-index:10;background:var(--bg);padding:8px 0}.tb{padding:8px 16px;border:1px solid var(--border);border-radius:6px;background:var(--card);font-size:13px;cursor:pointer}.tb:hover{border-color:var(--accent)}.tb.active{background:var(--accent);color:#fff;border-color:var(--accent)}.pn{display:none}.pn.active{display:block}.sb{position:sticky;top:52px;z-index:9;background:var(--card);border:1px solid var(--border);border-radius:8px;padding:12px 16px;margin-bottom:16px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px;box-shadow:0 1px 4px rgba(0,0,0,.04)}.sb .st{display:flex;gap:16px;font-size:14px}.sb .st strong{color:var(--accent)}.ph{text-align:center;padding:20px;background:var(--card);border:1px solid var(--border);border-radius:8px;margin-bottom:20px;box-shadow:0 1px 3px rgba(0,0,0,.06)}.ph h2{font-size:17px;margin-bottom:6px}.ph .mt{font-size:13px;color:var(--muted)}.cd{background:var(--card);border:1px solid var(--border);border-radius:8px;padding:18px 20px;margin-bottom:12px;box-shadow:0 1px 3px rgba(0,0,0,.06)}.cd.submitted{pointer-events:none}.cd.correct{border-color:var(--green);background:#fcfdf9}.cd.wrong{border-color:var(--red);background:#fefcfc}.qn{font-weight:700;color:var(--accent);font-size:13px;margin-bottom:4px;display:flex;align-items:center;gap:8px}.qt{display:inline-block;font-size:11px;font-weight:600;padding:2px 8px;border-radius:4px}.qt.single{color:#5b3ec4;background:#f3f0ff}.qt.multi{color:#b85c1e;background:#fff4ed}.qt.judge{color:#2d7d46;background:#edf7f0}.qt.subjective{color:#8b4513;background:#fff8f0}.qq{font-size:15px;margin:8px 0 12px;font-weight:500}.ops{list-style:none;padding:0;display:flex;flex-direction:column;gap:6px}.op{display:flex;align-items:flex-start;gap:10px;padding:9px 14px;border:1px solid var(--border);border-radius:6px;cursor:pointer;font-size:14px}.op:hover{border-color:var(--accent)}.op.selected{border-color:var(--accent);background:var(--al)}.op.correct-answer{border-color:var(--green);background:var(--gb)}.op.wrong-answer{border-color:var(--red);background:var(--rb)}.opl{font-weight:600;color:var(--muted);min-width:22px}.exp{margin-top:12px;padding:12px;border-radius:6px;background:#fafaf7;font-size:13px;display:none;border-left:3px solid var(--accent)}.exp.show{display:block}.exp.correct-exp{border-left-color:var(--green);background:var(--gb)}.exp.wrong-exp{border-left-color:var(--red);background:var(--rb)}'
LABELS = {'single': '单选题', 'multi': '多选题', 'judge': '判断题', 'subjective': '主观题'}
LB = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']

@app.route('/export', methods=['POST', 'GET'])
def do_export():

    if request.method == 'GET':
        return 'OK'
    papers = request.json
    if not papers:
        return 'No papers', 400
    
    lit = json.dumps({p['id']: p for p in papers}, ensure_ascii=False)
    
    tabs = ''.join(f'<div class="tb{" active" if i==0 else ""}" data-p="{i}">{p["t"]}</div>' for i, p in enumerate(papers))
    panels = ''.join(f'<div class="pn{" active" if i==0 else ""}" id="p-{i}"></div>' for i in range(len(papers)))
    
    js = f'''var P={lit};var L={{s:"{LABELS['single']}",m:"{LABELS['multi']}",j:"{LABELS['judge']}",z:"{LABELS['subjective']}"}};var B={json.dumps(LB)};var S={{}};
function E(s){{return(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}}
function F(q){{if(q.s==='subjective')return q.a[0]||'略';if(q.s==='judge')return q.a[0]===0?'正确':'错误';return(q.a||[]).map(function(i){{return B[i];}}).join('');}}
function I(){{Object.keys(P).forEach(function(k,i){{S[k]={{a:{{}},s:{{}}}};R(k,i);}});document.getElementById('tabs').addEventListener('click',function(e){{var t=e.target.closest('.tb');if(!t)return;document.querySelectorAll('#tabs .tb').forEach(function(x){{x.classList.remove('active');}});t.classList.add('active');document.querySelectorAll('.pn').forEach(function(x){{x.classList.remove('active');}});document.getElementById('p-'+t.dataset.p).classList.add('active');}});}}
function R(k,idx){{var p=P[k],st=S[k],n=p.d.length,sb=Object.keys(st.s).length,c=0;for(var x in st.s){{if(st.s[x].o)c++;}}var h='';h+='<div class=ph><h2>'+E(p.t)+'</h2><div class=mt>'+E(p.s)+' · 共'+n+'题</div></div>';h+='<div class=sb><div class=st>已答: <strong>'+sb+'/'+n+'</strong> 正确: <strong>'+c+'</strong> 得分: <strong>'+(sb>0?Math.round(c/sb*100):0)+'%</strong></div><div class=ac><button onclick=RST(\\"'+k+'\\") style=\\"padding:5px 14px;border:1px solid var(--red);border-radius:5px;background:var(--card);color:var(--red);font-size:12px;cursor:pointer\\">重做</button></div></div>';p.d.forEach(function(q,qi){{var s=st.s[qi],u=st.a[qi]||[],cc=s?(s.o?'correct':'wrong'):'';var lb=q.s==='judge'?['正确','错误']:q.s==='subjective'?[]:q.o.map(function(o,oi){{return B[oi]+'. '+o;}});h+='<div class=\\"cd '+(s?'submitted ':'')+cc+'\\"><div class=qn><span>'+(qi+1)+'.</span><span class=\\"qt '+q.s+'\\">'+L[q.s[0]]+'</span>'+(s?(s.o?'<span style=\\"color:var(--green);font-size:12px\\"> ✓</span>':'<span style=\\"color:var(--red);font-size:12px\\"> ✗</span>'):'')+'</div><div class=qq>'+E(q.q)+'</div>';if(q.s==='subjective'){{h+='<div style=\\"margin-top:8px;padding:8px 12px;background:#fafaf7;border-radius:6px;font-size:14px;color:var(--muted)\\">点击\\"查看答案\\"显示参考答案</div>';}}else{{h+='<div class=ops>';lb.forEach(function(l,oi){{var cl='';if(s){{if(q.a.indexOf(oi)>=0)cl='correct-answer';else if(u.indexOf(oi)>=0)cl='wrong-answer';}}else if(u.indexOf(oi)>=0)cl='selected';h+='<div class=\\"op '+cl+'\\" data-qi='+qi+' data-oi='+oi+'><span class=opl>'+B[oi]+'</span><span>'+E(l.replace(/^[A-H]\\.\\\\s*/,''))+'</span></div>';}});h+='</div>';}}if(!s)h+='<div style=\\"margin-top:8px\\"><button data-submit='+qi+' style=\\"padding:5px 14px;border:1px solid var(--accent);border-radius:5px;background:var(--accent);color:#fff;font-size:12px;cursor:pointer\\">查看答案</button></div>';if(s){{var ec=s.o?'correct-exp':'wrong-exp';h+='<div class=\\"exp show '+ec+'\\"><strong>正确答案：</strong>'+F(q)+(q.e?'<br><strong>解析：</strong>'+E(q.e):'')+'</div>';}}h+='</div>';}});document.getElementById('p-'+idx).innerHTML=h;}}
function C(k,qi,oi){{var q=P[k].d[qi],a=S[k].a[qi]||[];if(q.s==='single'||q.s==='judge')a=[oi];else{{var p=a.indexOf(oi);if(p>=0)a.splice(p,1);else a.push(oi);}}S[k].a[qi]=a;R(k,Object.keys(P).indexOf(k));}}
function SB(k,qi){{var q=P[k].d[qi];var ok=q.s==='subjective'?true:(q.a.length===(S[k].a[qi]||[]).length&&q.a.every(function(a){{return(S[k].a[qi]||[]).indexOf(a)>=0;}}));S[k].s[qi]={{o:ok}};R(k,Object.keys(P).indexOf(k));}}
function RST(k){{S[k]={{a:{{}},s:{{}}}};R(k,Object.keys(P).indexOf(k));}}
document.addEventListener('click',function(e){{var op=e.target.closest('.op');if(op&&op.dataset.qi!=null){{var k=Object.keys(P)[parseInt(document.querySelector('.tb.active').dataset.p)];C(k,parseInt(op.dataset.qi),parseInt(op.dataset.oi));return;}}var btn=e.target.closest('button[data-submit]');if(btn){{var k=Object.keys(P)[parseInt(document.querySelector('.tb.active').dataset.p)];SB(k,parseInt(btn.dataset.submit));}}}});
I();var ag=document.getElementById('asGrid');if(ag){{var k=Object.keys(P)[0];var p=P[k];for(var i=0;i<p.d.length;i++){{var c='as-num';var s=S[k].s[i];if(s)c+=s.o?' correct':' wrong';(function(i,c){{var d=document.createElement('div');d.className=c;d.textContent=i+1;d.onclick=function(){{document.querySelectorAll('.cd')[i].scrollIntoView({{behavior:'smooth',block:'center'}});}};ag.appendChild(d);}})(i,c);}}}}'''
    
    title = papers[0]['t']
    subtitle = papers[0]['s']
    count = len(papers)
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{title}</title>
<style>{CSS}</style>
</head>
<body>
<div class="c">
<h1>{title}</h1>
<p class="sub">{subtitle} · 共{count}套</p>
<div style="display:flex;align-items:center;gap:8px;margin-bottom:8px"><button class="btn small" onclick="var t=document.getElementById('pvTabs');t.style.display=t.style.display==='none'?'flex':'none';this.textContent=this.textContent==='+ 展开'?'- 收起':'+ 展开'" style="flex-shrink:0">- 收起</button><div class="tabs" id="pvTabs" style="position:static;background:transparent;padding:0;flex-wrap:wrap;overflow:hidden">{tabs}</div></div>
{panels}
</div>
<script>
{js}
</script>
</body>
</html>'''
    
    buf = io.BytesIO(html.encode('utf-8'))
    resp = send_file(buf, mimetype='text/html;charset=utf-8', as_attachment=True, download_name='试卷.html')
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

@app.after_request
def add_cors(resp):
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    resp.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
    return resp

@app.route('/export', methods=['OPTIONS'])
def handle_options():
    return make_response('', 204)

if __name__ == '__main__':
    print('Export server: http://localhost:5001/export')
    app.run(host='0.0.0.0', port=5001)
