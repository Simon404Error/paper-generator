# 智能题库

## 依赖

- 浏览器（Edge/Chrome）
- Python 3.10+ + Flask（仅导出功能需要）

```bash
pip install flask
```
## 使用

开箱即用：双击 `index.html` 打开主界面

导出试卷前，需先启动导出服务：
   ```bash
   python export_server.py
   ```
   按钮旁有实时状态指示：🟢 已启动 / 🔴 未启动

## 功能

- 题库管理（单选/多选/判断/主观，批量删除，标签筛选）
- 智能组卷（自定义题型分布、套数、不重复开关、有序/随机排版）
- 预览测试（交互答题、实时评分、题型筛选、折叠标签）
- 导入导出（JSON 题库导入，Python 服务端生成试卷 HTML）

## 文件

| 文件 | 说明 |
|------|------|
| `index.html` | 主程序 |
| `export_server.py` | 导出服务（需 Python Flask） |
| `题库导入模板.json` | 导入格式参考 |

## License

MIT
