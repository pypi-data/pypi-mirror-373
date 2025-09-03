class EnvError(Exception):
    def __init__(self, key: str):
        super().__init__(f"Failed to load env variable {key}")
        self.key = key
