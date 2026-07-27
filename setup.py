import json
data = json.load(open(r'D:/这样就干净多了/》》1 上岸上岸上岸/paper-generator-main/2026年竹溪县事业单位.json', 'r', encoding='utf-8'))
questions = [q for q in data if q.get('s') and not q.get('_comment')]
singles = sum(1 for q in questions if q['s'] == 'single')
multis = sum(1 for q in questions if q['s'] == 'multi')
judges = sum(1 for q in questions if q['s'] == 'judge')
subj = sum(1 for q in questions if q['s'] == 'subjective')
print(f'Total: {len(questions)} (single:{singles} multi:{multis} judge:{judges} subj:{subj})')

js = 'localStorage.setItem("gk_bank_v2", ' + json.dumps(json.dumps(questions, ensure_ascii=False)) + ');'
js += 'localStorage.setItem("gk_tab", "generate");'
js += 'location.href = "index.html";'

html = '<!DOCTYPE html><html><head><meta charset="UTF-8"></head><body><p>Loading...</p><script>' + js + '</script></body></html>'
with open('setup.html', 'w', encoding='utf-8') as f:
    f.write(html)
print('Done')
