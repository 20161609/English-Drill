# === Translation Quality Scoring Test (with your trained model) ===
import torch
import pandas as pd
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import os, sys
from transformers import AutoTokenizer, AutoModelForSequenceClassification

def _base_dir():
    """
    - Under development: parent folder (v14) based on this file
    - Post-deployment (PyInstaller): executable (.exe) baseline folder
    """
    if getattr(sys, 'frozen', False):  # If it's a PyInstaller running environment
        return os.path.dirname(sys.executable)
    else:  # Dev env (python main.py)
        return os.path.dirname(os.path.dirname(__file__))

MODEL_DIR = os.path.join(_base_dir(), "model")
tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_DIR)
model.eval()

# Score calculation function
def score_pair(src, mt):
    inputs = tokenizer(
        f"[KO] {src} [EN] {mt}",
        truncation=True,
        padding=True,
        max_length=128,
        return_tensors="pt"
    )
    with torch.no_grad():
        pred = model(**inputs).logits.squeeze().item()
        return float(pred) * 100
