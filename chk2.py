html = open('_e.html', 'r', encoding='utf-8').read()
js = html[html.find('<script>')+8:html.rfind('</script>')]

# Find the tab handler
idx = js.find('document.getElementById(\'p-\'+t.dataset.p).classList.add')
print(js[idx:idx+200])

# Also check the R function signature
idx2 = js.find('function R(k,idx){')
print('\nR:', js[idx2:idx2+100])
