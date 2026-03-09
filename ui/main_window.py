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

    def __init__(self, album_manager):
        """
        :param album_manager: AlbumManager のインスタンス
        """
        super().__init__()
        self.album_manager = album_manager

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
        self.image_grid.show_album(album_name)

    def _refresh_grid(self):
        """
        エクスプローラから画像を追加したあとにグリッドを更新するコールバックなのじゃ。
        """
        self.image_grid.refresh()
