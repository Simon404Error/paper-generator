with open('公基试卷生成器.html', 'r', encoding='utf-8') as f:
    content = f.read()

original_lines = content.split('\n')
changes = []

# === 1. Subtitle change on line 168 ===
# "公共基础知识 · 智能组卷" -> "自定义题库 · 智能组卷"
old_sub = '公共基础知识 · 智能组卷'
new_sub = '自定义题库 · 智能组卷'
if old_sub in content:
    content = content.replace(old_sub, new_sub)
    changes.append(f'Line ~168: {old_sub} -> {new_sub}')
else:
    changes.append('WARN: subtitle not found!')

# === 2. Remove remaining 事业单位 from export template (line ~951) ===
# The line has: 共${papers.length}套 · 事业单位考试公共基础知识
old_export = '共${papers.length}套 · 事业单位考试公共基础知识'
new_export = '共${papers.length}套 · 公共基础知识'
if old_export in content:
    content = content.replace(old_export, new_export)
    changes.append(f'Export line: removed 事业单位考试')
else:
    changes.append('WARN: export 事业单位 not found!')

# === 3. Add batch delete UI to bank tab ===
# Find the filter row and add batch actions
# Current HTML area around filterType
old_bank_row = '''    <select id="filterType" onchange="renderBank()">
      <option value="all">全部类型</option>
      <option value="single">单选题</option>
      <option value="multi">多选题</option>
      <option value="judge">判断题</option>
    </select>
    <input type="text" id="filterKeyword" placeholder="搜索题目关键词..." oninput="renderBank()">
    <button class="btn accent" onclick="openQuestionModal()">＋ 添加题目</button>'''

new_bank_row = '''    <select id="filterType" onchange="renderBank()">
      <option value="all">全部类型</option>
      <option value="single">单选题</option>
      <option value="multi">多选题</option>
      <option value="judge">判断题</option>
    </select>
    <input type="text" id="filterKeyword" placeholder="搜索题目关键词..." oninput="renderBank()">
    <button class="btn accent" onclick="openQuestionModal()">＋ 添加题目</button>
    <button class="btn danger" id="btnBatchDelete" style="display:none" onclick="batchDelete()">🗑 批量删除</button>
    <button class="btn small" id="btnSelectAll" style="display:none" onclick="toggleSelectAll()">全选</button>'''

if old_bank_row in content:
    content = content.replace(old_bank_row, new_bank_row)
    changes.append('Added batch delete buttons to bank tab')
else:
    changes.append('WARN: bank row not found!')

# === 4. Add checkbox column to question list header ===
# Find the card with qlist
old_card = '''  <div class="card">
    <div class="qlist" id="qlist"><div class="empty">暂无题目，点击"添加题目"开始</div></div>
  </div>'''

new_card = '''  <div class="card">
    <div class="qlist-header" id="qlistHeader" style="display:none;padding:0 0 8px 0;border-bottom:1px solid var(--border);margin-bottom:4px">
      <label style="font-size:13px;cursor:pointer;user-select:none">
        <input type="checkbox" id="cbSelectAll" onchange="toggleSelectAll()" style="margin-right:6px">全选
      </label>
      <span id="selectedCount" style="font-size:12px;color:var(--muted);margin-left:12px"></span>
    </div>
    <div class="qlist" id="qlist"><div class="empty">暂无题目，点击"添加题目"开始</div></div>
  </div>'''

if old_card in content:
    content = content.replace(old_card, new_card)
    changes.append('Added select-all header to question list')
else:
    changes.append('WARN: qlist card not found!')

# === 5. Add checkbox to each qitem in renderBank ===
# Find the qitem template in renderBank
old_qitem = '''      <div class="qitem">
        <div class="qi">
          <span class="qt ${q.s}">${TYPE_LABELS[q.s]}</span>'''

new_qitem = '''      <div class="qitem">
        <input type="checkbox" class="qcb" data-idx="${idx}" onchange="updateBatchUI()" style="flex-shrink:0;margin-top:3px">
        <div class="qi">
          <span class="qt ${q.s}">${TYPE_LABELS[q.s]}</span>'''

if old_qitem in content:
    content = content.replace(old_qitem, new_qitem)
    changes.append('Added checkboxes to question items')
else:
    changes.append('WARN: qitem template not found!')

# === 6. Add batch delete JS functions ===
# Find a good insertion point - after deleteQuestion function
old_del_func = '''function deleteQuestion(idx) {
  if (!confirm('确定要删除这道题目吗？')) return;
  const bank = loadBank();
  bank.splice(idx, 1);
  saveBank(bank);
  renderBank();
  toast('已删除');
}'''

new_del_func = '''function deleteQuestion(idx) {
  if (!confirm('确定要删除这道题目吗？')) return;
  const bank = loadBank();
  bank.splice(idx, 1);
  saveBank(bank);
  renderBank();
  toast('已删除');
}

function getCheckedIndices() {
  const cbs = document.querySelectorAll('.qcb:checked');
  return [...cbs].map(cb => parseInt(cb.dataset.idx));
}

function updateBatchUI() {
  const checked = getCheckedIndices();
  const header = document.getElementById('qlistHeader');
  const btnDel = document.getElementById('btnBatchDelete');
  const btnSel = document.getElementById('btnSelectAll');
  const countEl = document.getElementById('selectedCount');
  if (checked.length > 0) {
    header.style.display = 'block';
    btnDel.style.display = 'inline-flex';
    btnSel.style.display = 'inline-flex';
    countEl.textContent = `已选 ${checked.length} 题`;
  } else {
    header.style.display = 'none';
    btnDel.style.display = 'none';
    btnSel.style.display = 'none';
  }
}

function toggleSelectAll() {
  const cbs = document.querySelectorAll('.qcb');
  const allChecked = [...cbs].every(cb => cb.checked);
  cbs.forEach(cb => { cb.checked = !allChecked; });
  document.getElementById('cbSelectAll').checked = !allChecked;
  updateBatchUI();
}

function batchDelete() {
  const indices = getCheckedIndices();
  if (indices.length === 0) { toast('请先选择要删除的题目'); return; }
  if (!confirm(`确定要删除选中的 ${indices.length} 道题目吗？此操作不可恢复。`)) return;
  const bank = loadBank();
  // Sort descending to avoid index shift issues
  indices.sort((a, b) => b - a);
  for (const idx of indices) {
    bank.splice(idx, 1);
  }
  saveBank(bank);
  document.getElementById('cbSelectAll').checked = false;
  renderBank();
  toast(`已删除 ${indices.length} 道题目`);
}

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

if old_del_func in content:
    content = content.replace(old_del_func, new_del_func)
    changes.append('Added batch delete JS functions')
else:
    changes.append('WARN: deleteQuestion function not found!')

# === 7. Add updateBatchUI() call at end of renderBank ===
old_end_render = '''  document.getElementById('qlist').innerHTML = filtered.map((q, fi) => {'''

# We need to add updateBatchUI(); at the end of renderBank, before the closing }
# Let's find the exact closing of renderBank
# renderBank ends with: toast(idx >= 0 ? '已更新' : '已添加');
# Then closeQuestionModal closes
# Then renderBank() is called from saveQuestion

# Actually let me find the actual end of renderBank function
old_render_end = '''  document.getElementById('qlist').innerHTML = filtered.map((q, fi) => {
    const idx = bank.indexOf(q);
    const label = q.s === 'judge' ? '正确/错误' : (q.o||[]).join(' / ');
    return `
      <div class="qitem">
        <input type="checkbox" class="qcb" data-idx="${idx}" onchange="updateBatchUI()" style="flex-shrink:0;margin-top:3px">
        <div class="qi">
          <span class="qt ${q.s}">${TYPE_LABELS[q.s]}</span>
          <div class="qtxt">${escHtml(q.q)}</div>
          <div class="qmeta">
            答案: ${formatAnswer(q)} &nbsp;|&nbsp; 选项: ${label}
            ${q.tag ? `&nbsp;|&nbsp; 🏷 ${escHtml(q.tag)}` : ''}
          </div>
        </div>
        <div class="qact">
          <button class="btn small" onclick="openQuestionModal(${idx})">编辑</button>
          <button class="btn small danger" onclick="deleteQuestion(${idx})">删除</button>
        </div>
      </div>`;
  }).join('');
}'''

# Now I need to add updateBatchUI(); call right before the closing } of renderBank
# Let me find it in the content
if old_render_end in content:
    new_render_end = old_render_end + '\n  updateBatchUI();'
    content = content.replace(old_render_end, new_render_end)
    changes.append('Added updateBatchUI() call at end of renderBank')
else:
    # Try to find an alternative pattern
    alt_end = '  }).join(\'\');\n}'
    idx_alt = content.find(alt_end)
    if idx_alt > 0:
        # Check this is inside renderBank
        before = content[max(0,idx_alt-200):idx_alt]
        if 'renderBank' in before or 'qlist' in before:
            content = content[:idx_alt+len(alt_end)-2] + '\n  updateBatchUI();\n}' + content[idx_alt+len(alt_end)+1:]
            changes.append('Added updateBatchUI() call (alt method)')
        else:
            changes.append('WARN: alt end pattern found but not in renderBank')

# === Verify changes ===
new_lines = content.split('\n')
print(f'Lines: {len(original_lines)} -> {len(new_lines)}')
print()
for c in changes:
    print(c)

# Write back
with open('公基试卷生成器.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('\nDone.')
