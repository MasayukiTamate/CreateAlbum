"""
ui/main_window.py
メインウィンドウの定義なのじゃ。
3ペインレイアウトを組み立て、各パネルを配置して連携させるのじゃ。
"""

import tkinter as tk
from ui.album_tab_panel import AlbumTabPanel
from ui.image_grid_panel import ImageGridPanel
from ui.explorer_panel import ExplorerPanel


class MainWindow(tk.Tk):
    """
    アプリのメインウィンドウなのじゃ。
    3ペイン構成:
        左: AlbumTabPanel  (アルバムリスト)
        中: ImageGridPanel (画像グリッド)
        右: ExplorerPanel  (ファイルエクスプローラ)
    """

    def __init__(self, album_manager, config=None):
        """
        :param album_manager: AlbumManager のインスタンス
        :param config:        ConfigManager のインスタンス (オプション)
        """
        super().__init__()
        self.album_manager = album_manager
        self.config = config
        self.log_manager = None # app.pyで後からセットされるのじゃ

        # ウィンドウの基本設定なのじゃ
        self.title("📸 CreateAlbum")
        self.geometry("1280x800")
        self.minsize(900, 600)
        self.configure(bg="#181825")

        self._build_ui()

        # 起動時: 最初のアルバムを選択状態にするのじゃ
        names = self.album_manager.get_album_names()
        if names:
            self.image_grid.show_album(names[0])

    def _build_ui(self):
        """3ペインレイアウトを組み立てるのじゃ。"""

        # ──── タイトルバー ────
        title_bar = tk.Frame(self, bg="#11111b", height=40)
        title_bar.pack(fill="x")
        title_bar.pack_propagate(False)

        tk.Label(
            title_bar,
            text="📸  CreateAlbum",
            bg="#11111b",
            fg="#cba6f7",
            font=("Yu Gothic UI", 14, "bold"),
            anchor="w",
            padx=16,
        ).pack(side="left", fill="y")

        # ヘッダー内の右側に配置するためのフレーム
        header_right = tk.Frame(title_bar, bg="#11111b")
        header_right.pack(side="right", fill="y", padx=16)

        # 応答時間表示用ラベルなのじゃ
        self.response_time_label = tk.Label(
            header_right,
            text="応答時間: - ms",
            bg="#11111b",
            fg="#a6adc8",
            font=("Consolas", 10)
        )
        self.response_time_label.pack(side="left", padx=10)

        # ログウィンドウの表示/非表示を切り替えるボタンなのじゃ
        self.log_toggle_btn = tk.Button(
            header_right,
            text="📋 ログ表示切替",
            command=self._toggle_log_window,
            bg="#45475a",
            fg="#cdd6f4",
            font=("Yu Gothic UI", 10),
            relief="flat",
            cursor="hand2"
        )
        self.log_toggle_btn.pack(side="right", pady=5)

        # ──── メインコンテンツ (3ペイン) ────
        content = tk.Frame(self, bg="#181825")
        content.pack(fill="both", expand=True)

        # ── 左ペイン: アルバムタブ ──
        self.album_panel = AlbumTabPanel(
            content,
            album_manager=self.album_manager,
            on_select_callback=self._on_album_select,
            width=220,
            bg="#1e1e2e",
        )
        self.album_panel.pack(side="left", fill="y")

        # 仕切り線
        tk.Frame(content, bg="#313244", width=1).pack(side="left", fill="y")

        # ── 右ペイン: エクスプローラ ──
        self.explorer_panel = ExplorerPanel(
            content,
            album_manager=self.album_manager,
            get_current_album_callback=self.album_panel.get_selected,
            refresh_grid_callback=self._refresh_grid,
            width=280,
            bg="#1e1e2e",
        )
        self.explorer_panel.pack(side="right", fill="y")

        # 仕切り線
        tk.Frame(content, bg="#313244", width=1).pack(side="right", fill="y")

        # ── 中央ペイン: 画像グリッド ──
        self.image_grid = ImageGridPanel(
            content,
            album_manager=self.album_manager,
            bg="#181825",
        )
        self.image_grid.pack(side="left", fill="both", expand=True)

    # ──────────────────────────────────────────
    # コールバック / ヘルパー
    # ──────────────────────────────────────────

    def _on_album_select(self, album_name: str):
        """
        アルバムが選択されたときの処理なのじゃ。
        画像グリッドを切り替えるのじゃ。
        :param album_name: 選択されたアルバム名
        """
        # UI構築中に album_panel の初期化から呼ばれることがあるため、
        # image_grid が既にインスタンス化されているか確認してから操作するのじゃ。
        if hasattr(self, 'image_grid'):
            self.image_grid.show_album(album_name)

    def _refresh_grid(self):
        """
        エクスプローラから画像を追加したあとにグリッドを更新するコールバックなのじゃ。
        """
        self.image_grid.refresh()

    def _toggle_log_window(self):
        """ログウィンドウの表示/非表示を切り替えるのじゃ"""
        if self.log_manager:
            self.log_manager.toggle_window()

    def update_response_time(self, milliseconds: float):
        """応答時間をUIに表示するのじゃ"""
        if hasattr(self, 'response_time_label'):
            self.response_time_label.config(text=f"応答時間: {milliseconds:.1f} ms")
