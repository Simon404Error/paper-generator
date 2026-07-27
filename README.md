# 试卷生成器

试卷生成 · 智能题库

## 快速开始

**双击 `run.bat`** 即可一键启动（自动安装依赖、启动服务器、打开浏览器）。

或手动启动：

```bash
pip install flask
python app.py
# 浏览器打开 http://localhost:5000
```

## 功能

- **题库管理** — 添加、编辑、删除、批量删除题目，支持单选、多选、判断、主观四种题型
- **智能组卷** — 自定义题型分布和套数，知识点标签筛选，不重复开关
- **预览测试** — 交互答题、实时评分、答案解析
- **导入导出** — 导入 JSON 题库，导出独立交互试卷 HTML
- **即时保存** — 题库文件 `questions.json` 自动持久化，导出试卷支持作答保存

## 技术

Python Flask 后端 + 原生 JS 前端。所有组卷和导出逻辑在服务端 Python 中运行，稳定可靠。

## 文件说明

| 文件 | 说明 |
|------|------|
| `app.py` | Flask 主程序 |
| `run.bat` | Windows 一键启动脚本 |
| `requirements.txt` | Python 依赖 |
| `questions.json` | 题库文件（自动生成） |
| `题库导入模板.json` | 导入模板参考 |

## License

MIT
