c = open('index.html', 'rb').read()

# The import card has: </div></div></div> after importResult
# Should be: </div></div> (close result div, close card div)
# The extra </div> closes the tab-io container

# Find the triple closing divs pattern
old = b'</div></div></div>\n  <div class="card"><h3 style="margin-bottom:12px">\xe5\xaf\xbc\xe5\x87\xba</h3>'
new = b'</div></div>\n  <div class="card"><h3 style="margin-bottom:12px">\xe5\xaf\xbc\xe5\x87\xba</h3>'
n = c.count(old)
c = c.replace(old, new)
print(f'Extra </div> removed: {n}')

# Verify the IO section div count
io_start = c.find(b'id="tab-io"')
io_end = c.find(b'class="modal-overlay"')
io = c[io_start:io_end]
opens = io.count(b'<div')
closes = io.count(b'</div>')
print(f'IO divs: {opens} open, {closes} close (balanced: {opens==closes})')

print(f'Braces: {c.count(b"{")}/{c.count(b"}")}')

with open('index.html', 'wb') as f: f.write(c)

import subprocess
content = c.decode('utf-8')
script = content[content.find('<script>')+8:content.rfind('</script>')]
with open('_s.js','w',encoding='utf-8') as f: f.write(script)
r = subprocess.run(['node','--check','_s.js'], capture_output=True, text=True)
print('JS:', 'OK' if r.returncode==0 else 'ERROR')
