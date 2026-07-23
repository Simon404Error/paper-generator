with open('公基试卷生成器.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Add updateBatchUI() before closing } of renderBank
# Line 413:   }).join('');
# Line 414: }
old_end = "  }).join('');\n}"
new_end = "  }).join('');\n  updateBatchUI();\n}"
if old_end in content:
    content = content.replace(old_end, new_end, 1)  # Only replace first occurrence (in renderBank)
    print("Added updateBatchUI() at end of renderBank")
else:
    print("WARN: renderBank end pattern not found!")

# Also add batch UI reset when no results found
old_return = "    list.innerHTML = '<div class=\"empty\">没有匹配的题目</div>';\n    return;"
new_return = "    list.innerHTML = '<div class=\"empty\">没有匹配的题目</div>';\n    updateBatchUI();\n    return;"
if old_return in content:
    content = content.replace(old_return, new_return, 1)
    print("Added updateBatchUI() at early return in renderBank")
else:
    print("WARN: early return pattern not found!")

# Remove the unused renderBankWithBatch function I added earlier - clean up
old_batch_func = '''
// Call updateBatchUI after each render to reset UI state
function renderBankWithBatch() {
  renderBank();
  // Reset batch UI state after render
  document.getElementById('qlistHeader').style.display = 'none';
  document.getElementById('btnBatchDelete').style.display = 'none';
  document.getElementById('btnSelectAll').style.display = 'none';
  document.getElementById('cbSelectAll').checked = false;
}

// Override original renderBank calls - actually no, we need to hook into renderBank
// Better: modify renderBank to call updateBatchUI at the end
const _originalRenderBank = renderBank;
// Actually we just need updateBatchUI called at the end of renderBank
// Let me modify the renderBank function directly'''
if old_batch_func in content:
    content = content.replace(old_batch_func, '')
    print("Removed unused renderBankWithBatch placeholder")

# Write back
with open('公基试卷生成器.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("\nDone.")
