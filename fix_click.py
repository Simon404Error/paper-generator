with open('index.html', 'r', encoding='utf-8') as f:
    c = f.read()

# Fix 1: preview mode - only add 'submitted' class when actually submitted
old1 = "html += '<div class=\"cd submitted ' + cardClass + '\">'"
new1 = "html += '<div class=\"cd ' + (sub ? 'submitted ' : '') + cardClass + '\">'"
count1 = c.count(old1)
c = c.replace(old1, new1)
print(f'Preview fix: {count1} replacements')

# Fix 2: export HTML - same issue in the exported JS
# The export template has: h+='<div class="cd submitted '+cc+'">
old2 = "h+='<div class=\"cd submitted '+cc+'\""
new2 = "h+='<div class=\"cd '+(sub?'submitted ':'')+cc+'\""
count2 = c.count(old2)
c = c.replace(old2, new2)
print(f'Export fix: {count2} replacements')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(c)

print('Done')
