"""
ui/album_tab_panel.py
左ペイン: アルバムのタブ（リスト）を表示・管理するパネルなのじゃ。
アルバムの選択・追加・削除・名前変更機能を持つのじゃ。
"""

import tkinter as tk
from tkinter import simpledialog, messagebox


class AlbumTabPanel(tk.Frame):
    """
    左ペインに配置するアルバムタブパネルなのじゃ。
    tkinter の Listbox でアルバム名を一覧表示し、
    選択したアルバムをコールバックで通知するのじゃ。
    """

    def __init__(self, parent, album_manager, on_select_callback, **kwargs):
        """
        :param parent:             親ウィジェット
        :param album_manager:      AlbumManager のインスタンス
        :param on_select_callback: アルバム選択時に呼ばれるコールバック(album_name: str)
        """
        super().__init__(parent, **kwargs)
        self.configure(bg="#1e1e2e")

        # データ管理オブジェクト
        self.album_manager = album_manager
        # アルバム選択時に呼ぶコールバック
        self.on_select_callback = on_select_callback

        self._build_ui()
        self.refresh()

    def _build_ui(self):
        """UIウィジェットを組み立てるのじゃ。"""

        # ── ヘッダーラベル ──
        header = tk.Label(
            self,
            text="📁 アルバム",
            bg="#1e1e2e",
            fg="#cdd6f4",
            font=("Yu Gothic UI", 13, "bold"),
            anchor="w",
            padx=12,
            pady=10,
        )
        header.pack(fill="x")

        # ── アルバムリスト ──
        list_frame = tk.Frame(self, bg="#1e1e2e")
        list_frame.pack(fill="both", expand=True, padx=6, pady=(0, 6))

        # スクロールバー
        scrollbar = tk.Scrollbar(list_frame, orient="vertical", bg="#313244")
        scrollbar.pack(side="right", fill="y")

        # アルバム名を並べる Listbox
        self.listbox = tk.Listbox(
            list_frame,
            yscrollcommand=scrollbar.set,
            bg="#313244",
            fg="#cdd6f4",
            selectbackground="#89b4fa",
            selectforeground="#1e1e2e",
            font=("Yu Gothic UI", 11),
            borderwidth=0,
            highlightthickness=0,
            activestyle="none",
            cursor="hand2",
        )
        self.listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.listbox.yview)

        # リスト選択イベントのバインド
        self.listbox.bind("<<ListboxSelect>>", self._on_select)
        # ダブルクリックでリネーム
        self.listbox.bind("<Double-Button-1>", self._on_rename)

        # ── ボタン行 ──
        btn_frame = tk.Frame(self, bg="#1e1e2e")
        btn_frame.pack(fill="x", padx=6, pady=(0, 8))

        # 追加ボタン
        self.add_btn = tk.Button(
            btn_frame,
            text="＋ 追加",
            command=self._on_add,
            bg="#89b4fa",
            fg="#1e1e2e",
            font=("Yu Gothic UI", 10, "bold"),
            relief="flat",
            cursor="hand2",
            padx=8,
            pady=4,
        )
        self.add_btn.pack(side="left", expand=True, fill="x", padx=(0, 4))

        # 削除ボタン
        self.del_btn = tk.Button(
            btn_frame,
            text="✕ 削除",
            command=self._on_delete,
            bg="#f38ba8",
            fg="#1e1e2e",
            font=("Yu Gothic UI", 10, "bold"),
            relief="flat",
            cursor="hand2",
            padx=8,
            pady=4,
        )
        self.del_btn.pack(side="left", expand=True, fill="x")

    # ──────────────────────────────────────────
    # 公開メソッド
    # ──────────────────────────────────────────

    def refresh(self, select_name: str = None):
        """
        Listbox の内容をアルバムマネージャに同期するのじゃ。
        :param select_name: 更新後に選択状態にするアルバム名 (省略可)
        """
        self.listbox.delete(0, tk.END)
        names = self.album_manager.get_album_names()
        for name in names:
            self.listbox.insert(tk.END, name)

        # 選択位置を復元するのじゃ
        if select_name and select_name in names:
            idx = names.index(select_name)
            self.listbox.selection_set(idx)
            self.listbox.activate(idx)
        elif names:
            # デフォルトは先頭を選択するのじゃ
            self.listbox.selection_set(0)
            self.listbox.activate(0)
            self.on_select_callback(names[0])

    def get_selected(self) -> str | None:
        """
        現在選択中のアルバム名を返すのじゃ。
        何も選択されていない場合は None を返すのじゃ。
        """
        sel = self.listbox.curselection()
        if not sel:
            return None
        return self.listbox.get(sel[0])

    # ──────────────────────────────────────────
    # イベントハンドラ
    # ──────────────────────────────────────────

    def _on_select(self, event):
        """Listbox でアルバムを選択したときのハンドラなのじゃ。"""
        name = self.get_selected()
        if name:
            self.on_select_callback(name)

    def _on_add(self):
        """追加ボタン押下: 新しいアルバム名を入力ダイアログで受け取るのじゃ。"""
        name = simpledialog.askstring(
            "新しいアルバム",
            "アルバム名を入力してください：",
            parent=self,
        )
        if name:
            if self.album_manager.add_album(name):
                self.refresh(select_name=name)
                self.on_select_callback(name)
            else:
                messagebox.showwarning(
                    "重複エラー",
                    f"「{name}」はすでに存在するのじゃ！",
                    parent=self,
                )

    def _on_delete(self):
        """削除ボタン押下: 選択中のアルバムを削除するのじゃ。"""
        name = self.get_selected()
        if not name:
            return
        ok = messagebox.askyesno(
            "確認",
            f"「{name}」を削除しますか？\n（画像ファイル自体は消えないのじゃ）",
            parent=self,
        )
        if ok:
            self.album_manager.delete_album(name)
            self.refresh()

    def _on_rename(self, event):
        """ダブルクリック: 選択中のアルバム名を変更するのじゃ。"""
        old_name = self.get_selected()
        if not old_name:
            return
        new_name = simpledialog.askstring(
            "アルバム名変更",
            f"「{old_name}」の新しい名前：",
            initialvalue=old_name,
            parent=self,
        )
        if new_name and new_name != old_name:
            if self.album_manager.rename_album(old_name, new_name):
                self.refresh(select_name=new_name)
                self.on_select_callback(new_name)
            else:
                messagebox.showwarning(
                    "エラー",
                    f"「{new_name}」への変更に失敗したのじゃ！",
                    parent=self,
                )
