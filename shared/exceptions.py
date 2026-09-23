class NotFound(Exception):
    def __init__(self, name: str):
        self.name = name
        super().__init__(name)
