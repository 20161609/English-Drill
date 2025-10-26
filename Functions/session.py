import os, random, codecs
from collections import deque

class SentencePicker:
    def __init__(self, sentences):
        self.sentences = [s.strip() for s in sentences if s.strip()]
        if not self.sentences:
            raise ValueError("No sentences in the file.")
        self.Q = deque()
        self.N = len(self.sentences)

    def pick(self):
        if len(self.Q) >= self.N:
            self.Q.popleft()
        blocked = set(self.Q)
        candidates = [i for i in range(self.N) if i not in blocked]
        if not candidates:
            candidates = list(range(self.N))
        idx = random.choice(candidates)
        self.Q.append(idx)
        return idx, self.sentences[idx]

def load_categories(text_root: str, src_lang: str):
    lang_dir = os.path.join(text_root, src_lang)
    if not os.path.isdir(lang_dir):
        return []
    items = []
    for fn in os.listdir(lang_dir):
        if fn.lower().endswith(".txt"):
            name = os.path.splitext(fn)[0]
            path = os.path.join(lang_dir, fn)
            items.append((name, path))
    items.sort(key=lambda x: x[0].lower())
    return items

def read_sentences(path: str):
    with codecs.open(path, "r", "utf-8") as f:
        lines = f.read().splitlines()
    return lines

def list_languages(text_root: str):
    langs = []
    for name in os.listdir(text_root):
        p = os.path.join(text_root, name)
        if os.path.isdir(p):
            langs.append(name)
    langs.sort()
    return langs
