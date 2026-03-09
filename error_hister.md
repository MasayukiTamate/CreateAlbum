# エラー履歴（詳細解析付き）なのじゃ

## 2026-03-09 AttributeError の発生
**エラー内容**:
`AttributeError: '_tkinter.tkapp' object has no attribute 'image_grid'`

**詳細な原因分析**:
`c:\App_Code_Python\CreateAlbum\ui\main_window.py` の `_build_ui` メソッド内で、左ペインの `AlbumTabPanel` をインスタンス化する際、内部で `self.refresh()` が呼ばれ、最初のアルバムを選択状態にするためのコールバック `on_select_callback` (`self._on_album_select`) が即座に発火してしまうのじゃ。

このとき、`_on_album_select` 内で `self.image_grid.show_album(album_name)` が呼ばれるのじゃが、中央ペインの `ImageGridPanel` (すなわち `self.image_grid`) はこの時点ではまだインスタンス化（初期化）されていないため、オブジェクトにアクセスできず `AttributeError` が発生したのじゃ。

**解決策**:
コールバックである `_on_album_select` 内で、`self.image_grid` が存在するかどうかを `hasattr(self, 'image_grid')` でチェックするように修正することで、起動時のUI構築順序に依存しない安全な実装にするのじゃ。起動時の初期表示はすでに `MainWindow.__init__` で安全に行われているため、これで問題なく動作するはずなのじゃ。
