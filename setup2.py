import json, os, glob

# Find the file
base = r'D:\这样就干净多了\》》1 上岸上岸上岸\paper-generator-main'
files = os.listdir(base)
json_files = [f for f in files if f.endswith('.json')]
print('JSON files:', json_files)

for jf in json_files:
    path = os.path.join(base, jf)
    data = json.load(open(path, 'r', encoding='utf-8'))
    questions = [q for q in data if q.get('s') and not q.get('_comment')]
    singles = sum(1 for q in questions if q['s'] == 'single')
    multis = sum(1 for q in questions if q['s'] == 'multi')
    judges = sum(1 for q in questions if q['s'] == 'judge')
    subj = sum(1 for q in questions if q['s'] == 'subjective')
    print(f'{jf}: {len(questions)} (s:{singles} m:{multis} j:{judges} z:{subj})')
    
    if len(questions) > 100:
        js = 'localStorage.setItem("gk_bank_v2", ' + json.dumps(json.dumps(questions, ensure_ascii=False)) + ');'
        js += 'localStorage.setItem("gk_tab", "generate");'
        js += 'location.href = "index.html";'
        html = '<!DOCTYPE html><html><head><meta charset="UTF-8"></head><body><p>Loading ' + str(len(questions)) + ' questions...</p><script>' + js + '</script></body></html>'
        with open('setup.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print('setup.html created')
