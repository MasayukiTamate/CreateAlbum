"""
album_manager.py
アルバムデータの管理を担当するモジュールなのじゃ。
アルバムの追加・削除・リネーム、画像の追加・削除、
および albums.json によるデータ永続化を行うのじゃ。
"""

import json
import os
from pathlib import Path


class AlbumManager:
    """
    アルバムデータを管理するクラスなのじゃ。
    データは albums.json に保存・読み込みされるのじゃ。
    """

    # アルバムデータを保存するJSONファイルのパス
    DATA_FILE = Path(__file__).parent / "albums.json"

    def __init__(self):
        """
        初期化: JSONファイルからアルバムデータを読み込むのじゃ。
        ファイルが存在しない場合は空の辞書で始めるのじゃ。
        データ構造: { アルバム名(str): [画像パス(str), ...] }
        """
        # アルバムデータを格納する辞書 { アルバム名: [画像パスリスト] }
        self.albums: dict[str, list[str]] = {}
        self._load()

    # ──────────────────────────────────────────
    # ファイルI/O
    # ──────────────────────────────────────────

    def _load(self):
        """
        albums.json からアルバムデータを読み込むのじゃ。
        ファイルが存在しない・壊れている場合は空データで継続するのじゃ。
        """
        if self.DATA_FILE.exists():
            try:
                with open(self.DATA_FILE, "r", encoding="utf-8") as f:
                    self.albums = json.load(f)
            except (json.JSONDecodeError, IOError):
                # 読み込みに失敗したら空データで始めるのじゃ
                self.albums = {}

    def save(self):
        """
        アルバムデータを albums.json に保存するのじゃ。
        変更のたびに呼ぶことで確実にデータを永続化するのじゃ。
        """
        with open(self.DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.albums, f, ensure_ascii=False, indent=2)

    # ──────────────────────────────────────────
    # アルバム操作
    # ──────────────────────────────────────────

    def get_album_names(self) -> list[str]:
        """
        アルバム名の一覧を返すのじゃ。
        辞書のキー順で返すのじゃ。
        """
        return list(self.albums.keys())

    def add_album(self, name: str) -> bool:
        """
        新しいアルバムを追加するのじゃ。
        同名のアルバムが既に存在する場合は False を返すのじゃ。

        :param name: 追加するアルバム名
        :return: 成功すれば True、既に存在する場合は False
        """
        name = name.strip()
        if not name or name in self.albums:
            return False
        self.albums[name] = []
        self.save()
        return True

    def delete_album(self, name: str) -> bool:
        """
        指定した名前のアルバムを削除するのじゃ。
        存在しないアルバムを指定した場合は False を返すのじゃ。

        :param name: 削除するアルバム名
        :return: 成功すれば True
        """
        if name not in self.albums:
            return False
        del self.albums[name]
        self.save()
        return True

    def rename_album(self, old_name: str, new_name: str) -> bool:
        """
        アルバム名を変更するのじゃ。
        新名が空・既存名と同じ・既存の別名と重複する場合は False を返すのじゃ。

        :param old_name: 変更前のアルバム名
        :param new_name: 変更後のアルバム名
        :return: 成功すれば True
        """
        new_name = new_name.strip()
        if not new_name or new_name == old_name:
            return False
        if old_name not in self.albums or new_name in self.albums:
            return False
        # 順序を保ちながらキー名を変更するのじゃ
        self.albums = {
            (new_name if k == old_name else k): v
            for k, v in self.albums.items()
        }
        self.save()
        return True

    # ──────────────────────────────────────────
    # 画像操作
    # ──────────────────────────────────────────

    def get_images(self, album_name: str) -> list[str]:
        """
        指定アルバムの画像パスリストを返すのじゃ。
        アルバムが存在しない場合は空リストを返すのじゃ。

        :param album_name: 対象のアルバム名
        :return: 画像パスのリスト
        """
        return list(self.albums.get(album_name, []))

    def add_image(self, album_name: str, image_path: str) -> bool:
        """
        指定アルバムに画像を追加するのじゃ。
        既に同じパスが登録済みの場合は重複追加しないのじゃ。

        :param album_name: 追加先のアルバム名
        :param image_path: 追加する画像の絶対パス
        :return: 成功すれば True
        """
        if album_name not in self.albums:
            return False
        # 重複チェックをするのじゃ
        if image_path in self.albums[album_name]:
            return False
        self.albums[album_name].append(image_path)
        self.save()
        return True

    def remove_image(self, album_name: str, image_path: str) -> bool:
        """
        指定アルバムから画像を削除するのじゃ。

        :param album_name: 対象のアルバム名
        :param image_path: 削除する画像の絶対パス
        :return: 成功すれば True
        """
        if album_name not in self.albums:
            return False
        try:
            self.albums[album_name].remove(image_path)
            self.save()
            return True
        except ValueError:
            return False
