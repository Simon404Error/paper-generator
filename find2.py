c = open('index.html', 'r', encoding='utf-8').read()
idx = c.find('papers.length>1')
if idx > 0:
    print(c[idx:idx+120])
else:
    print('not found')
