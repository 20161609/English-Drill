import os, sys
from .session import list_languages, load_categories, read_sentences, SentencePicker
from .config import load_config, save_config

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
        self.cfg = load_config()
        self.text_root = os.path.join(self.base_dir, "text")
        self.categories = load_categories(self.text_root, self.cfg['src_lang'])
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

        if self.state == ROOT:
            if command == 'ls':
                self._cmd_ls()
            elif command.startswith("lang"):
                self._cmd_lang(command)
            elif command == 'config':
                self._print_config()
            elif command.isdigit():
                self._cmd_choose_by_number(int(command))
        elif self.state == CHOSEN:
            if command == 'ls':
                self._cmd_ls()
            elif command == 'back':
                self._to_root()
            


    def _cmd_langs(self):
        langs = list_languages(self.text_root)
        if not langs:
            print("No languages found under text/. Create text/<src>/ first.")
            return
        print("Available source languages:")
        print(", ".join(langs))

    def _cmd_ls(self, initial=False):
        if not self.categories:
            print(f"No *.txt files under text/{self.cfg['src_lang']}/. Add your source-language sentences there.")
            return
        print("ls")
        for i, (name, _) in enumerate(self.categories, 1):
            print(f"{i}. {name}")
        self.state = ROOT
        self.prompt = '>>> '

    def _print_config(self):
        print("Current config:", self.cfg)

    def _cmd_lang(self, cmd: str):
        parts = cmd.split()
        if len(parts) == 1:
            print(f"Languages: source={self.cfg['src_lang']} target={self.cfg['tgt_lang']} (target fixed to 'en')")
            return
        if len(parts) >= 2:
            src = parts[1].lower()
            if not os.path.isdir(os.path.join(self.text_root, src)):
                print(f"'{src}' not found under text/. Use 'langs' to see options.")
                return
            self.cfg['src_lang'] = src
            self.cfg['tgt_lang'] = 'en'
            save_config(self.cfg)
            print(f"Set language: source={src}, target=en (fixed)")
            self.categories = load_categories(self.text_root, self.cfg['src_lang'])
            if not self.categories:
                print(f"No categories under text/{self.cfg['src_lang']}/ yet.")
            self.state = ROOT
            self.current_cat = None
            self.picker = None
            self.round_total = 0
            self.round_idx = 0
            self.current_pair = None
            self._cmd_ls()
        else:
            print("Usage: lang <src>   (see 'langs')")

    def _cmd_choose_by_number(self, num: int):
        if num < 1 or num > len(self.categories):
            print("Index out of range.")
            return
        name, path = self.categories[num-1]
        sents = read_sentences(path)
        try:
            self.picker = SentencePicker(sents)
        except Exception as e:
            print("Category load error:", e)
            return
        self.current_cat = name
        self.state = CHOSEN
        self.prompt = f"[{name}] >>> "
        print(f"[{name}] >>> Enter number of questions. Example: 10")

    def _to_root(self):
        self.state = ROOT
        self.current_cat = None
        self.picker = None
        self.round_total = 0
        self.round_idx = 0
        self.current_pair = None
        self.prompt = '>>> '
        self._cmd_ls()
