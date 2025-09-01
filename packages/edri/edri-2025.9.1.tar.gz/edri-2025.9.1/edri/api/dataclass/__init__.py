from .file import File
from .client import Client

class Cookie:
    def __init__(self, name: str):
        self.name = name


class Header:
    def __init__(self, name: str):
        self.name = name.lower()


class Scope:
    def __init__(self, name: str):
        self.name = name.lower()
