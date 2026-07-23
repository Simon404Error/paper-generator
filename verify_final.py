with open('公基试卷生成器.html', 'r', encoding='utf-8') as f:
    c = f.read()

checks = [
    ('Subtitle changed', c.count('自定义题库 · 智能组卷') >= 1),
    ('No 事业单位', c.count('事业单位') == 0),
    ('Batch checkboxes', c.count('class="qcb"') >= 1),
    ('Batch delete button', c.count('btnBatchDelete') >= 1),
    ('Select all checkbox', c.count('cbSelectAll') >= 1),
    ('updateBatchUI function', c.count('function updateBatchUI()') >= 1),
    ('batchDelete function', c.count('function batchDelete()') >= 1),
    ('toggleSelectAll function', c.count('function toggleSelectAll()') >= 1),
    ('updateBatchUI call in renderBank', c.count('updateBatchUI()') >= 2),
]

all_ok = True
for name, ok in checks:
    flag = 'PASS' if ok else 'FAIL'
    if not ok:
        all_ok = False
    print(f'  [{flag}] {name}')

print(f'\nTotal lines: {c.count(chr(10))}')

# Sanity: check there are no obvious JS errors
# Count braces roughly
opens = c.count('{')
closes = c.count('}')
print(f'Braces: {opens} open, {closes} close')

if all_ok:
    print('\nAll checks passed.')
else:
    print('\nSome checks FAILED.')
