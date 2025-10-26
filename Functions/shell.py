import os, sys
from .session import list_languages

TITLE_NAME = 'CLI Translation Practice (GLOBAL → Target=en)'

ROOT = 'root'
CHOSEN = 'chosen'
TESTING = 'testing'

def _app_base():
    base = getattr(sys, '_MEIPASS', None)
    if base and os.path.isdir(base):
        return base
    return os.path.dirname(os.path.dirname(__file__))

class Shell:
    def __init__(self):
        print(f"\"Welcome to {TITLE_NAME}\"")
        self.prompt = '>>> '
        self.base_dir = _app_base()
        self.text_root = os.path.join(self.base_dir, "text")
        self.state = ROOT
        self.current_cat = None
        self.picker = None
        self.round_total = 0
        self.round_idx = 0
        self.current_pair = None
        print("Type 'help' for commands.")

    def fetch(self, command: str):
        if command == 'langs':
            self._cmd_langs()
            return

    def _cmd_langs(self):
        langs = list_languages(self.text_root)
        if not langs:
            print("No languages found under text/. Create text/<src>/ first.")
            return
        print("Available source languages:")
        print(", ".join(langs))
