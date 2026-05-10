import tkinter as tk
from tkinter import ttk
import winsound
import threading


class PomodoroApp:
    def __init__(self, root):
        self.root = root
        self.root.title("番茄钟")
        self.root.geometry("360x520")
        self.root.resizable(False, False)
        self.root.configure(bg="#2b2b2b")

        # 状态: idle / working / paused_work / resting / paused_rest
        self.state = "idle"
        self.remaining_seconds = 0
        self.timer_id = None
        self.completed_count = 0

        # 默认时长（分钟）
        self.work_minutes = tk.IntVar(value=25)
        self.rest_minutes = tk.IntVar(value=5)

        self._build_ui()

    def _build_ui(self):
        # --- 标题 ---
        tk.Label(
            self.root, text="番茄钟", font=("Microsoft YaHei", 20, "bold"),
            bg="#2b2b2b", fg="#ffffff"
        ).pack(pady=(20, 5))

        # --- 计时器显示 ---
        self.time_label = tk.Label(
            self.root, text="25:00", font=("Consolas", 56, "bold"),
            bg="#2b2b2b", fg="#ff6b6b"
        )
        self.time_label.pack(pady=(10, 5))

        # --- 状态标签 ---
        self.status_label = tk.Label(
            self.root, text="准备开始", font=("Microsoft YaHei", 12),
            bg="#2b2b2b", fg="#aaaaaa"
        )
        self.status_label.pack(pady=(0, 15))

        # --- 控制按钮 ---
        btn_frame = tk.Frame(self.root, bg="#2b2b2b")
        btn_frame.pack(pady=5)

        btn_style = {
            "font": ("Microsoft YaHei", 11),
            "width": 8, "height": 1,
            "border": 0, "cursor": "hand2",
            "activebackground": "#555555", "activeforeground": "#ffffff"
        }

        self.start_btn = tk.Button(
            btn_frame, text="开始", bg="#4CAF50", fg="white",
            command=self._on_start, **btn_style
        )
        self.start_btn.grid(row=0, column=0, padx=6)

        self.pause_btn = tk.Button(
            btn_frame, text="暂停", bg="#FF9800", fg="white",
            command=self._on_pause, state="disabled", **btn_style
        )
        self.pause_btn.grid(row=0, column=1, padx=6)

        self.reset_btn = tk.Button(
            btn_frame, text="重置", bg="#f44336", fg="white",
            command=self._on_reset, **btn_style
        )
        self.reset_btn.grid(row=0, column=2, padx=6)

        # --- 分隔线 ---
        ttk.Separator(self.root, orient="horizontal").pack(fill="x", padx=30, pady=15)

        # --- 设置区域 ---
        settings_frame = tk.LabelFrame(
            self.root, text=" 设置 ", font=("Microsoft YaHei", 10),
            bg="#2b2b2b", fg="#cccccc", padx=15, pady=10
        )
        settings_frame.pack(padx=20, fill="x")

        row1 = tk.Frame(settings_frame, bg="#2b2b2b")
        row1.pack(fill="x", pady=3)
        tk.Label(row1, text="工作时长:", font=("Microsoft YaHei", 10),
                 bg="#2b2b2b", fg="#cccccc").pack(side="left")
        tk.Spinbox(
            row1, from_=1, to=90, textvariable=self.work_minutes, width=5,
            font=("Microsoft YaHei", 10), justify="center",
            command=self._on_settings_change
        ).pack(side="left", padx=5)
        tk.Label(row1, text="分钟", font=("Microsoft YaHei", 10),
                 bg="#2b2b2b", fg="#cccccc").pack(side="left")

        row2 = tk.Frame(settings_frame, bg="#2b2b2b")
        row2.pack(fill="x", pady=3)
        tk.Label(row2, text="休息时长:", font=("Microsoft YaHei", 10),
                 bg="#2b2b2b", fg="#cccccc").pack(side="left")
        tk.Spinbox(
            row2, from_=1, to=30, textvariable=self.rest_minutes, width=5,
            font=("Microsoft YaHei", 10), justify="center",
            command=self._on_settings_change
        ).pack(side="left", padx=5)
        tk.Label(row2, text="分钟", font=("Microsoft YaHei", 10),
                 bg="#2b2b2b", fg="#cccccc").pack(side="left")

        # --- 分隔线 ---
        ttk.Separator(self.root, orient="horizontal").pack(fill="x", padx=30, pady=15)

        # --- 统计区域 ---
        stats_frame = tk.LabelFrame(
            self.root, text=" 统计 ", font=("Microsoft YaHei", 10),
            bg="#2b2b2b", fg="#cccccc", padx=15, pady=10
        )
        stats_frame.pack(padx=20, fill="x")

        self.stats_label = tk.Label(
            stats_frame, text="今日完成: 0 个番茄",
            font=("Microsoft YaHei", 12), bg="#2b2b2b", fg="#ffcc00"
        )
        self.stats_label.pack()

    def _on_settings_change(self):
        if self.state == "idle":
            self._update_display(self.work_minutes.get() * 60)

    def _on_start(self):
        if self.state == "idle":
            # 从空闲开始工作
            self.remaining_seconds = self.work_minutes.get() * 60
            self._start_countdown("working")
        elif self.state == "paused_work":
            self._start_countdown("working")
        elif self.state == "paused_rest":
            self._start_countdown("resting")

    def _on_pause(self):
        if self.state == "working":
            self.state = "paused_work"
            self._cancel_timer()
            self._set_status("已暂停（工作）", "#FF9800")
            self.start_btn.config(text="继续", state="normal")
            self.pause_btn.config(state="disabled")
        elif self.state == "resting":
            self.state = "paused_rest"
            self._cancel_timer()
            self._set_status("已暂停（休息）", "#FF9800")
            self.start_btn.config(text="继续", state="normal")
            self.pause_btn.config(state="disabled")

    def _on_reset(self):
        self._cancel_timer()
        self.state = "idle"
        self._update_display(self.work_minutes.get() * 60)
        self._set_status("准备开始", "#aaaaaa")
        self.time_label.config(fg="#ff6b6b")
        self.start_btn.config(text="开始", state="normal")
        self.pause_btn.config(state="disabled")

    def _start_countdown(self, new_state):
        self.state = new_state
        if new_state == "working":
            self._set_status("工作中...", "#ff6b6b")
            self.time_label.config(fg="#ff6b6b")
            self.root.configure(bg="#3b1a1a")
        else:
            self._set_status("休息中...", "#4CAF50")
            self.time_label.config(fg="#4CAF50")
            self.root.configure(bg="#1a3b1a")

        self.start_btn.config(state="disabled")
        self.pause_btn.config(state="normal")
        self._tick()

    def _tick(self):
        if self.remaining_seconds <= 0:
            self._on_timer_end()
            return
        self._update_display(self.remaining_seconds)
        self.remaining_seconds -= 1
        self.timer_id = self.root.after(1000, self._tick)

    def _on_timer_end(self):
        self._play_sound()

        if self.state == "working":
            self.completed_count += 1
            self.stats_label.config(text=f"今日完成: {self.completed_count} 个番茄")
            # 自动切换到休息
            self.remaining_seconds = self.rest_minutes.get() * 60
            self._start_countdown("resting")
        else:
            # 休息结束，回到工作
            self.remaining_seconds = self.work_minutes.get() * 60
            self._set_status("休息结束，准备开始", "#aaaaaa")
            self.time_label.config(fg="#ff6b6b")
            self.root.configure(bg="#2b2b2b")
            self._update_display(self.remaining_seconds)
            self.state = "idle"
            self.start_btn.config(text="开始", state="normal")
            self.pause_btn.config(state="disabled")

    def _update_display(self, seconds):
        m, s = divmod(seconds, 60)
        self.time_label.config(text=f"{m:02d}:{s:02d}")

    def _set_status(self, text, color):
        self.status_label.config(text=text, fg=color)

    def _cancel_timer(self):
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None

    def _play_sound(self):
        def _beep():
            winsound.Beep(800, 300)
            winsound.Beep(1000, 300)
            winsound.Beep(1200, 400)
        threading.Thread(target=_beep, daemon=True).start()


def main():
    root = tk.Tk()
    app = PomodoroApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
