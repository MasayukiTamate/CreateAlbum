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
    # 設定管理オブジェクトを生成するのじゃ
    from config_manager import ConfigManager
    config = ConfigManager()

    # アルバムデータを管理するオブジェクトを生成するのじゃ
    album_manager = AlbumManager()

    # メインウィンドウを生成して起動するのじゃ
    app = MainWindow(album_manager, config)
    
    # ログ管理オブジェクトを生成し、ウィンドウを初期化するのじゃ
    # ※MainWindowが生成された後にToplevelを作成するのが安全なのじゃ
    from log_manager import LogManager
    log_manager = LogManager(app, config)
    app.log_manager = log_manager # app配下でも参照できるようにするのじゃ
    
    log_manager.log("アプリを起動したのじゃ！")

    app.mainloop()


if __name__ == "__main__":
    main()
