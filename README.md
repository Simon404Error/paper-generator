# 试卷生成器

试卷生成 · 智能题库 · Python 版

## 快速开始

双击 `run.bat` 一键启动，或：

```bash
pip install flask
python app.py
# 打开 http://localhost:5000
```

## 功能

- 题库管理 — 单选/多选/判断/主观题，批量删除
- 智能组卷 — 自定义题型分布、套数、标签筛选、不重复开关
- 预览测试 — 交互答题、实时评分
- 导入导出 — JSON 题库导入，独立试卷 HTML 导出
- 数据持久化 — `questions.json` 自动保存

## 文件

| 文件 | 说明 |
|------|------|
| `app.py` | Flask 主程序 |
| `run.bat` | Windows 一键启动 |
| `requirements.txt` | 依赖 (flask) |
| `题库导入模板.json` | 导入格式参考 |

## License

MIT
