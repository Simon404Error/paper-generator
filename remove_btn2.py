c = open('index.html', 'rb').read()

# Simply remove the button HTML - that's all the user asked for
old = b'<button class="btn accent" onclick="exportPapersHTML()" id="btnExportHTML" disabled>&#x1F4C4; \xe5\xaf\xbc\xe5\x87\xba\xe8\xaf\x95\xe5\x8d\xb7 HTML</button>'
c = c.replace(old, b'')
print(f'Button removed: {c.count(old)}')

# Fix renderPaperList to not crash when btn is null
old2 = b",btn=document.getElementById('btnExportHTML');\nif(papers.length===0){div.innerHTML='<p style=\"font-size:13px;color:var(--muted);margin-top:12px\">"
new2 = b";\nif(papers.length===0){div.innerHTML='<p style=\"font-size:13px;color:var(--muted);margin-top:12px\">"
n2 = c.count(old2)
c = c.replace(old2, new2)
print(f'btn var removed: {n2}')

old3 = b"</p>';btn.disabled=true;return;}\nbtn.disabled=false;"
new3 = b"</p>';return;}\n"
n3 = c.count(old3)
c = c.replace(old3, new3)
print(f'btn disabled removed: {n3}')

print(f'Braces: {c.count(b"{")}/{c.count(b"}")}')

with open('index.html', 'wb') as f: f.write(c)

import subprocess
content = c.decode('utf-8')
script = content[content.find('<script>')+8:content.rfind('</script>')]
with open('_s.js','w',encoding='utf-8') as f: f.write(script)
r = subprocess.run(['node','--check','_s.js'], capture_output=True, text=True)
print('JS:', 'OK' if r.returncode==0 else 'ERROR')
