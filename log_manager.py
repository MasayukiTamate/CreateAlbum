"""
log_manager.py
GUIでログを出力するウィンドウを管理するモジュールなのじゃ。
設定によって表示/非表示を切り替えられるのじゃ。
"""

import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import time
from datetime import datetime

class LogManager:
    """
    ログ出力とそのGUIウィンドウを管理するクラスなのじゃ。
    """
    def __init__(self, root, config_manager=None):
        self.root = root
        self.config = config_manager
        self.log_window = None
        self.text_area = None
        
        # 応答時間計測用なのじゃ
        self.start_times = {}

        if self.config and self.config.get("show_log_window", True):
            self.create_log_window()

    def create_log_window(self):
        """ログウィンドウを作成するのじゃ"""
        if self.log_window is not None and self.log_window.winfo_exists():
            return

        self.log_window = tk.Toplevel(self.root)
        self.log_window.title("📜 アプリログなのじゃ")
        self.log_window.geometry("500x300")
        self.log_window.configure(bg="#1e1e2e")
        
        # ウィンドウを閉じるときは破棄ではなく隠すだけにするか、設定を更新するのじゃ
        self.log_window.protocol("WM_DELETE_WINDOW", self.toggle_window)

        # ログ表示エリア
        self.text_area = ScrolledText(self.log_window, state='disabled', bg="#1e1e2e", fg="#a6e3a1", font=("Consolas", 10))
        self.text_area.pack(expand=True, fill='both', padx=5, pady=5)
        
        # 常に手前に表示
        self.log_window.attributes('-topmost', True)

    def log(self, message):
        """ログメッセージを出力するのじゃ"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        
        # コンソールにも出力しておくのじゃ
        print(formatted_message, end="")
        
        if self.text_area is not None and self.log_window.winfo_exists():
            self.text_area.config(state='normal')
            self.text_area.insert(tk.END, formatted_message)
            self.text_area.see(tk.END)
            self.text_area.config(state='disabled')

    def toggle_window(self):
        """ログウィンドウの表示/非表示を切り替えるのじゃ"""
        current_state = self.config.get("show_log_window", True)
        new_state = not current_state
        
        if new_state:
            self.create_log_window()
        else:
            if self.log_window and self.log_window.winfo_exists():
                self.log_window.destroy()
                self.log_window = None
                self.text_area = None
                
        self.config.set("show_log_window", new_state)
        self.log(f"ログウィンドウの表示を {new_state} に変更したのじゃ")

    # 応答時間の計測
    def start_timer(self, operation_name):
        """処理時間を計測開始するのじゃ"""
        self.start_times[operation_name] = time.time()
        
    def end_timer(self, operation_name):
        """処理時間を計測終了し、ログに出力するのじゃ"""
        if operation_name in self.start_times:
            elapsed_time = time.time() - self.start_times[operation_name]
            self.log(f"[応答時間] {operation_name}: {elapsed_time:.4f}秒")
            del self.start_times[operation_name]
