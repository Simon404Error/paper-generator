with open('公基试卷生成器.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Show lines 410-430
for i in range(409, 430):
    line = lines[i]
    # Encode to ascii to avoid console issues
    safe = line.encode('ascii', errors='replace').decode('ascii')
    print(f'{i+1}: {safe.rstrip()}')
