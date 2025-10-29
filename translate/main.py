import argparse
import os
import sys
import time
from typing import List, Iterable, Optional

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
from tqdm import tqdm
import requests

SOURCE_LANG = 'ko'
TARGET_LANG = 'en'

def read_lines(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return f.read().splitlines()

def write_lines(path: str, lines):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        for line in lines:
            f.write(line + "\n")
    os.replace(tmp, path)

class MarianTranslator:
    def __init__(self, src_lang: str, tgt_lang: str, model_name: Optional[str], device: str):
        if not model_name:
            pair = f"{src_lang}-{tgt_lang}".lower()
            default_models = {
                "ko-en": "Helsinki-NLP/opus-mt-ko-en",
                "ja-en": "Helsinki-NLP/opus-mt-ja-en",
                "zh-en": "Helsinki-NLP/opus-mt-zh-en",
                "en-ko": "Helsinki-NLP/opus-mt-en-ko",
                "en-ja": "Helsinki-NLP/opus-mt-en-ja",
                "en-zh": "Helsinki-NLP/opus-mt-en-zh",
            }
            model_name = default_models.get(pair, f"Helsinki-NLP/opus-mt-{src_lang}-{tgt_lang}")
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        self.device = device
        self.model.to(self.device)
        self.model.eval()

    @torch.inference_mode()
    def translate_batch(self, texts: List[str], max_new_tokens: int = 128) -> List[str]:
        if len(texts) == 0:
            return []
        enc = self.tokenizer(texts, return_tensors="pt", padding=True, truncation=True)
        enc = {k: v.to(self.device) for k, v in enc.items()}
        gen = self.model.generate(
            **enc,
            max_new_tokens=max_new_tokens,
            num_beams=4,
            early_stopping=True
        )
        outs = self.tokenizer.batch_decode(gen, skip_special_tokens=True)
        return [o.strip() for o in outs]

class LibreTranslateTranslator:
    def __init__(self, src_lang: str, tgt_lang: str, api_url: str, api_key: Optional[str] = None):
        self.src = src_lang
        self.tgt = tgt_lang
        self.api_url = api_url.rstrip("/")
        self.api_key = api_key

    def translate_batch(self, texts, max_new_tokens: int = 128):
        out = []
        for t in texts:
            payload = {"q": t, "source": self.src, "target": self.tgt, "format": "text"}
            if self.api_key:
                payload["api_key"] = self.api_key
            for attempt in range(3):
                try:
                    r = requests.post(self.api_url + "/translate", json=payload, timeout=30)
                    r.raise_for_status()
                    out.append(r.json().get("translatedText", "").strip())
                    break
                except Exception:
                    time.sleep(1.5 * (attempt + 1))
            else:
                out.append("")
        return out

def chunker(seq, size: int):
    for i in range(0, len(seq), size):
        yield seq[i:i+size]

def main():
    p = argparse.ArgumentParser(description="Line-by-line TXT translator (source -> target).")
    p.add_argument("--input", "-i", required=True, help="Source .txt path (one sentence per line).")
    p.add_argument("--output", "-o", required=True, help="Target .txt path (translated, line-aligned).")
    p.add_argument("--src", default=SOURCE_LANG, help=f"Source lang code (default: {SOURCE_LANG}).")
    p.add_argument("--tgt", default="en", help="Target lang code (default: en).")
    p.add_argument("--provider", choices=["marian", "libre"], default="marian",
                   help="Translation backend. 'marian' = offline (free). 'libre' = LibreTranslate server.")
    p.add_argument("--model", default=None, help="HF model name (for provider=marian).")
    p.add_argument("--batch_size", type=int, default=16, help="Batch size (marian).")
    p.add_argument("--max_new_tokens", type=int, default=128, help="Max new tokens per line.")
    p.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto", help="Device for Marian.")
    p.add_argument("--libre_url", default="http://localhost:5000", help="LibreTranslate base URL.")
    p.add_argument("--libre_key", default=None, help="LibreTranslate API key (if your server requires).")
    p.add_argument("--keep_empty", action="store_true", help="Keep empty lines as empty (default '')")
    args = p.parse_args()

    if args.provider == "marian":
        if args.device == "cuda":
            device = "cuda" if torch.cuda.is_available() else "cpu"
        elif args.device == "auto":
            device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            device = "cpu"
        translator = MarianTranslator(args.src, args.tgt, args.model, device)
    else:
        translator = LibreTranslateTranslator(args.src, args.tgt, args.libre_url, args.libre_key)

    src_lines = read_lines(args.input)
    results = []

    if args.provider == "marian":
        for batch in tqdm(list(chunker(src_lines, args.batch_size)), desc="Translating", unit="batch"):
            to_translate = [ln if ln.strip() else "" for ln in batch]
            mask = [bool(ln.strip()) for ln in to_translate]
            payload = [ln for ln in to_translate if ln.strip()]
            outs = translator.translate_batch(payload, max_new_tokens=args.max_new_tokens) if payload else []
            it = iter(outs)
            for m in mask:
                results.append(next(it, "") if m else "")
    else:
        for ln in tqdm(src_lines, desc="Translating", unit="line"):
            if not ln.strip():
                results.append("")
                continue
            out = translator.translate_batch([ln], max_new_tokens=args.max_new_tokens)
            results.append(out[0] if out else "")

    write_lines(args.output, results)

    if len(results) != len(src_lines):
        print(f"[WARN] line-count mismatch: src={len(src_lines)} vs out={len(results)}", file=sys.stderr)
    else:
        print(f"[OK] Translated {len(results)} lines -> {args.output}")

if __name__ == "__main__":
    main()

