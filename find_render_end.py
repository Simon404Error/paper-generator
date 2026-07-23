with open('公基试卷生成器.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find renderBank function end
in_func = False
brace_count = 0
for i, line in enumerate(lines):
    if 'function renderBank()' in line:
        in_func = True
        brace_count = 0
        print(f'Start: line {i+1}')
    if in_func:
        brace_count += line.count('{') - line.count('}')
        if brace_count <= 0 and '{' in line:
            print(f'End: line {i+1}: {line.rstrip()}')
            # Show lines around the end
            for j in range(max(0,i-5), min(len(lines), i+3)):
                print(f'  {j+1}: {lines[j].rstrip()}')
            break
