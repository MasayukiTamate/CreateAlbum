# 修正履歴 (hister.md) なのじゃ

- 2026-03-09: `ui/main_window.py` の `_on_album_select` メソッドを修正し、`self.image_grid` インスタンスが存在するか確認してから `show_album` メソッドを呼び出すよう安全な実装に変更。これにより起動時の `AttributeError` を解消したのじゃ。

## 2026-03-09 追加要望 (v2) の実装
- `ui/explorer_panel.py` に左矢印ボタン（⬅追加）を新設し、アルバムへの追加機能を提供したのじゃ。
- `ui/explorer_panel.py` のリスト領域下部に、選択画像のプレビュー表示機能を追加したのじゃ。
- `ui/explorer_panel.py` および `ui/image_grid_panel.py` の画像一覧から右クリックで、実画像のファイル名変更（リネーム）ができる機能を追加したのじゃ。
- `album_manager.py` に `rename_image_path` メソッドを追加し、実ファイルのリネームに伴いアルバム情報内のパスも自動更新されるようにしたのじゃ。

## 2026-03-09 アルバム未選択エラーの修正
- `ui/album_tab_panel.py` を修正したのじゃ。エクスプローラペインやボタンなどをクリックすると Tkinter の `Listbox.curselection()` が外れてしまう仕様のため、内部変数 `self._current_album` に最後に選択されたアルバム名を保持し、`get_selected()` で確実に返せるようにしたのじゃ。
