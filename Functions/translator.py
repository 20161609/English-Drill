# translate_strict_v4.py
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch, re

_MODEL_NAME = "Helsinki-NLP/opus-mt-ko-en"
_tokenizer = AutoTokenizer.from_pretrained(_MODEL_NAME)
_model = AutoModelForSeq2SeqLM.from_pretrained(_MODEL_NAME)
_device = "cuda" if torch.cuda.is_available() else "cpu"
_model.to(_device)
_model.eval()

@torch.inference_mode()
def translate(src: str) -> str:
    if not src.strip():
        return ""
    inputs = _tokenizer(src, return_tensors="pt", truncation=True).to(_device)
    outputs = _model.generate(**inputs, num_beams=4, early_stopping=True, max_new_tokens=128)
    return _tokenizer.decode(outputs[0], skip_special_tokens=True).strip()

# For proofreading (grammar consistency + maintaining expression for learning)
def _normalize_english(text: str) -> str:
    rules = {
        r"\bThe server does not respond\b": "The server is not responding",
        r"\bUploading of files failed\b": "The file upload has failed",
        r"\bIt's too slow\b": "It is too slow",
        r"\bI'm\b": "I am",
        r"\bHe's\b": "He is",
        r"\bShe's\b": "She is",
        r"\bCan't\b": "cannot",
        r"\bdoesn't\b": "does not",
    }
    for pat, rep in rules.items():
        text = re.sub(pat, rep, text)
    return text.strip()

def translate_strict(src: str) -> str:
    raw = translate(src)    
    return _normalize_english(raw)

def test_translate(tests, translate):
    for t in tests:
        print(f"{t} -> {translate(t)}\n")
