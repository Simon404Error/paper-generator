with open('index.html', 'r', encoding='utf-8') as f:
    c = f.read()

# Fix 1: preview mode
old1 = "html += '<div class=\"cd submitted ' + cardClass + '\">'"
new1 = "html += '<div class=\"cd ' + (sub ? 'submitted ' : '') + cardClass + '\">'"
c1 = c.count(old1)
c = c.replace(old1, new1)
print(f'Fix 1 (preview): {c1} replacements')

# Fix 2: export mode - search for the exact pattern
old2 = "h+='<div class=\"cd submitted '+cc+'\""
new2 = "h+='<div class=\"cd '+(sub?'submitted ':'')+cc+'\""
c2 = c.count(old2)
c = c.replace(old2, new2)
print(f'Fix 2 (export): {c2} replacements')

# Verify
print(f'Remaining "cd submitted" in file: {c.count("cd submitted")} (should be 0)')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(c)

print('Done')
