"""
字幕遮挡条 —— 浮于最上层的黑色矩形，可拖动 + 拉伸

操作：
  - 左键拖动          → 移动位置
  - 滚轮              → 调整高度
  - 右键 + 滚轮       → 调整宽度
  - 按住 Ctrl + 滚轮  → 调整透明度
  - 双击              → 隐藏/显示
  - 右键菜单          → 颜色、置顶、锁定、退出
  - 拖动边缘(4px边框) → 拉伸大小

依赖（Python 自带，无需安装）：
  tkinter
"""

import tkinter as tk


class SubtitleBlocker:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("字幕遮挡条")

        # ====== 初始参数 ======
        self.color = "#000000"          # 遮挡条颜色（黑色）
        self.alpha = 0.85               # 不透明度 (0.0 ~ 1.0)
        self.width = 800
        self.height = 80
        self.x = 200
        self.y = 800
        self.min_width = 60
        self.min_height = 20
        self.edge_thickness = 6         # 边缘拖拽感应宽度

        # ====== 窗口设置 ======
        self.root.geometry(f"{self.width}x{self.height}+{self.x}+{self.y}")
        self.root.overrideredirect(True)        # 无标题栏
        self.root.attributes('-topmost', True)   # 始终置顶
        self.root.attributes('-alpha', self.alpha)

        # 背景色决定初始外观（若系统不支持透明色，用纯色做 fallback）
        try:
            self.root.attributes('-transparentcolor', '')
        except tk.TclError:
            pass

        # ====== 画布 ======
        self.canvas = tk.Canvas(
            self.root,
            bg=self.color,
            highlightthickness=0,
            bd=0,
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # ====== 状态 ======
        self._drag_data = {"x": 0, "y": 0}
        self._resize_edge = None   # 'n','s','e','w','ne','nw','se','sw'
        self.locked = False
        self.hidden = False
        self._resize_margin = self.edge_thickness

        # ====== 绑定事件 ======
        self._bind_events()

        # ====== 右键菜单 ======
        self._build_context_menu()

        self.root.mainloop()

    # ---------- 事件绑定 ----------
    def _bind_events(self):
        c = self.canvas
        w = self.root

        # 左键拖动（移动）
        c.bind("<ButtonPress-1>",   self._on_drag_start)
        c.bind("<B1-Motion>",       self._on_drag_move)

        # 边缘检测 — 移动鼠标时更新光标样式
        c.bind("<Motion>",          self._on_motion)

        # 边缘拖拽（拉伸）—— 用 Button-1 的一个变通：如果光标在边缘就是拉伸
        # 我们用统一的 B1-Motion，在 _on_drag_move 里判断是移动还是拉伸
        c.bind("<ButtonRelease-1>", self._on_release)

        # 滚轮调整高度
        c.bind("<MouseWheel>",      self._on_wheel)        # Windows
        c.bind("<Button-4>",        self._on_wheel_up)     # Linux
        c.bind("<Button-5>",        self._on_wheel_down)   # Linux

        # 双击隐藏/显示
        c.bind("<Double-Button-1>", self._toggle_hide)

        # 键盘快捷键（需要焦点）
        w.bind("<Escape>",          lambda e: self.root.destroy())
        # 焦点获取
        c.bind("<Button-1>",        lambda e: c.focus_set(), add="+")

    # ---------- 右键菜单 ----------
    def _build_context_menu(self):
        self.menu = tk.Menu(self.root, tearoff=0)

        color_menu = tk.Menu(self.menu, tearoff=0)
        color_menu.add_command(label="黑色",   command=lambda: self._set_color("#000000"))
        color_menu.add_command(label="深灰",   command=lambda: self._set_color("#333333"))
        color_menu.add_command(label="灰色",   command=lambda: self._set_color("#666666"))
        color_menu.add_command(label="白色",   command=lambda: self._set_color("#FFFFFF"))
        color_menu.add_command(label="自定义…", command=self._pick_color)

        self.menu.add_cascade(label="颜色", menu=color_menu)
        self.menu.add_separator()

        self.menu.add_command(label="透明度 +",  command=lambda: self._adj_alpha(+0.05))
        self.menu.add_command(label="透明度 -",  command=lambda: self._adj_alpha(-0.05))
        self.menu.add_separator()

        self._lock_var = tk.BooleanVar(value=False)
        self.menu.add_checkbutton(label="锁定位置", variable=self._lock_var,
                                  command=self._toggle_lock)
        self._topmost_var = tk.BooleanVar(value=True)
        self.menu.add_checkbutton(label="窗口置顶", variable=self._topmost_var,
                                  command=self._toggle_topmost)
        self.menu.add_separator()

        self.menu.add_command(label="还原大小 (800×80)", command=self._reset_size)
        self.menu.add_command(label="全宽", command=self._maximize_width)
        self.menu.add_separator()
        self.menu.add_command(label="退出", command=self.root.destroy)

        self.canvas.bind("<Button-3>", self._show_menu)   # 右键

    def _show_menu(self, event):
        self.menu.post(event.x_root, event.y_root)

    # ---------- 拖拽 / 拉伸 ----------
    def _on_drag_start(self, event):
        if self.locked:
            return
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y
        # 判断是否在边缘 → 拉伸模式
        edge = self._hit_edge(event.x, event.y)
        self._resize_edge = edge

    def _on_drag_move(self, event):
        if self.locked:
            return

        dx = event.x - self._drag_data["x"]
        dy = event.y - self._drag_data["y"]

        if self._resize_edge:
            self._do_resize(self._resize_edge, dx, dy, event)
        else:
            # 移动窗口
            new_x = self.root.winfo_x() + dx
            new_y = self.root.winfo_y() + dy
            self.root.geometry(f"+{new_x}+{new_y}")

    def _on_release(self, event):
        self._resize_edge = None

    def _hit_edge(self, x, y):
        """返回鼠标所在边缘方向，不在边缘则 None"""
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        m = self._resize_margin

        left   = x <= m
        right  = x >= w - m
        top    = y <= m
        bottom = y >= h - m

        if top and left:    return 'nw'
        if top and right:   return 'ne'
        if bottom and left: return 'sw'
        if bottom and right:return 'se'
        if left:            return 'w'
        if right:           return 'e'
        if top:             return 'n'
        if bottom:          return 's'
        return None

    def _on_motion(self, event):
        if self.locked:
            self.canvas.config(cursor="")
            return
        edge = self._hit_edge(event.x, event.y)
        cursors = {
            'n':  'sb_v_double_arrow',
            's':  'sb_v_double_arrow',
            'e':  'sb_h_double_arrow',
            'w':  'sb_h_double_arrow',
            'ne': 'top_right_corner',
            'nw': 'top_left_corner',
            'se': 'bottom_right_corner',
            'sw': 'bottom_left_corner',
        }
        cursor_name = cursors.get(edge, "")
        self.canvas.config(cursor=cursor_name)

    def _do_resize(self, edge, dx, dy, event):
        """根据边缘方向调整窗口大小和位置"""
        x = self.root.winfo_x()
        y = self.root.winfo_y()
        w = self.root.winfo_width()
        h = self.root.winfo_height()

        new_x, new_y = x, y
        new_w, new_h = w, h

        if 'e' in edge or edge == 'e':
            new_w = max(self.min_width, w + dx)
        if 'w' in edge or edge == 'w':
            new_w = max(self.min_width, w - dx)
            new_x = x + dx
        if 's' in edge or edge == 's':
            new_h = max(self.min_height, h + dy)
        if 'n' in edge or edge == 'n':
            new_h = max(self.min_height, h - dy)
            new_y = y + dy

        self.root.geometry(f"{new_w}x{new_h}+{new_x}+{new_y}")

        # 更新 drag 参考点（避免跳跃）
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    # ---------- 滚轮调整 ----------
    def _on_wheel(self, event):
        """Windows 滚轮"""
        if self.locked:
            return
        # Ctrl + 滚轮 → 调整透明度
        if (event.state & 0x4):   # Ctrl
            delta = 0.03 if event.delta > 0 else -0.03
            self._adj_alpha(delta)
        # 右键按住 + 滚轮 → 调整宽度（在 motion 里不好跟踪右键状态，改用 shift）
        elif (event.state & 0x1):  # Shift
            delta_w = 20 if event.delta > 0 else -20
            self._adj_width(delta_w)
        else:
            delta_h = 10 if event.delta > 0 else -10
            self._adj_height(delta_h)

    def _on_wheel_up(self, event):
        """Linux 滚轮上"""
        if self.locked:
            return
        if (event.state & 0x4):
            self._adj_alpha(+0.03)
        elif (event.state & 0x1):
            self._adj_width(+20)
        else:
            self._adj_height(+10)

    def _on_wheel_down(self, event):
        """Linux 滚轮下"""
        if self.locked:
            return
        if (event.state & 0x4):
            self._adj_alpha(-0.03)
        elif (event.state & 0x1):
            self._adj_width(-20)
        else:
            self._adj_height(-10)

    # ---------- 属性调整 ----------
    def _adj_height(self, dh):
        h = self.root.winfo_height()
        new_h = max(self.min_height, h + dh)
        self.root.geometry(f"{self.root.winfo_width()}x{new_h}")

    def _adj_width(self, dw):
        w = self.root.winfo_width()
        new_w = max(self.min_width, w + dw)
        self.root.geometry(f"{new_w}x{self.root.winfo_height()}")

    def _adj_alpha(self, da):
        self.alpha = max(0.2, min(1.0, self.alpha + da))
        self.root.attributes('-alpha', self.alpha)
        print(f"透明度: {self.alpha:.2f}")

    def _set_color(self, color):
        self.color = color
        self.canvas.config(bg=color)

    def _pick_color(self):
        # 简单版：弹一个输入框
        from tkinter import simpledialog
        c = simpledialog.askstring("自定义颜色", "输入十六进制颜色码 (如 #FF0000):",
                                   initialvalue=self.color)
        if c:
            self._set_color(c)

    # ---------- 模式切换 ----------
    def _toggle_hide(self, event=None):
        if self.hidden:
            self.root.deiconify()
            self.hidden = False
        else:
            self.root.withdraw()
            self.hidden = True

    def _toggle_lock(self):
        self.locked = self._lock_var.get()

    def _toggle_topmost(self):
        self.root.attributes('-topmost', self._topmost_var.get())

    def _reset_size(self):
        self.root.geometry("800x80")
        self.root.attributes('-alpha', 0.85)
        self.alpha = 0.85

    def _maximize_width(self):
        screen_w = self.root.winfo_screenwidth()
        self.root.geometry(f"{screen_w}x{self.root.winfo_height()}")


if __name__ == '__main__':
    SubtitleBlocker()
