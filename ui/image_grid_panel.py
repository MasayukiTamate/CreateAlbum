"""
ui/image_grid_panel.py
中央ペイン: 選択中のアルバムに登録された画像をグリッド表示するパネルなのじゃ。
Pillow でサムネイルを生成し、Canvas + scrollbar でスクロール対応するのじゃ。
右クリックメニューで画像の削除も可能なのじゃ。
クリックで拡大プレビューを開くのじゃ。
"""

import tkinter as tk
from tkinter import messagebox
from pathlib import Path

try:
    from PIL import Image, ImageTk
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False


# サムネイルの幅・高さ（ピクセル）
THUMB_SIZE = 150
# グリッドの列数
GRID_COLS = 4
# サムネイル周囲のパディング
THUMB_PAD = 8


class ImageGridPanel(tk.Frame):
    """
    中央ペインに配置する画像グリッドパネルなのじゃ。
    現在選択されているアルバムの画像をサムネイルで一覧表示するのじゃ。
    """

    def __init__(self, parent, album_manager, **kwargs):
        """
        :param parent:        親ウィジェット
        :param album_manager: AlbumManager のインスタンス
        """
        super().__init__(parent, **kwargs)
        self.configure(bg="#181825")

        # データ管理オブジェクト
        self.album_manager = album_manager
        # 現在表示中のアルバム名
        self.current_album: str | None = None
        # サムネイル画像への参照を保持 (GC対策なのじゃ)
        self._thumbnails: list = []

        self._build_ui()

    def _build_ui(self):
        """UIウィジェットを組み立てるのじゃ。"""

        # ── ヘッダー ──
        self.header_label = tk.Label(
            self,
            text="🖼 アルバムを選択してください",
            bg="#181825",
            fg="#a6adc8",
            font=("Yu Gothic UI", 12),
            anchor="w",
            padx=14,
            pady=10,
        )
        self.header_label.pack(fill="x")

        # Pillow が入っていないときの警告
        if not PILLOW_AVAILABLE:
            tk.Label(
                self,
                text="⚠ Pillow がインストールされていないのじゃ！\n   python -m pip install Pillow",
                bg="#181825",
                fg="#f38ba8",
                font=("Yu Gothic UI", 11),
            ).pack(pady=20)

        # ── スクロール可能なキャンバス ──
        canvas_frame = tk.Frame(self, bg="#181825")
        canvas_frame.pack(fill="both", expand=True, padx=6, pady=(0, 6))

        self.canvas = tk.Canvas(
            canvas_frame,
            bg="#181825",
            highlightthickness=0,
        )
        scrollbar = tk.Scrollbar(
            canvas_frame, orient="vertical",
            command=self.canvas.yview,
            bg="#313244",
        )
        self.canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        # キャンバス内のフレーム（実際にサムネイルを並べる場所なのじゃ）
        self.grid_frame = tk.Frame(self.canvas, bg="#181825")
        self.canvas_window = self.canvas.create_window(
            (0, 0), window=self.grid_frame, anchor="nw"
        )

        # フレームサイズ変化でキャンバスのスクロール領域を更新するのじゃ
        self.grid_frame.bind("<Configure>", self._on_frame_configure)
        # キャンバス幅変化でフレーム幅を追従させるのじゃ
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        # マウスホイールスクロールのバインド
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    # ──────────────────────────────────────────
    # 公開メソッド
    # ──────────────────────────────────────────

    def show_album(self, album_name: str):
        """
        指定したアルバムの画像を読み込んでグリッドに表示するのじゃ。
        :param album_name: 表示するアルバムの名前
        """
        self.current_album = album_name
        self.header_label.config(text=f"🖼 {album_name}")
        self._render_grid()

    def refresh(self):
        """
        現在のアルバムを再描画するのじゃ（画像追加・削除後に呼ぶのじゃ）。
        """
        if self.current_album:
            self._render_grid()

    # ──────────────────────────────────────────
    # 内部描画処理
    # ──────────────────────────────────────────

    def _render_grid(self):
        """
        grid_frame の内容をクリアしてサムネイルを並べ直すのじゃ。
        """
        # 既存ウィジェットをすべて削除するのじゃ
        for widget in self.grid_frame.winfo_children():
            widget.destroy()
        self._thumbnails.clear()

        images = self.album_manager.get_images(self.current_album)

        if not images:
            # 画像が0枚のときのメッセージなのじゃ
            tk.Label(
                self.grid_frame,
                text="📂 画像がまだないのじゃ\nエクスプローラからダブルクリックで追加してね",
                bg="#181825",
                fg="#585b70",
                font=("Yu Gothic UI", 12),
                justify="center",
            ).grid(row=0, column=0, padx=40, pady=60)
            return

        for idx, img_path in enumerate(images):
            row = idx // GRID_COLS
            col = idx % GRID_COLS
            cell = self._create_thumb_cell(img_path)
            cell.grid(row=row, column=col, padx=THUMB_PAD, pady=THUMB_PAD)

    def _create_thumb_cell(self, img_path: str) -> tk.Frame:
        """
        1枚の画像に対応するサムネイルセルフレームを作って返すのじゃ。
        :param img_path: 画像ファイルの絶対パス
        :return: セルフレーム
        """
        cell = tk.Frame(
            self.grid_frame,
            bg="#313244",
            bd=0,
            relief="flat",
            cursor="hand2",
        )

        if PILLOW_AVAILABLE and Path(img_path).exists():
            try:
                img = Image.open(img_path)
                img.thumbnail((THUMB_SIZE, THUMB_SIZE))
                photo = ImageTk.PhotoImage(img)
                self._thumbnails.append(photo)  # GC防止なのじゃ

                lbl = tk.Label(
                    cell,
                    image=photo,
                    bg="#313244",
                    cursor="hand2",
                )
                lbl.pack(padx=4, pady=4)
                # クリックで拡大プレビューを開くのじゃ
                lbl.bind("<Button-1>", lambda e, p=img_path: self._open_preview(p))
            except Exception:
                self._error_thumb(cell, img_path)
        else:
            self._error_thumb(cell, img_path)

        # ファイル名ラベル（長い名前は省略するのじゃ）
        name = Path(img_path).name
        display_name = name if len(name) <= 18 else name[:15] + "…"
        name_lbl = tk.Label(
            cell,
            text=display_name,
            bg="#313244",
            fg="#cdd6f4",
            font=("Yu Gothic UI", 8),
        )
        name_lbl.pack(pady=(0, 4))

        # 右クリックでコンテキストメニューを表示するのじゃ
        cell.bind("<Button-3>", lambda e, p=img_path: self._show_context_menu(e, p))
        for child in cell.winfo_children():
            child.bind("<Button-3>", lambda e, p=img_path: self._show_context_menu(e, p))

        return cell

    def _error_thumb(self, parent: tk.Frame, img_path: str):
        """
        画像が読めないときのプレースホルダーを表示するのじゃ。
        """
        tk.Label(
            parent,
            text="🖼\n読込失敗",
            bg="#45475a",
            fg="#f38ba8",
            font=("Yu Gothic UI", 10),
            width=12,
            height=6,
        ).pack(padx=4, pady=4)

    def _open_preview(self, img_path: str):
        """
        クリックされた画像を大きなウィンドウでプレビュー表示するのじゃ。
        :param img_path: 表示する画像のパス
        """
        if not PILLOW_AVAILABLE:
            return
        win = tk.Toplevel(self)
        win.title(Path(img_path).name)
        win.configure(bg="#1e1e2e")
        try:
            img = Image.open(img_path)
            # 最大800x600に収めてプレビューするのじゃ
            img.thumbnail((800, 600))
            photo = ImageTk.PhotoImage(img)
            lbl = tk.Label(win, image=photo, bg="#1e1e2e")
            lbl.image = photo  # GC防止なのじゃ
            lbl.pack(padx=10, pady=10)
        except Exception as ex:
            tk.Label(
                win,
                text=f"表示できないのじゃ…\n{ex}",
                bg="#1e1e2e",
                fg="#f38ba8",
                font=("Yu Gothic UI", 11),
            ).pack(padx=20, pady=20)

    def _show_context_menu(self, event, img_path: str):
        """
        右クリック時にコンテキストメニューを出すのじゃ。
        現在は「アルバムから削除」のみ提供するのじゃ。
        """
        menu = tk.Menu(self, tearoff=0, bg="#313244", fg="#cdd6f4",
                       activebackground="#89b4fa", activeforeground="#1e1e2e")
        menu.add_command(
            label="🗑 このアルバムから削除",
            command=lambda: self._remove_image(img_path),
        )
        menu.tk_popup(event.x_root, event.y_root)

    def _remove_image(self, img_path: str):
        """
        アルバムから画像を削除して再描画するのじゃ。
        :param img_path: 削除する画像パス
        """
        ok = messagebox.askyesno(
            "確認",
            f"このアルバムから削除しますか？\n（ファイル自体は削除されないのじゃ）",
            parent=self,
        )
        if ok and self.current_album:
            self.album_manager.remove_image(self.current_album, img_path)
            self._render_grid()

    # ──────────────────────────────────────────
    # Canvas スクロール関連
    # ──────────────────────────────────────────

    def _on_frame_configure(self, event):
        """grid_frame のサイズが変わったらスクロール領域を更新するのじゃ。"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        """キャンバス幅が変わったら内部フレームの幅を合わせるのじゃ。"""
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _on_mousewheel(self, event):
        """マウスホイールでスクロールするのじゃ。"""
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
