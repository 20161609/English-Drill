import os, json, sys
DEFAULT = {"src_lang": "ko", "tgt_lang": "en"}  # target fixed to en

def _storage_dir():
    # If frozen (PyInstaller), store next to the executable
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    # Dev mode: project root (two levels up from this file)
    return os.path.dirname(os.path.dirname(__file__))

def _cfg_path():
    return os.path.join(_storage_dir(), ".appconfig.json")

def load_config():
    path = _cfg_path()
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                data["tgt_lang"] = "en"
                return {**DEFAULT, **data}
        except Exception:
            return DEFAULT.copy()
    return DEFAULT.copy()

def save_config(cfg):
    cfg = dict(cfg)
    cfg["tgt_lang"] = "en"
    path = _cfg_path()
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False
