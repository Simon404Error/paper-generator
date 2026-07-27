c = open('export_server.py', 'r', encoding='utf-8').read()

# Add updateAS function definition before I() or after RST
# Find: function RST(k){
old = "function RST(k){{S[k]={{a:{{}},s:{{}}}};R(k,Object.keys(P).indexOf(k));}}"
new = "function RST(k){{S[k]={{a:{{}},s:{{}}}};R(k,Object.keys(P).indexOf(k));}}function updateAS(idx){{var ag=document.getElementById('asGrid');if(!ag)return;ag.innerHTML='';var k=Object.keys(P)[idx];var p=P[k];for(var i=0;i<p.d.length;i++){{var c='as-num';var s=S[k].s[i];if(s)c+=s.o?' correct':' wrong';(function(i,c){{var d=document.createElement('div');d.className=c;d.textContent=i+1;d.onclick=function(){{document.querySelectorAll('.cd')[i].scrollIntoView({{behavior:'smooth',block:'center'}});}};ag.appendChild(d);}})(i,c);}}}}"
n = c.count(old)
c = c.replace(old, new)
print(f'updateAS added: {n}')

# Also add updateAS calls after C (clickOpt) and SB (submit) functions
old_c = "R(k,Object.keys(P).indexOf(k));}}"
new_c = "R(k,Object.keys(P).indexOf(k));updateAS(Object.keys(P).indexOf(k));}}"
c = c.replace(old_c, new_c)
print(f'C/SB calls: {c.count(old_c)}')

with open('export_server.py', 'w', encoding='utf-8') as f:
    f.write(c)

import py_compile
try:
    py_compile.compile('export_server.py', doraise=True)
    print('Python: OK')
except py_compile.PyCompileError as e:
    print('ERR:', e)
