"""
app.py
アプリケーションのエントリーポイントなのじゃ。
AlbumManager を初期化して MainWindow を起動するのじゃ。
起動方法: python app.py
"""

from album_manager import AlbumManager
from ui.main_window import MainWindow


def main():
    """
    アプリを起動するメイン関数なのじゃ。
    AlbumManager でデータを読み込み、MainWindow を表示するのじゃ。
    """
    # アルバムデータを管理するオブジェクトを生成するのじゃ
    album_manager = AlbumManager()

    # メインウィンドウを生成して起動するのじゃ
    app = MainWindow(album_manager)
    app.mainloop()


if __name__ == "__main__":
    main()
