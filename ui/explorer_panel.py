"""
ui/explorer_panel.py
右ペイン: ファイルエクスプローラパネルなのじゃ。
フォルダツリーと、選択フォルダ内の画像一覧を表示するのじゃ。
画像をダブルクリックで現在のアルバムに追加できるのじゃ。
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

try:
    from PIL import Image, ImageTk
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False


# エクスプローラで表示する画像拡張子の集合
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff", ".tif"}

# 画像一覧のサムネイルサイズ
LIST_THUMB_SIZE = 48


class ExplorerPanel(tk.Frame):
    """
    右ペインに配置するファイルエクスプローラパネルなのじゃ。
    フォルダを選択してそのフォルダ内の画像を一覧表示し、
    ダブルクリックで現在のアルバムに画像を追加するのじゃ。
    """

    def __init__(self, parent, album_manager, get_current_album_callback, refresh_grid_callback, **kwargs):
        """
        :param parent:                     親ウィジェット
        :param album_manager:              AlbumManager のインスタンス
        :param get_current_album_callback: 現在選択中のアルバム名を返すコールバック
        :param refresh_grid_callback:      画像グリッドを再描画させるコールバック
        """
        super().__init__(parent, **kwargs)
        self.configure(bg="#1e1e2e")

        # 各種参照を保持するのじゃ
        self.album_manager = album_manager
        self.get_current_album = get_current_album_callback
        self.refresh_grid = refresh_grid_callback

        # 現在表示中のフォルダパス
        self.current_dir: Path | None = None
        # エクスプローラ用サムネイルのGC防止リスト
        self._list_thumbs: list = []

        self._build_ui()

    def _build_ui(self):
        """UIウィジェットを組み立てるのじゃ。"""

        # ── ヘッダー + フォルダ選択ボタン ──
        header_frame = tk.Frame(self, bg="#1e1e2e")
        header_frame.pack(fill="x")

        tk.Label(
            header_frame,
            text="🗂 エクスプローラ",
            bg="#1e1e2e",
            fg="#cdd6f4",
            font=("Yu Gothic UI", 13, "bold"),
            anchor="w",
            padx=12,
            pady=10,
        ).pack(side="left")

        tk.Button(
            header_frame,
            text="📂",
            command=self._choose_folder,
            bg="#a6e3a1",
            fg="#1e1e2e",
            font=("Yu Gothic UI", 12, "bold"),
            relief="flat",
            cursor="hand2",
            padx=6,
        ).pack(side="right", padx=10, pady=8)

        # ── 現在のフォルダパス表示 ──
        self.path_label = tk.Label(
            self,
            text="フォルダを選択してください",
            bg="#1e1e2e",
            fg="#585b70",
            font=("Yu Gothic UI", 9),
            anchor="w",
            padx=12,
            wraplength=240,
            justify="left",
        )
        self.path_label.pack(fill="x")

        # ── フォルダツリー (Treeview) ──
        tree_label = tk.Label(
            self, text="フォルダ", bg="#1e1e2e",
            fg="#a6adc8", font=("Yu Gothic UI", 10, "bold"),
            anchor="w", padx=12,
        )
        tree_label.pack(fill="x", pady=(8, 0))

        tree_frame = tk.Frame(self, bg="#1e1e2e")
        tree_frame.pack(fill="x", padx=6, pady=(2, 0))

        # ttkのスタイルをカスタマイズするのじゃ
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Explorer.Treeview",
            background="#313244",
            foreground="#cdd6f4",
            fieldbackground="#313244",
            rowheight=24,
            font=("Yu Gothic UI", 10),
        )
        style.configure("Explorer.Treeview.Heading", background="#45475a", foreground="#cdd6f4")
        style.map("Explorer.Treeview", background=[("selected", "#89b4fa")], foreground=[("selected", "#1e1e2e")])

        # フォルダツリー本体
        self.tree = ttk.Treeview(
            tree_frame,
            style="Explorer.Treeview",
            selectmode="browse",
            height=8,
        )
        tree_scroll = tk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)
        tree_scroll.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)
        self.tree.heading("#0", text="フォルダ")
        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)
        self.tree.bind("<<TreeviewOpen>>", self._on_tree_open)

        # ── 仕切り線 ──
        tk.Frame(self, bg="#45475a", height=1).pack(fill="x", pady=6, padx=6)

        # ── 画像ファイル一覧 ──
        img_label = tk.Label(
            self, text="画像ファイル", bg="#1e1e2e",
            fg="#a6adc8", font=("Yu Gothic UI", 10, "bold"),
            anchor="w", padx=12,
        )
        img_label.pack(fill="x")

        img_list_frame = tk.Frame(self, bg="#1e1e2e")
        img_list_frame.pack(fill="both", expand=True, padx=6, pady=(4, 6))

        img_scroll = tk.Scrollbar(img_list_frame, orient="vertical", bg="#313244")
        img_scroll.pack(side="right", fill="y")

        # 画像ファイルを並べるListboxなのじゃ
        self.img_listbox = tk.Listbox(
            img_list_frame,
            yscrollcommand=img_scroll.set,
            bg="#313244",
            fg="#cdd6f4",
            selectbackground="#a6e3a1",
            selectforeground="#1e1e2e",
            font=("Yu Gothic UI", 10),
            borderwidth=0,
            highlightthickness=0,
            activestyle="none",
            cursor="hand2",
        )
        self.img_listbox.pack(side="left", fill="both", expand=True)
        img_scroll.config(command=self.img_listbox.yview)

        # ダブルクリックでアルバムに追加するのじゃ
        self.img_listbox.bind("<Double-Button-1>", self._on_image_double_click)

        # ── ヒントテキスト ──
        tk.Label(
            self,
            text="💡 ダブルクリックでアルバムに追加",
            bg="#1e1e2e",
            fg="#585b70",
            font=("Yu Gothic UI", 9),
            anchor="w",
            padx=12,
            pady=4,
        ).pack(fill="x")

        # 実際の画像パスをリストとして保持 (Listboxと1対1対応なのじゃ)
        self._image_paths: list[str] = []

    # ──────────────────────────────────────────
    # フォルダ選択・ツリー操作
    # ──────────────────────────────────────────

    def _choose_folder(self):
        """
        フォルダ選択ダイアログを開き、ルートフォルダをセットするのじゃ。
        """
        folder = filedialog.askdirectory(title="フォルダを選択")
        if not folder:
            return
        self.current_dir = Path(folder)
        self.path_label.config(text=str(self.current_dir), fg="#89b4fa")

        # ツリーをリセットしてルートを追加するのじゃ
        self.tree.delete(*self.tree.get_children())
        root_id = self.tree.insert(
            "", "end",
            text=self.current_dir.name,
            values=[str(self.current_dir)],
            open=True,
        )
        self._populate_tree(root_id, self.current_dir)
        self._load_images(self.current_dir)

    def _populate_tree(self, parent_id: str, folder: Path):
        """
        フォルダのサブディレクトリをツリーに追加するのじゃ。
        :param parent_id: 親ノードのID
        :param folder:    対象フォルダの Path
        """
        try:
            subdirs = sorted(
                [p for p in folder.iterdir() if p.is_dir()],
                key=lambda p: p.name.lower(),
            )
            for sub in subdirs:
                child_id = self.tree.insert(
                    parent_id, "end",
                    text=sub.name,
                    values=[str(sub)],
                )
                # ダミーノードを入れて展開矢印を表示するのじゃ
                if any(p.is_dir() for p in sub.iterdir() if p.is_dir()):
                    self.tree.insert(child_id, "end", text="__dummy__")
        except PermissionError:
            pass

    def _on_tree_open(self, event):
        """
        ツリーノードが展開されたとき、子フォルダを動的に読み込むのじゃ。
        """
        node_id = self.tree.focus()
        children = self.tree.get_children(node_id)
        # ダミーがあれば本物の子に入れ替えるのじゃ
        if children and self.tree.item(children[0])["text"] == "__dummy__":
            self.tree.delete(children[0])
            folder_path = Path(self.tree.item(node_id)["values"][0])
            self._populate_tree(node_id, folder_path)

    def _on_tree_select(self, event):
        """
        ツリーでフォルダを選択したとき、そのフォルダの画像を読み込むのじゃ。
        """
        sel = self.tree.selection()
        if not sel:
            return
        folder_path = Path(self.tree.item(sel[0])["values"][0])
        self._load_images(folder_path)

    def _load_images(self, folder: Path):
        """
        指定フォルダ内の画像ファイルを img_listbox に列挙するのじゃ。
        :param folder: 対象フォルダの Path
        """
        self.img_listbox.delete(0, tk.END)
        self._image_paths.clear()

        try:
            files = sorted(
                [p for p in folder.iterdir()
                 if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS],
                key=lambda p: p.name.lower(),
            )
        except PermissionError:
            files = []

        for f in files:
            self.img_listbox.insert(tk.END, f"  {f.name}")
            self._image_paths.append(str(f))

        if not files:
            self.img_listbox.insert(tk.END, "  （画像ファイルなし）")

    # ──────────────────────────────────────────
    # アルバムへの追加
    # ──────────────────────────────────────────

    def _on_image_double_click(self, event):
        """
        画像一覧でダブルクリックされたとき、現在のアルバムに画像を追加するのじゃ。
        """
        sel = self.img_listbox.curselection()
        if not sel:
            return

        idx = sel[0]
        if idx >= len(self._image_paths):
            return  # 「画像ファイルなし」行をクリックした場合は無視するのじゃ

        img_path = self._image_paths[idx]
        album_name = self.get_current_album()

        if not album_name:
            messagebox.showwarning(
                "アルバム未選択",
                "先にアルバムを選択してください！",
                parent=self,
            )
            return

        result = self.album_manager.add_image(album_name, img_path)
        if result:
            self.refresh_grid()
            # 追加成功のフィードバックとして行の背景を一瞬変えるのじゃ
            self.img_listbox.itemconfig(idx, bg="#a6e3a1", fg="#1e1e2e")
            self.after(600, lambda: self._reset_listbox_color(idx))
        else:
            # 重複追加の場合は薄い警告色にするのじゃ
            self.img_listbox.itemconfig(idx, bg="#f38ba8", fg="#1e1e2e")
            self.after(600, lambda: self._reset_listbox_color(idx))

    def _reset_listbox_color(self, idx: int):
        """
        画像一覧のアイテムカラーをデフォルトに戻すのじゃ。
        """
        try:
            self.img_listbox.itemconfig(idx, bg="#313244", fg="#cdd6f4")
        except tk.TclError:
            pass  # すでに削除されていたら無視するのじゃ
