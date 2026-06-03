<p align="center">
  <img src="https://img.shields.io/badge/Python-3.7+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/依赖-零!-brightgreen.svg" alt="zero deps">
  <img src="https://img.shields.io/badge/许可-MIT-yellow.svg" alt="license">
</p>

---

## 🎯 这是什么

看视频、直播、网课时，字幕挡住了画面？**字幕遮挡条**在你屏幕上放一个黑色半透明矩形，随意拖动、拉伸，把不想看的字幕盖住。

```
┌─────────────────────────────────────────┐
│                                         │
│          （视频画面）                      │
│                                         │
│   ┌───────────────────────────────┐     │
│   │     ██ 字幕遮挡条 ██           │     │  ← 浮于顶层
│   └───────────────────────────────┘     │
│                                         │
└─────────────────────────────────────────┘
```

- 🪶 **零依赖** — 仅用 Python 自带 tkinter，Windows/Mac/Linux 都能跑
- 📌 **始终置顶** — 盖上之后切到其他窗口也不会消失
- 🎨 **可调透明度** — 半透明到完全不透明随意调

## 📥 下载

> [**⬇️ 下载 EXE（Windows 免安装）**](../../releases)

双击运行，什么都没装也能用。

## 🕹️ 操作

| 操作 | 效果 |
|:---|:---|
| **左键拖动** | 移动位置 |
| **拖拽边缘** | 拉伸大小（上下左右 + 四角） |
| **滚轮** | 调整高度 |
| **Shift + 滚轮** | 调整宽度 |
| **Ctrl + 滚轮** | 调整透明度 |
| **双击** | 隐藏 / 显示 |
| **右键** | 弹出菜单 |
| **Esc** | 退出 |

### 右键菜单

| 菜单项 | 说明 |
|:---|:---|
| 颜色 → 黑/深灰/灰/白/自定义 | 换颜色 |
| 透明度 + / - | 微调透明度 |
| 锁定位置 | 锁住后无法拖动（防止误触） |
| 窗口置顶 | 始终在最上层（默认开启） |
| 还原大小 | 恢复默认 800×80 |
| 全宽 | 一键拉满屏幕宽度 |

## 🚀 从源码运行

```bash
python subtitle_blocker_gui.py
```

Python 3.7 以上即可，**不需要 pip install 任何东西**。

## 🔧 自行打包为 EXE

```bash
pip install pyinstaller
pyinstaller --onefile --noconsole --name "字幕遮挡条" subtitle_blocker_gui.py
```

生成的 EXE 在 `dist/` 目录下。

## 📁 项目结构

```
subtitle-blocker/
├── subtitle_blocker_gui.py   # 全部源码（单文件）
├── README.md
├── LICENSE
└── .gitignore
```

## 📄 许可

MIT — 随便用，随便改，随便分发。
