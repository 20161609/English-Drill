import os, sys, torch, gdown, zipfile

from transformers import AutoTokenizer, AutoModelForSequenceClassification

DRIVE_ID = "1pTn2HbF2ZSTG43DDl17FfnTxY9KXYMwi"
DRIVE_URL = f"https://drive.google.com/uc?id={DRIVE_ID}"

def _base_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(BASE_DIR, "model_20251102")
ZIP_PATH = os.path.join(BASE_DIR, "model_20251102.zip")

# Download model & restore
def ensure_model():
    # Get file
    if os.path.exists(os.path.join(MODEL_DIR, "model.safetensors")):
        print(f"[INFO] Found existing model at {MODEL_DIR}")
        return
    os.makedirs(_base_dir(), exist_ok=True)
    print("[INFO] Model not found. Downloading from Google Drive...")

    # Download
    gdown.download(DRIVE_URL, ZIP_PATH, quiet=False)

    # Validation
    if not os.path.exists(ZIP_PATH) or os.path.getsize(ZIP_PATH) < 10_000:
        raise RuntimeError(f"[ERROR] Downloaded file too small or missing: {ZIP_PATH}")

    # Release
    if not zipfile.is_zipfile(ZIP_PATH):
        raise RuntimeError(f"[ERROR] The downloaded file is not a valid zip archive: {ZIP_PATH}")
    print("[INFO] Unzipping model...")
    with zipfile.ZipFile(ZIP_PATH, "r") as zip_ref:
        zip_ref.extractall(MODEL_DIR)

    os.remove(ZIP_PATH)
    print(f"[OK] Model ready at {MODEL_DIR}")

# Get model
ensure_model()

print("[INFO] Loading model...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_DIR)
model.eval()

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

def score_pair(src: str, mt: str) -> float:
    if not src.strip() or not mt.strip():
        return 0.0
    text = f"ko: {src.strip()} en: {mt.strip()}"
    enc = tokenizer(text, return_tensors="pt", truncation=True, max_length=256).to(device)
    out = model(**enc)
    pred = out.logits.squeeze().item()
    return max(0.0, min(1.0, pred)) * 100.0