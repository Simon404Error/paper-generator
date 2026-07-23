with open('公基试卷生成器.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find filterType section
idx = content.find('id="filterType"')
print("=== filterType area ===")
print(content[idx-10:idx+350])
print()
print("=== qlist area ===")
idx2 = content.find('id="qlist"')
print(content[idx2-10:idx2+200])
print()
print("=== renderBank function ===")
idx3 = content.find('function renderBank()')
print(content[idx3:idx3+3000])
print()
print("=== deleteQuestion function ===")
idx4 = content.find('function deleteQuestion')
print(content[idx4:idx4+500])
