import os
def _get_requests():
    try:
        import requests
        return requests
    except Exception:
        return None

def _clean(s: str) -> str:
    return (s or "").strip()

def translate(text: str, source_lang: str, target_lang: str) -> str:
    provider = (os.getenv("MT_PROVIDER") or "").lower().strip()
    if not provider:
        return ""
    if provider == "azure":
        return _azure(text, source_lang, target_lang)
    if provider == "deepl":
        return _deepl(text, source_lang, target_lang)
    if provider == "libre":
        return _libre(text, source_lang, target_lang)
    return ""

def _azure(text: str, src: str, tgt: str) -> str:
    requests = _get_requests()
    if not requests:
        return ""
    endpoint = os.getenv("AZURE_TRANSLATOR_ENDPOINT", "https://api.cognitive.microsofttranslator.com").rstrip("/")
    key = os.getenv("AZURE_TRANSLATOR_KEY", "")
    region = os.getenv("AZURE_TRANSLATOR_REGION", "")
    if not key or not region:
        return ""
    url = f"{endpoint}/translate"
    params = {"api-version": "3.0", "from": src, "to": tgt}
    headers = {
        "Ocp-Apim-Subscription-Key": key,
        "Ocp-Apim-Subscription-Region": region,
        "Content-Type": "application/json",
    }
    try:
        resp = requests.post(url, params=params, headers=headers, json=[{"text": text}], timeout=20)
        resp.raise_for_status()
        data = resp.json()
        return _clean(data[0]["translations"][0]["text"])
    except Exception:
        return ""

def _deepl(text: str, src: str, tgt: str) -> str:
    requests = _get_requests()
    if not requests:
        return ""
    url = os.getenv("DEEPL_API_URL", "https://api-free.deepl.com/v2/translate")
    key = os.getenv("DEEPL_API_KEY", "")
    if not key:
        return ""
    def map_code(code: str) -> str:
        m = {"en":"EN-US","vi":"VI","ko":"KO","ja":"JA","zh":"ZH","fr":"FR","de":"DE","es":"ES",
             "pt":"PT-PT","it":"IT","nl":"NL","pl":"PL","sv":"SV"}
        return m.get(code.lower(), code.upper())
    data = {"auth_key": key, "text": text, "source_lang": map_code(src), "target_lang": map_code(tgt)}
    try:
        resp = requests.post(url, data=data, timeout=20)
        resp.raise_for_status()
        js = resp.json()
        tr = js.get("translations", [{}])[0].get("text", "")
        return _clean(tr)
    except Exception:
        return ""

def _libre(text: str, src: str, tgt: str) -> str:
    requests = _get_requests()
    if not requests:
        return ""
    url = os.getenv("LIBRE_URL", "http://localhost:5000/translate")
    payload = {"q": text, "source": src, "target": tgt, "format": "text"}
    headers = {"Content-Type": "application/json"}
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=20)
        resp.raise_for_status()
        js = resp.json()
        return _clean(js.get("translatedText", ""))
    except Exception:
        return ""
