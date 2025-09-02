from __future__ import annotations

from amabase.utils import Color

class SettingsCommand:
    help = "Display amabase settings."

    def handle(self):
        from amabase.conf import settings

        key_len = 10
        for key in settings.values.keys():
            if len(key) > key_len:
                key_len = len(key)

        for key in sorted(settings.values.keys()):
            value = settings.values[key]
            if not isinstance(value, str):
                value = str(value)
            print(f"{Color.CYAN}{key}{Color.RESET}: {' ' * (key_len - len(key))}{value}")
