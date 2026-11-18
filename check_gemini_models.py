import os
from pathlib import Path

# load .env without extra packages
for line in Path(".env").read_text().splitlines():
    if "=" in line and not line.strip().startswith("#"):
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"'))

from google import genai

key = os.environ.get("GEMINI_API_KEY")
model = os.environ.get("GEMINI_MODEL")
print("Key loaded:", bool(key), "| length:", len(key or ""))
print("Model in .env:", model)

client = genai.Client(api_key=key)
print("Flash models your key can use:")
for m in client.models.list():
    if "flash" in m.name:
        print("  ", m.name)

try:
    r = client.models.generate_content(model=model, contents="Say hi in 3 words")
    print("SUCCESS:", r.text)
except Exception as e:
    print("FAILED:", type(e).__name__, e)