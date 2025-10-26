import os, random, codecs
from collections import deque

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
