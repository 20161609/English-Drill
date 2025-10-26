import os, re, json, math, sys
from typing import List
from .translator import translate as mt_translate

def _envf(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, default))
    except Exception:
        return default

SCORE_SCALE   = _envf("SCORE_SCALE", 1.0)
SCORE_OFFSET  = _envf("SCORE_OFFSET", 0.4)
PENALTY_FACTOR= _envf("PENALTY_FACTOR", 0.6)

def _app_base():
    base = getattr(sys, '_MEIPASS', None)
    if base and os.path.isdir(base):
        return base
    return os.path.dirname(os.path.dirname(__file__))

ROOT_DIR = _app_base()
REF_DIR  = os.path.join(ROOT_DIR, "refs")

def _unicode_words(s: str) -> List[str]:
    return [t.casefold() for t in re.findall(r"[^\W\d_]+", s, flags=re.UNICODE)]

def _overlap_score_lenient(user: str, ref: str) -> float:
    u = set(_unicode_words(user))
    r = set(_unicode_words(ref))
    if not u or not r:
        return 0.0
    ratio = len(u & r) / max(len(r), 1)
    base = 5.0 * math.sqrt(ratio)
    base = base * SCORE_SCALE + (SCORE_OFFSET * 1.0)
    return max(0.0, min(5.0, round(base, 2)))

def _dedup5(items):
    seen, out = set(), []
    for t in items:
        t = (t or "").strip()
        if not t:
            continue
        if t not in seen:
            seen.add(t)
            out.append(t)
        if len(out) == 5:
            break
    while len(out) < 5 and out:
        out.append(out[-1])
    return out[:5] if out else ["", "", "", "", ""]

def _load_refpack(src_lang: str):
    path = os.path.join(REF_DIR, f"{src_lang.lower()}.json")
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
    except Exception:
        pass
    return []

def _best_ref_for_text(text: str, refpack):
    best, best_score = None, -1
    for item in refpack:
        triggers = item.get("triggers", [])
        score = sum(1 for t in triggers if t and t in text)
        if score > best_score:
            best, best_score = item, score
    return best

def evaluate(src_text: str, user_tgt: str, src_lang: str, tgt_lang: str):
    user = user_tgt.strip()
    pack = _load_refpack(src_lang)
    ref_item = _best_ref_for_text(src_text, pack) if pack else None
    ref_en = ref_item["ref"] if ref_item and ref_item.get("ref") else ""
    alts_en = ref_item.get("alts", []) if ref_item else []
    if os.getenv("MT_PROVIDER"):
        ref_tgt = mt_translate(src_text, src_lang, "en") or ref_en
        score = _overlap_score_lenient(user, ref_tgt or src_text)
        return {"score": score, "alternatives": _dedup5([ref_tgt] + alts_en)}
    if ref_en:
        score = _overlap_score_lenient(user, ref_en)
        return {"score": score, "alternatives": _dedup5([ref_en] + alts_en)}
    words = _unicode_words(user)
    rough = min(5.0, max(0.0, (len(words) / 8.0) * 5.0))
    rough = rough * SCORE_SCALE + SCORE_OFFSET
    rough = max(0.0, min(5.0, round(rough, 2)))
    return {"score": rough, "alternatives": _dedup5([user, user.capitalize(), re.sub(r"\.$", "", user)])}
