
class SettingsNotFound(Exception):
    def __init__(self, name: str):
        self.name = name
        super().__init__(f"Configuration directive not found: '{name}'")
