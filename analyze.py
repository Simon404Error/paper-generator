with open('公基试卷生成器.html', 'r', encoding='utf-8') as f:
    c = f.read()

print("=== 公共基础知识 occurrences ===")
idx = 0
while True:
    pos = c.find('公共基础知识', idx)
    if pos == -1:
        break
    ctx = c[max(0,pos-30):pos+50]
    line_num = c[:pos].count('\n') + 1
    print(f"  Line {line_num}, pos {pos}")
    idx = pos + 1

print()
print("=== 事业单位 occurrences ===")
idx = 0
while True:
    pos = c.find('事业单位', idx)
    if pos == -1:
        break
    ctx = c[max(0,pos-30):pos+50]
    line_num = c[:pos].count('\n') + 1
    print(f"  Line {line_num}, pos {pos}")
    idx = pos + 1

print()
print("=== 试卷生成器 occurrences ===")
idx = 0
while True:
    pos = c.find('试卷生成器', idx)
    if pos == -1:
        break
    ctx = c[max(0,pos-30):pos+50]
    line_num = c[:pos].count('\n') + 1
    print(f"  Line {line_num}, pos {pos}")
    idx = pos + 1

print()
print("=== 公基 occurrences ===")
idx = 0
while True:
    pos = c.find('公基', idx)
    if pos == -1:
        break
    ctx = c[max(0,pos-10):pos+30]
    line_num = c[:pos].count('\n') + 1
    print(f"  Line {line_num}, pos {pos}")
    idx = pos + 1
