import os

def list_languages(text_root: str):
    langs = []
    for name in os.listdir(text_root):
        p = os.path.join(text_root, name)
        if os.path.isdir(p):
            langs.append(name)
    langs.sort()
    return langs
