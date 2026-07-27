"""试卷生成器 - Flask 后端"""
import json, os, random, io, re
from flask import Flask, request, jsonify, send_file, render_template_string

app = Flask(__name__)
BANK_FILE = 'questions.json'
PAPERS_FILE = 'papers.json'

def load_bank():
    if os.path.exists(BANK_FILE):
        with open(BANK_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_bank(data):
    with open(BANK_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_papers():
    if os.path.exists(PAPERS_FILE):
        with open(PAPERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_papers(data):
    with open(PAPERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ====== API ======

@app.route('/api/bank', methods=['GET'])
def get_bank():
    return jsonify(load_bank())

@app.route('/api/bank', methods=['POST'])
def add_question():
    bank = load_bank()
    q = request.json
    q['id'] = len(bank) + 1
    bank.append(q)
    save_bank(bank)
    return jsonify({'ok': True, 'id': q['id']})

@app.route('/api/bank/<int:qid>', methods=['PUT'])
def update_question(qid):
    bank = load_bank()
    if 0 <= qid < len(bank):
        bank[qid] = request.json
        save_bank(bank)
        return jsonify({'ok': True})
    return jsonify({'ok': False, 'error': 'not found'}), 404

@app.route('/api/bank/<int:qid>', methods=['DELETE'])
def delete_question(qid):
    bank = load_bank()
    if 0 <= qid < len(bank):
        bank.pop(qid)
        save_bank(bank)
        return jsonify({'ok': True})
    return jsonify({'ok': False}), 404

@app.route('/api/bank/batch-delete', methods=['POST'])
def batch_delete():
    ids = sorted(request.json.get('ids', []), reverse=True)
    bank = load_bank()
    for i in ids:
        if 0 <= i < len(bank):
            bank.pop(i)
    save_bank(bank)
    return jsonify({'ok': True, 'deleted': len(ids)})

@app.route('/api/bank/import', methods=['POST'])
def import_questions():
    data = request.json
    imported = [q for q in data if q.get('s') and q.get('q') and not q.get('_comment')]
    bank = load_bank()
    existing = {q['q'] for q in bank}
    new = [q for q in imported if q['q'] not in existing]
    bank.extend(new)
    save_bank(bank)
    return jsonify({'ok': True, 'imported': len(new), 'skipped': len(imported) - len(new)})

@app.route('/api/generate', methods=['POST'])
def generate():
    cfg = request.json
    nS = int(cfg.get('single', 0) or 0)
    nM = int(cfg.get('multi', 0) or 0)
    nJ = int(cfg.get('judge', 0) or 0)
    nZ = int(cfg.get('subjective', 0) or 0)
    nPapers = int(cfg.get('count', 1) or 1)
    name = cfg.get('name', '').strip() or '试卷'
    subtitle = cfg.get('subtitle', '').strip() or '试卷'
    noDup = cfg.get('nodup', False)
    topics = cfg.get('topics', [])
    
    bank = load_bank()
    pool = bank
    if topics:
        pool = [q for q in bank if q.get('tag') and any(t in q['tag'].replace('，',',').split(',') for t in topics)]
    
    singles = [q for q in pool if q['s'] == 'single']
    multis = [q for q in pool if q['s'] == 'multi']
    judges = [q for q in pool if q['s'] == 'judge']
    subjectives = [q for q in pool if q['s'] == 'subjective']
    
    if nS > len(singles): return jsonify({'ok': False, 'error': f'单选题不足(需{nS},有{len(singles)})'})
    if nM > len(multis): return jsonify({'ok': False, 'error': f'多选题不足(需{nM},有{len(multis)})'})
    if nJ > len(judges): return jsonify({'ok': False, 'error': f'判断题不足(需{nJ},有{len(judges)})'})
    if nZ > len(subjectives): return jsonify({'ok': False, 'error': f'主观题不足(需{nZ},有{len(subjectives)})'})
    if nS + nM + nJ + nZ == 0: return jsonify({'ok': False, 'error': '请至少选择一种题型'})
    
    if noDup:
        if nS * nPapers > len(singles): return jsonify({'ok': False, 'error': f'单选题不足(不重复需{nS*nPapers},有{len(singles)})'})
        if nM * nPapers > len(multis): return jsonify({'ok': False, 'error': f'多选题不足(不重复需{nM*nPapers},有{len(multis)})'})
        if nJ * nPapers > len(judges): return jsonify({'ok': False, 'error': f'判断题不足(不重复需{nJ*nPapers},有{len(judges)})'})
        if nZ * nPapers > len(subjectives): return jsonify({'ok': False, 'error': f'主观题不足(不重复需{nZ*nPapers},有{len(subjectives)})'})
    
    papers = []
    used_s, used_m, used_j, used_z = set(), set(), set(), set()
    
    for pi in range(nPapers):
        def pick(arr, used, n):
            avail = [i for i in range(len(arr)) if i not in used]
            if len(avail) < n:
                avail = list(range(len(arr)))
            chosen = random.sample(avail, min(n, len(avail)))
            used.update(chosen)
            return [arr[i] for i in chosen]
        
        qs = []
        if nS > 0: qs.extend(pick(singles, used_s, nS))
        if nM > 0: qs.extend(pick(multis, used_m, nM))
        if nJ > 0: qs.extend(pick(judges, used_j, nJ))
        if nZ > 0: qs.extend(pick(subjectives, used_z, nZ))
        random.shuffle(qs)
        
        papers.append({'id': f'p{pi+1}', 't': f'{name} ({pi+1})', 's': subtitle, 'd': qs})
    
    save_papers(papers)
    return jsonify({'ok': True, 'papers': papers})

@app.route('/api/papers', methods=['GET'])
def get_papers():
    return jsonify(load_papers())

@app.route('/api/export', methods=['POST'])
def export_html():
    papers = load_papers()
    if not papers:
        return jsonify({'ok': False, 'error': '请先生成试卷'})
    
    # Build standalone HTML
    lit = json.dumps({p['id']: p for p in papers}, ensure_ascii=False)
    
    css = ':root{--bg:#f5f4f0;--card:#fff;--text:#2c2c2c;--muted:#6b6b6b;--border:#e0ded8;--accent:#2c5f8a;--al:#e8f0f7;--green:#2d7d46;--gb:#edf7f0;--red:#c0392b;--rb:#fef0ef}*{box-sizing:border-box;margin:0;padding:0}body{font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;background:var(--bg);color:var(--text);line-height:1.7;font-size:15px}.c{max-width:860px;margin:0 auto;padding:24px 16px 60px}h1{font-size:21px;text-align:center;margin:20px 0 6px}.sub{text-align:center;color:var(--muted);font-size:13px;margin-bottom:18px}.tabs{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:18px;position:sticky;top:0;z-index:10;background:var(--bg);padding:8px 0}.tb{padding:8px 16px;border:1px solid var(--border);border-radius:6px;background:var(--card);font-size:13px;cursor:pointer}.tb:hover{border-color:var(--accent)}.tb.active{background:var(--accent);color:#fff;border-color:var(--accent)}.pn{display:none}.pn.active{display:block}.sb{position:sticky;top:52px;z-index:9;background:var(--card);border:1px solid var(--border);border-radius:8px;padding:12px 16px;margin-bottom:16px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px;box-shadow:0 1px 4px rgba(0,0,0,.04)}.sb .st{display:flex;gap:16px;font-size:14px}.sb .st strong{color:var(--accent)}.ph{text-align:center;padding:20px;background:var(--card);border:1px solid var(--border);border-radius:8px;margin-bottom:20px;box-shadow:0 1px 3px rgba(0,0,0,.06)}.ph h2{font-size:17px;margin-bottom:6px}.ph .mt{font-size:13px;color:var(--muted)}.cd{background:var(--card);border:1px solid var(--border);border-radius:8px;padding:18px 20px;margin-bottom:12px;box-shadow:0 1px 3px rgba(0,0,0,.06)}.cd.submitted{pointer-events:none}.cd.correct{border-color:var(--green);background:#fcfdf9}.cd.wrong{border-color:var(--red);background:#fefcfc}.qn{font-weight:700;color:var(--accent);font-size:13px;margin-bottom:4px;display:flex;align-items:center;gap:8px}.qt{display:inline-block;font-size:11px;font-weight:600;padding:2px 8px;border-radius:4px}.qt.single{color:#5b3ec4;background:#f3f0ff}.qt.multi{color:#b85c1e;background:#fff4ed}.qt.judge{color:#2d7d46;background:#edf7f0}.qt.subjective{color:#8b4513;background:#fff8f0}.qq{font-size:15px;margin:8px 0 12px;font-weight:500}.ops{list-style:none;padding:0;display:flex;flex-direction:column;gap:6px}.op{display:flex;align-items:flex-start;gap:10px;padding:9px 14px;border:1px solid var(--border);border-radius:6px;cursor:pointer;font-size:14px}.op:hover{border-color:var(--accent)}.op.selected{border-color:var(--accent);background:var(--al)}.op.correct-answer{border-color:var(--green);background:var(--gb)}.op.wrong-answer{border-color:var(--red);background:var(--rb)}.opl{font-weight:600;color:var(--muted);min-width:22px}.exp{margin-top:12px;padding:12px;border-radius:6px;background:#fafaf7;font-size:13px;display:none;border-left:3px solid var(--accent)}.exp.show{display:block}.exp.correct-exp{border-left-color:var(--green);background:var(--gb)}.exp.wrong-exp{border-left-color:var(--red);background:var(--rb)}.pv-filter{display:flex;gap:8px;flex-wrap:nowrap;margin-bottom:8px;padding:8px 0;overflow-x:auto}.pv-filter label{font-size:12px;cursor:pointer;user-select:none;display:inline-flex;align-items:center;gap:4px;padding:4px 8px;border:1px solid var(--border);border-radius:4px;background:var(--card)}.pv-filter label.off{opacity:.4}'
    
    tabs = ''.join(f'<div class="tb{" active" if i==0 else ""}" data-p="{i}">{p["t"]}</div>' for i, p in enumerate(papers))
    panels = ''.join(f'<div class="pn{" active" if i==0 else ""}" id="p-{i}"></div>' for i in range(len(papers)))
    
    # Generate the JS code
    labels = {'single': '单选题', 'multi': '多选题', 'judge': '判断题', 'subjective': '主观题'}
    lb = ['A','B','C','D','E','F','G','H']
    
    js_lines = []
    js_lines.append(f'var P={lit};')
    js_lines.append(f'var L={{s:"{labels["single"]}",m:"{labels["multi"]}",j:"{labels["judge"]}",z:"{labels["subjective"]}"}};')
    js_lines.append(f'var B={json.dumps(lb)};')
    js_lines.append('var S={};')
    js_lines.append("function E(s){return(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}")
    js_lines.append("function F(q){if(q.s==='subjective')return q.a[0]||'略';if(q.s==='judge')return q.a[0]===0?'正确':'错误';return(q.a||[]).map(function(i){return B[i];}).join('');}")
    
    # I = init
    js_lines.append("function I(){Object.keys(P).forEach(function(k,i){S[k]={a:{},s:{}};R(k,i);});")
    js_lines.append("document.getElementById('tabs').addEventListener('click',function(e){var t=e.target.closest('.tb');if(!t)return;")
    js_lines.append("document.querySelectorAll('#tabs .tb').forEach(function(x){x.classList.remove('active');});")
    js_lines.append("t.classList.add('active');document.querySelectorAll('.pn').forEach(function(x){x.classList.remove('active');});")
    js_lines.append("document.getElementById('p-'+t.dataset.p).classList.add('active');});}")
    
    # R = renderPaper
    js_lines.append("function R(k,idx){var p=P[k],st=S[k],n=p.d.length,sb=Object.keys(st.s).length,c=0;")
    js_lines.append("for(var x in st.s){if(st.s[x].o)c++;}var h='';")
    js_lines.append("h+='<div class=ph><h2>'+E(p.t)+'</h2><div class=mt>'+E(p.s)+' · 共'+n+'题</div></div>';")
    js_lines.append("h+='<div class=sb><div class=st>已答: <strong>'+sb+'/'+n+'</strong> 正确: <strong>'+c+'</strong> 得分: <strong>'+(sb>0?Math.round(c/sb*100):0)+'%</strong></div><div class=ac><button onclick=RST(\"'+k+'\") style=\"padding:5px 14px;border:1px solid var(--red);border-radius:5px;background:var(--card);color:var(--red);font-size:12px;cursor:pointer\">重做</button></div></div>';")
    js_lines.append("var ft=[];document.querySelectorAll('#pvFilter input[type=checkbox]:checked').forEach(function(cb){ft.push(cb.value);});")
    js_lines.append("p.d.forEach(function(q,qi){if(ft.length>0&&ft.indexOf(q.s)<0)return;")
    js_lines.append("var s=st.s[qi],u=st.a[qi]||[],cc=s?(s.o?'correct':'wrong'):'';")
    js_lines.append("var lb=q.s==='judge'?['正确','错误']:q.s==='subjective'?[]:q.o.map(function(o,oi){return B[oi]+'. '+o;});")
    js_lines.append("h+='<div class=\"cd '+(s?'submitted ':'')+cc+'\"><div class=qn><span>'+(qi+1)+'.</span><span class=\"qt '+q.s+'\">'+L[q.s[0]]+'</span>'+(s?(s.o?'<span style=\"color:var(--green);font-size:12px\"> ✓</span>':'<span style=\"color:var(--red);font-size:12px\"> ✗</span>'):'')+'</div><div class=qq>'+E(q.q)+'</div>';")
    js_lines.append("if(q.s==='subjective'){h+='<div style=\"margin-top:8px;padding:8px 12px;background:#fafaf7;border-radius:6px;font-size:14px;color:var(--muted)\">点击\"查看答案\"显示参考答案</div>';}")
    js_lines.append("else{h+='<div class=ops>';lb.forEach(function(l,oi){var cl='';if(s){if(q.a.indexOf(oi)>=0)cl='correct-answer';else if(u.indexOf(oi)>=0)cl='wrong-answer';}else if(u.indexOf(oi)>=0)cl='selected';h+='<div class=\"op '+cl+'\" data-qi='+qi+' data-oi='+oi+'><span class=opl>'+B[oi]+'</span><span>'+E(l.replace(/^[A-H]\\.\\s*/,''))+'</span></div>';});h+='</div>';}")
    js_lines.append("if(!s)h+='<div style=\"margin-top:8px\"><button data-submit='+qi+' style=\"padding:5px 14px;border:1px solid var(--accent);border-radius:5px;background:var(--accent);color:#fff;font-size:12px;cursor:pointer\">查看答案</button></div>';")
    js_lines.append("if(s){var ec=s.o?'correct-exp':'wrong-exp';h+='<div class=\"exp show '+ec+'\"><strong>正确答案：</strong>'+F(q)+(q.e?'<br><strong>解析：</strong>'+E(q.e):'')+'</div>';}h+='</div>';});")
    js_lines.append("document.getElementById('p-'+idx).innerHTML=h;}")
    
    # C = clickOpt
    js_lines.append("function C(k,qi,oi){var q=P[k].d[qi],a=S[k].a[qi]||[];if(q.s==='single'||q.s==='judge')a=[oi];else{var p=a.indexOf(oi);if(p>=0)a.splice(p,1);else a.push(oi);}S[k].a[qi]=a;R(k,Object.keys(P).indexOf(k));saveST();}")
    # SB = submitOne
    js_lines.append("function SB(k,qi){var q=P[k].d[qi];var ok=q.s==='subjective'?true:(q.a.length===(S[k].a[qi]||[]).length&&q.a.every(function(a){return(S[k].a[qi]||[]).indexOf(a)>=0;}));S[k].s[qi]={o:ok};R(k,Object.keys(P).indexOf(k));saveST();}")
    # RST = reset
    js_lines.append("function RST(k){S[k]={a:{},s:{}};R(k,Object.keys(P).indexOf(k));saveST();}")
    # saveST / loadST
    js_lines.append("function saveST(){try{var d={};Object.keys(S).forEach(function(k){d[k]={a:S[k].a,s:S[k].s};});localStorage.setItem('gk_xs',JSON.stringify(d));}catch(e){}}")
    js_lines.append("function loadST(){try{var d=JSON.parse(localStorage.getItem('gk_xs'));if(d){Object.keys(d).forEach(function(k){S[k]=d[k];});return true;}}catch(e){}return false;}")
    # pvTF = filter toggle
    js_lines.append("function pvTF(){var cbs=document.querySelectorAll('#pvFilter input[type=checkbox]');cbs.forEach(function(cb){cb.parentElement.classList.toggle('off',!cb.checked);});Object.keys(P).forEach(function(k){R(k,Object.keys(P).indexOf(k));});}")
    # Click delegation
    js_lines.append("document.addEventListener('click',function(e){var op=e.target.closest('.op');if(op&&op.dataset.qi!=null){var k=Object.keys(P)[parseInt(document.querySelector('.tb.active').dataset.p)];C(k,parseInt(op.dataset.qi),parseInt(op.dataset.oi));return;}var btn=e.target.closest('button[data-submit]');if(btn){var k=Object.keys(P)[parseInt(document.querySelector('.tb.active').dataset.p)];SB(k,parseInt(btn.dataset.submit));}});")
    js_lines.append("loadST();I();")
    
    js = '\n'.join(js_lines)
    
    title = papers[0]['t'] if papers else '试卷'
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{title}</title>
<style>{css}</style>
</head>
<body>
<div class="c">
<div class="pv-filter" id="pvFilter" style="display:flex">
<label class="off"><input type="checkbox" value="single" onchange="pvTF()">单选题</label>
<label class="off"><input type="checkbox" value="multi" onchange="pvTF()">多选题</label>
<label class="off"><input type="checkbox" value="judge" onchange="pvTF()">判断题</label>
<label class="off"><input type="checkbox" value="subjective" onchange="pvTF()">主观题</label>
</div>
<h1>{title}</h1>
<p class="sub">{papers[0]["s"] if papers else ""} · 共{len(papers)}套</p>
<div class="tabs" id="tabs">{tabs}</div>
{panels}
</div>
<script>
{js}
</script>
</body>
</html>'''
    
    buf = io.BytesIO(html.encode('utf-8'))
    return send_file(buf, mimetype='text/html;charset=utf-8', as_attachment=True, download_name='试卷.html')

@app.route('/api/topics', methods=['GET'])
def get_topics():
    bank = load_bank()
    topics = set()
    for q in bank:
        if q.get('tag'):
            for t in q['tag'].replace('，', ',').split(','):
                t = t.strip()
                if t:
                    topics.add(t)
    return jsonify(sorted(topics))

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

HTML_TEMPLATE = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>试卷生成器 · Python版</title>
<style>
:root{--bg:#f5f4f0;--card:#fff;--text:#2c2c2c;--muted:#6b6b6b;--border:#e0ded8;--accent:#2c5f8a;--al:#e8f0f7;--green:#2d7d46;--gb:#edf7f0;--red:#c0392b;--rb:#fef0ef}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;background:var(--bg);color:var(--text);line-height:1.7;font-size:15px}
.c{max-width:960px;margin:0 auto;padding:24px 16px 60px}
h1{font-size:21px;text-align:center;margin:20px 0 6px}
.sub{text-align:center;color:var(--muted);font-size:13px;margin-bottom:18px}
.tabs{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:18px;position:sticky;top:0;z-index:10;background:var(--bg);padding:8px 0}
.tb{padding:8px 16px;border:1px solid var(--border);border-radius:6px;background:var(--card);font-size:13px;cursor:pointer;user-select:none}
.tb:hover{border-color:var(--accent)}.tb.active{background:var(--accent);color:#fff;border-color:var(--accent)}
.pn{display:none}.pn.active{display:block}
.card{background:var(--card);border:1px solid var(--border);border-radius:8px;padding:18px 20px;margin-bottom:12px;box-shadow:0 1px 3px rgba(0,0,0,.06)}
.row{display:flex;gap:12px;flex-wrap:wrap;align-items:center}.row>*{flex:1;min-width:120px}
.btn{padding:8px 18px;border:1px solid var(--border);border-radius:6px;background:var(--card);cursor:pointer;font-size:13px;font-family:inherit}
.btn:hover{border-color:var(--accent);background:var(--al)}.btn.accent{background:var(--accent);color:#fff;border-color:var(--accent)}
.btn.danger{color:var(--red);border-color:var(--red)}.btn.danger:hover{background:var(--rb)}.btn.small{padding:4px 12px;font-size:12px}
input,select,textarea{font-family:inherit;font-size:14px;padding:8px 12px;border:1px solid var(--border);border-radius:6px;background:var(--card);width:100%}
input:focus,select:focus,textarea:focus{border-color:var(--accent);outline:none}textarea{resize:vertical;min-height:60px}
.qt{display:inline-block;font-size:11px;font-weight:600;padding:2px 8px;border-radius:4px}
.qt.single{color:#5b3ec4;background:#f3f0ff}.qt.multi{color:#b85c1e;background:#fff4ed}.qt.judge{color:#2d7d46;background:#edf7f0}.qt.subjective{color:#8b4513;background:#fff8f0}
.stats{display:flex;gap:16px;flex-wrap:wrap;margin-bottom:16px}
.stat-item{background:var(--card);border:1px solid var(--border);border-radius:8px;padding:12px 16px;text-align:center;min-width:80px}
.stat-item .num{font-size:24px;font-weight:700;color:var(--accent)}.stat-item .lbl{font-size:12px;color:var(--muted)}
.qlist{max-height:600px;overflow-y:auto}
.qitem{display:flex;align-items:flex-start;gap:12px;padding:12px 0;border-bottom:1px solid var(--border)}
.qitem:last-child{border-bottom:none}.qitem .qi{flex:1}.qitem .qi .qtxt{font-weight:500;word-break:break-all}
.qitem .qi .qmeta{font-size:12px;color:var(--muted);margin-top:4px}.qitem .qact{display:flex;gap:4px;flex-shrink:0}
.cfg-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.cfg-item{display:flex;flex-direction:column;gap:4px}.cfg-item label{font-size:13px;color:var(--muted)}
.tags{display:flex;flex-wrap:wrap;gap:4px}.tag{padding:2px 8px;border-radius:4px;font-size:11px;background:#eee;color:var(--muted);cursor:pointer;user-select:none}.tag.selected{background:var(--accent);color:#fff}
.pp-card{padding:12px 16px;border:1px solid var(--border);border-radius:6px;margin-bottom:8px;cursor:pointer}.pp-card:hover{border-color:var(--accent);background:var(--al)}
.toast{position:fixed;bottom:24px;left:50%;transform:translateX(-50%);background:#333;color:#fff;padding:10px 24px;border-radius:8px;font-size:14px;z-index:200;opacity:0;transition:opacity .3s;pointer-events:none}
.toast.show{opacity:1}
.modal-overlay{display:none;position:fixed;inset:0;background:rgba(0,0,0,.3);z-index:100;justify-content:center;align-items:flex-start;padding-top:40px}
.modal-overlay.show{display:flex}
.modal{background:var(--card);border-radius:10px;padding:24px;width:700px;max-width:95vw;max-height:85vh;overflow-y:auto;box-shadow:0 8px 32px rgba(0,0,0,.15)}
.modal h3{font-size:17px;margin-bottom:16px}.form-group{margin-bottom:12px}.form-group label{display:block;font-size:13px;color:var(--muted);margin-bottom:4px}
.form-actions{display:flex;gap:8px;justify-content:flex-end;margin-top:16px}
</style>
</head>
<body>
<div class="c">
<h1>&#x1F4CB; 试卷生成器</h1>
<p class="sub">试卷生成 · 智能题库 · Python版</p>

<div class="tabs" id="mainTabs">
  <div class="tb active" data-tab="bank">题库管理</div>
  <div class="tb" data-tab="generate">试卷生成</div>
  <div class="tb" data-tab="preview">预览测试</div>
  <div class="tb" data-tab="io">导入导出</div>
</div>

<div class="pn active" id="tab-bank">
  <div class="stats" id="bankStats"></div>
  <div class="row" style="margin-bottom:12px">
    <select id="filterType" onchange="renderBank()"><option value="all">全部</option><option value="single">单选题</option><option value="multi">多选题</option><option value="judge">判断题</option><option value="subjective">主观题</option></select>
    <input type="text" id="filterKeyword" placeholder="搜索..." oninput="renderBank()">
    <button class="btn accent" onclick="openModal(-1)">＋ 添加</button>
    <button class="btn danger" id="btnBatchDel" style="display:none" onclick="batchDel()">🗑 批量删除</button>
  </div>
  <div class="card"><div class="qlist" id="qlist"><div class="empty" style="text-align:center;padding:40px;color:var(--muted)">暂无题目</div></div></div>
  <div id="batchBar" style="display:none;margin-top:8px"><label><input type="checkbox" id="selectAll" onchange="toggleSelectAll()"> 全选</label> <span id="selCount"></span></div>
</div>

<div class="pn" id="tab-generate">
  <div class="card">
    <h3 style="margin-bottom:12px">组卷配置</h3>
    <div class="cfg-grid">
      <div class="cfg-item"><label>名称前缀</label><input id="cfgName" value="试卷"></div>
      <div class="cfg-item"><label>生成套数</label><input type="number" id="cfgCount" value="1" min="1" max="20"></div>
      <div class="cfg-item"><label>单选题数</label><input type="number" id="cfgSingle" value="1" min="0" max="100"></div>
      <div class="cfg-item"><label>多选题数</label><input type="number" id="cfgMulti" value="1" min="0" max="50"></div>
      <div class="cfg-item"><label>判断题数</label><input type="number" id="cfgJudge" value="1" min="0" max="30"></div>
      <div class="cfg-item"><label>主观题数</label><input type="number" id="cfgSubjective" value="0" min="0" max="30"></div>
      <div class="cfg-item"><label>副标题</label><input id="cfgSubtitle" value="试卷"></div>
    </div>
    <div style="margin-top:12px"><label style="font-size:13px;color:var(--muted);display:block;margin-bottom:4px">选题范围（留空全选）</label><div class="tags" id="topicTags"></div></div>
    <div style="margin-top:8px"><label style="font-size:15px;cursor:pointer;user-select:none;display:inline-flex;align-items:center;gap:6px;background:var(--al);padding:6px 12px;border-radius:6px;white-space:nowrap"><input type="checkbox" id="cfgNoDup"> 每套试卷题目不重复</label></div>
    <div class="stats" id="genStats" style="margin-top:12px"></div>
    <div style="margin-top:12px"><button class="btn accent" onclick="doGenerate()">&#x1F3B2; 随机组卷</button></div>
  </div>
  <div id="paperPreview"></div>
</div>

<div class="pn" id="tab-preview"><div id="previewContent"><div class="empty" style="text-align:center;padding:40px;color:var(--muted)">请先生成试卷</div></div></div>

<div class="pn" id="tab-io">
  <div class="card">
    <h3 style="margin-bottom:12px">导入题库</h3>
    <p style="font-size:13px;color:var(--muted);margin-bottom:8px">选择 JSON 题库文件导入</p>
    <input type="file" id="importFile" accept=".json" onchange="doImport(event)" style="display:none">
    <button class="btn" onclick="document.getElementById('importFile').click()">选择文件导入</button>
    <div id="importResult" style="margin-top:8px;font-size:13px"></div>
  </div>
  <div class="card">
    <h3 style="margin-bottom:12px">导出</h3>
    <button class="btn accent" onclick="doExport()">&#x1F4C4; 导出试卷 HTML</button>
  </div>
</div>

<div class="modal-overlay" id="qModal"><div class="modal">
<h3 id="modalTitle">添加题目</h3>
<input type="hidden" id="editIdx" value="-1">
<div class="form-group"><label>题型</label><select id="qType"><option value="single">单选题</option><option value="multi">多选题</option><option value="judge">判断题</option><option value="subjective">主观题</option></select></div>
<div class="form-group"><label>题目</label><textarea id="qText" rows="3"></textarea></div>
<div class="form-group" id="optGroup"><label>选项（每行一个）</label><textarea id="qOptions" rows="4"></textarea></div>
<div class="form-group" id="ansGroup"><label>正确答案 (A=0,B=1... 逗号分隔)</label><input id="qAnswer"></div>
<div class="form-group"><label>解析</label><textarea id="qExplain" rows="2"></textarea></div>
<div class="form-group"><label>标签（逗号分隔）</label><input id="qTag"></div>
<div class="form-actions"><button class="btn" onclick="closeModal()">取消</button><button class="btn accent" onclick="saveQ()">保存</button></div>
</div></div>

<div class="toast" id="toast"></div>
</div>

<script>
var currentTab='bank';
var papers=[];

function toast(m){var e=document.getElementById('toast');e.textContent=m;e.classList.add('show');clearTimeout(e._t);e._t=setTimeout(function(){e.classList.remove('show');},2000);}

// Tabs
document.getElementById('mainTabs').addEventListener('click',function(e){
var t=e.target.closest('.tb');if(!t)return;
document.querySelectorAll('#mainTabs .tb').forEach(function(x){x.classList.remove('active');});
t.classList.add('active');currentTab=t.dataset.tab;
document.querySelectorAll('.pn').forEach(function(x){x.classList.remove('active');});
document.getElementById('tab-'+currentTab).classList.add('active');
if(currentTab==='bank')renderBank();
if(currentTab==='generate')renderGenerate();
if(currentTab==='preview')renderPreview();
});

// Bank
function renderBank(){
fetch('/api/bank').then(function(r){return r.json();}).then(function(bank){
var type=document.getElementById('filterType').value;
var kw=document.getElementById('filterKeyword').value.toLowerCase();
var f=bank;
if(type!=='all')f=f.filter(function(q){return q.s===type;});
if(kw)f=f.filter(function(q){return(q.q||'').toLowerCase().indexOf(kw)>=0||(q.e||'').toLowerCase().indexOf(kw)>=0||(q.tag||'').toLowerCase().indexOf(kw)>=0;});
var s=bank.filter(function(q){return q.s==='single';}).length;
var m=bank.filter(function(q){return q.s==='multi';}).length;
var j=bank.filter(function(q){return q.s==='judge';}).length;
var z=bank.filter(function(q){return q.s==='subjective';}).length;
document.getElementById('bankStats').innerHTML='<div class="stat-item"><div class="num">'+bank.length+'</div><div class="lbl">总题数</div></div><div class="stat-item"><div class="num">'+s+'</div><div class="lbl">单选题</div></div><div class="stat-item"><div class="num">'+m+'</div><div class="lbl">多选题</div></div><div class="stat-item"><div class="num">'+j+'</div><div class="lbl">判断题</div></div><div class="stat-item"><div class="num">'+z+'</div><div class="lbl">主观题</div></div>';
var list=document.getElementById('qlist');
if(f.length===0){list.innerHTML='<div class="empty" style="text-align:center;padding:40px;color:var(--muted)">没有匹配的题目</div>';return;}
var h='';
f.forEach(function(q,fi){
var idx=bank.indexOf(q);
var label=q.s==='judge'?'正确/错误':q.s==='subjective'?'主观题':(q.o||[]).join(' / ');
var ans=q.s==='judge'?(q.a[0]===0?'正确':'错误'):q.s==='subjective'?(q.a[0]||'略'):(q.a||[]).map(function(i){return String.fromCharCode(65+i);}).join('');
h+='<div class="qitem"><input type="checkbox" class="qcb" data-idx="'+idx+'" onchange="updateBatch()"><div class="qi"><span class="qt '+q.s+'">'+{single:'单选题',multi:'多选题',judge:'判断题',subjective:'主观题'}[q.s]+'</span><div class="qtxt">'+esc(q.q)+'</div><div class="qmeta">答案: '+ans+' | '+esc(label)+(q.tag?' | '+esc(q.tag):'')+'</div></div><div class="qact"><button class="btn small" onclick="openModal('+idx+')">编辑</button><button class="btn small danger" onclick="delQ('+idx+')">删除</button></div></div>';
});
list.innerHTML=h;
document.getElementById('batchBar').style.display='none';
document.getElementById('btnBatchDel').style.display='none';
});
}
function esc(s){return(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}
function updateBatch(){var n=document.querySelectorAll('.qcb:checked').length;document.getElementById('batchBar').style.display=n>0?'block':'none';document.getElementById('btnBatchDel').style.display=n>0?'inline-flex':'none';document.getElementById('selCount').textContent='已选 '+n+' 题';}
function toggleSelectAll(){var a=document.getElementById('selectAll').checked;document.querySelectorAll('.qcb').forEach(function(cb){cb.checked=a;});updateBatch();}
function batchDel(){var ids=[];document.querySelectorAll('.qcb:checked').forEach(function(cb){ids.push(parseInt(cb.dataset.idx));});if(ids.length===0)return;if(!confirm('删除 '+ids.length+' 题？'))return;fetch('/api/bank/batch-delete',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({ids:ids})}).then(function(){renderBank();toast('已删除 '+ids.length+' 题');});}
function delQ(idx){if(!confirm('删除？'))return;fetch('/api/bank/'+idx,{method:'DELETE'}).then(function(){renderBank();toast('已删除');});}

// Modal
function openModal(idx){
document.getElementById('editIdx').value=idx;
if(idx>=0){
fetch('/api/bank').then(function(r){return r.json();}).then(function(bank){
var q=bank[idx];if(!q)return;
document.getElementById('modalTitle').textContent='编辑题目';
document.getElementById('qType').value=q.s;
document.getElementById('qText').value=q.q;
document.getElementById('qOptions').value=(q.o||[]).join('\n');
document.getElementById('qAnswer').value=(q.a||[]).join(',');
document.getElementById('qExplain').value=q.e||'';
document.getElementById('qTag').value=q.tag||'';
updateOptVis();
});
}else{
document.getElementById('modalTitle').textContent='添加题目';
document.getElementById('qType').value='single';
document.getElementById('qText').value='';
document.getElementById('qOptions').value='';
document.getElementById('qAnswer').value='';
document.getElementById('qExplain').value='';
document.getElementById('qTag').value='';
updateOptVis();
}
document.getElementById('qModal').classList.add('show');
}
function closeModal(){document.getElementById('qModal').classList.remove('show');}
document.getElementById('qType').addEventListener('change',updateOptVis);
function updateOptVis(){
var v=document.getElementById('qType').value;
document.getElementById('optGroup').style.display=(v==='single'||v==='multi')?'block':'none';
document.getElementById('ansGroup').style.display=v==='subjective'?'none':'block';
}
function saveQ(){
var idx=parseInt(document.getElementById('editIdx').value);
var q={
s:document.getElementById('qType').value,
q:document.getElementById('qText').value.trim(),
o:document.getElementById('qOptions').value.split('\n').map(function(s){return s.trim();}).filter(function(s){return s;}),
a:(document.getElementById('qAnswer').value||'0').split(',').map(function(s){return parseInt(s.trim());}).filter(function(n){return!isNaN(n);}),
e:document.getElementById('qExplain').value.trim(),
tag:document.getElementById('qTag').value.trim()
};
if(!q.q){toast('请输入题目');return;}
if(q.s==='judge')q.o=['正确','错误'];
if(q.s==='subjective'){q.o=[];q.a=[q.a[0]||''];}

var url='/api/bank';var method='POST';
if(idx>=0){url+='/'+idx;method='PUT';}
fetch(url,{method:method,headers:{'Content-Type':'application/json'},body:JSON.stringify(q)}).then(function(){closeModal();renderBank();toast(idx>=0?'已更新':'已添加');});
}
document.getElementById('qModal').addEventListener('click',function(e){if(e.target===this)closeModal();});

// Generate
function renderGenerate(){
fetch('/api/bank').then(function(r){return r.json();}).then(function(bank){
var s=bank.filter(function(q){return q.s==='single';}).length;
var m=bank.filter(function(q){return q.s==='multi';}).length;
var j=bank.filter(function(q){return q.s==='judge';}).length;
var z=bank.filter(function(q){return q.s==='subjective';}).length;
document.getElementById('genStats').innerHTML='<div class="stat-item"><div class="num">'+bank.length+'</div><div class="lbl">题库总数</div></div><div class="stat-item"><div class="num">'+s+'</div><div class="lbl">单选题</div></div><div class="stat-item"><div class="num">'+m+'</div><div class="lbl">多选题</div></div><div class="stat-item"><div class="num">'+j+'</div><div class="lbl">判断题</div></div><div class="stat-item"><div class="num">'+z+'</div><div class="lbl">主观题</div></div>';
});
fetch('/api/topics').then(function(r){return r.json();}).then(function(topics){
var d=document.getElementById('topicTags');
if(topics.length===0){d.innerHTML='<span style="font-size:12px;color:var(--muted)">无标签</span>';return;}
d.innerHTML=topics.map(function(t){return '<span class="tag" onclick="this.classList.toggle(\'selected\')">'+esc(t)+'</span>';}).join('');
});
}

function getSelTopics(){
var r=[];document.querySelectorAll('#topicTags .tag.selected').forEach(function(el){r.push(el.textContent);});return r;
}

function doGenerate(){
var cfg={
single:parseInt(document.getElementById('cfgSingle').value)||0,
multi:parseInt(document.getElementById('cfgMulti').value)||0,
judge:parseInt(document.getElementById('cfgJudge').value)||0,
subjective:parseInt(document.getElementById('cfgSubjective').value)||0,
count:parseInt(document.getElementById('cfgCount').value)||1,
name:document.getElementById('cfgName').value.trim(),
subtitle:document.getElementById('cfgSubtitle').value.trim(),
nodup:document.getElementById('cfgNoDup').checked,
topics:getSelTopics()
};
fetch('/api/generate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(cfg)}).then(function(r){return r.json();}).then(function(res){
if(!res.ok){toast(res.error);return;}
papers=res.papers;
// Show preview
var h='';
papers.forEach(function(p,i){
var sc=p.d.filter(function(q){return q.s==='single';}).length;
var mc=p.d.filter(function(q){return q.s==='multi';}).length;
var jc=p.d.filter(function(q){return q.s==='judge';}).length;
var zc=p.d.filter(function(q){return q.s==='subjective';}).length;
h+='<div class="pp-card" onclick="previewPaper('+i+')"><strong>'+esc(p.t)+'</strong> <span style="font-size:13px;color:var(--muted)">'+p.d.length+'题 (单选'+sc+' + 多选'+mc+' + 判断'+jc+' + 主观'+zc+')</span></div>';
});
document.getElementById('paperPreview').innerHTML='<h4 style="margin-top:12px">已生成试卷</h4>'+h;
toast('已生成 '+papers.length+' 套试卷');
});
}

// Preview
var pvState=null;
function previewPaper(idx){pvState={pi:idx,ans:{},sub:{}};switchTab('preview');renderPV();}
function switchTab(name){
document.querySelectorAll('#mainTabs .tb').forEach(function(t){t.classList.remove('active');});
var el=document.querySelector('#mainTabs .tb[data-tab="'+name+'"]');if(el)el.classList.add('active');
document.querySelectorAll('.pn').forEach(function(p){p.classList.remove('active');});
document.getElementById('tab-'+name).classList.add('active');currentTab=name;
}

function renderPV(){
if(!pvState||!papers[pvState.pi])return;
var p=papers[pvState.pi],st=pvState,total=p.d.length;
var done=Object.keys(st.sub).length,correct=0;
for(var k in st.sub){if(st.sub[k].ok)correct++;}
var h='';
h+='<div class="ph"><h2>'+esc(p.t)+'</h2><div class="mt">'+esc(p.s)+' · 共'+total+'题</div></div>';
h+='<div class="sb"><div class="st">已答: <strong>'+done+'/'+total+'</strong> 正确: <strong>'+correct+'</strong> 得分: <strong>'+(done>0?Math.round(correct/done*100):0)+'%</strong></div><div class="ac"><button class="btn small danger" onclick="resetPV()">重做</button></div></div>';
p.d.forEach(function(q,qi){
var sub=st.sub[qi],ua=st.ans[qi]||[],cc=sub?(sub.ok?'correct':'wrong'):'';
var ol=q.s==='judge'?['正确','错误']:q.s==='subjective'?[]:q.o.map(function(o,oi){return String.fromCharCode(65+oi)+'. '+o;});
h+='<div class="cd '+(sub?'submitted ':'')+cc+'">';
h+='<div class="qn"><span>'+(qi+1)+'.</span><span class="qt '+q.s+'">'+{single:'单选题',multi:'多选题',judge:'判断题',subjective:'主观题'}[q.s]+'</span>'+(sub?(sub.ok?'<span style="color:var(--green);font-size:12px"> ✓ 正确</span>':'<span style="color:var(--red);font-size:12px"> ✗ 错误</span>'):'')+'</div>';
h+='<div class="qq">'+esc(q.q)+'</div>';
if(q.s==='subjective'){h+='<div style="margin-top:8px;padding:8px 12px;background:#fafaf7;border-radius:6px;font-size:14px;color:var(--muted)">点击"查看答案"显示参考答案</div>';}
else{h+='<div class="ops">';ol.forEach(function(l,oi){var cl='';if(sub){if(q.a.indexOf(oi)>=0)cl='correct-answer';else if(ua.indexOf(oi)>=0)cl='wrong-answer';}else if(ua.indexOf(oi)>=0)cl='selected';h+='<div class="op '+cl+'" data-qi="'+qi+'" data-oi="'+oi+'"><span class="opl">'+String.fromCharCode(65+oi)+'</span><span>'+esc(l.replace(/^[A-H]\\.\\s*/,''))+'</span></div>';});h+='</div>';}
if(!sub)h+='<div style="margin-top:8px"><button class="btn accent small" data-submit="'+qi+'">查看答案</button></div>';
if(sub){var ec=sub.ok?'correct-exp':'wrong-exp';h+='<div class="exp show '+ec+'"><strong>正确答案：</strong>'+fmtAns(q)+(q.e?'<br><strong>解析：</strong>'+esc(q.e):'')+'</div>';}
h+='</div>';
});
document.getElementById('previewContent').innerHTML=h;
if(!document.getElementById('previewContent')._pv){
document.getElementById('previewContent')._pv=true;
document.getElementById('previewContent').addEventListener('click',function(e){
if(!pvState)return;
var op=e.target.closest('.op');if(op){var c=op.closest('.cd');if(c&&c.classList.contains('submitted'))return;pvClick(parseInt(op.dataset.qi),parseInt(op.dataset.oi));return;}
var btn=e.target.closest('button[data-submit]');if(btn){pvSubmit(parseInt(btn.dataset.submit));}
});
}
}

function pvClick(qi,oi){var q=papers[pvState.pi].d[qi],a=pvState.ans[qi]||[];if(q.s==='single'||q.s==='judge')a=[oi];else{var p=a.indexOf(oi);if(p>=0)a.splice(p,1);else a.push(oi);}pvState.ans[qi]=a;renderPV();}
function pvSubmit(qi){var q=papers[pvState.pi].d[qi],ua=pvState.ans[qi]||[];var ok=q.s==='subjective'?true:(q.a.length===ua.length&&q.a.every(function(a){return ua.indexOf(a)>=0;}));pvState.sub[qi]={ok:ok};renderPV();}
function resetPV(){pvState.ans={};pvState.sub={};renderPV();}
function fmtAns(q){if(q.s==='subjective')return q.a[0]||'略';if(q.s==='judge')return q.a[0]===0?'正确':'错误';return(q.a||[]).map(function(i){return String.fromCharCode(65+i);}).join('');}

// Import/Export
function doImport(e){var f=e.target.files[0];if(!f)return;var r=new FileReader();r.onload=function(ev){try{var data=JSON.parse(ev.target.result);fetch('/api/bank/import',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)}).then(function(r){return r.json();}).then(function(res){document.getElementById('importResult').innerHTML='<span style="color:var(--green)">导入 '+res.imported+' 题，跳过 '+res.skipped+' 题</span>';renderBank();toast('导入完成');});}catch(err){document.getElementById('importResult').innerHTML='<span style="color:var(--red)">JSON解析失败</span>';}};r.readAsText(f);e.target.value='';}

function doExport(){
fetch('/api/export',{method:'POST'}).then(function(r){
if(!r.ok){r.json().then(function(d){toast(d.error);});return;}
return r.blob();
}).then(function(blob){
if(!blob)return;
var a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='试卷.html';a.click();
toast('试卷已导出');
});
}

// Init
renderBank();
renderGenerate();
</script>
</body>
</html>'''

if __name__ == '__main__':
    print('试卷生成器 Python版')
    print('访问 http://localhost:5000')
    app.run(host='0.0.0.0', port=5000, debug=True)
