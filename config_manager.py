"""
config_manager.py
アプリの全設定を管理するモジュールなのじゃ。
設定は config.json に保存され、起動時に読み込まれるのじゃ。
"""

import json
from pathlib import Path

class ConfigManager:
    """
    設定データを管理するクラスなのじゃ。
    """
    CONFIG_FILE = Path(__file__).parent / "config.json"

    def __init__(self):
        # デフォルト設定値なのじゃ
        self.settings = {
            "show_log_window": True,
            "window_geometry": "1280x800",
            "bg_color": "#181825",
            # 新たな変数はここに追加するのじゃ
        }
        self.load()

    def load(self):
        """設定データを読み込むのじゃ。"""
        if self.CONFIG_FILE.exists():
            try:
                with open(self.CONFIG_FILE, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    self.settings.update(loaded)
            except Exception as e:
                print(f"設定の読み込みに失敗したのじゃ: {e}")

    def save(self):
        """設定データを保存するのじゃ。"""
        try:
            with open(self.CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"設定の保存に失敗したのじゃ: {e}")

    def get(self, key, default=None):
        """設定値を取得するのじゃ。"""
        return self.settings.get(key, default)

    def set(self, key, value):
        """設定値を更新し、保存するのじゃ。"""
        self.settings[key] = value
        self.save()
