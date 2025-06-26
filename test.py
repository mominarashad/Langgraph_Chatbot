import requests
import os
from dotenv import load_dotenv

load_dotenv()

secret_key = os.getenv("LANGFUSE_SECRET_KEY")
host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")

url = f"{host}/api/public/observations"

print("🔑 Secret key prefix:", secret_key[:6], "...")

res = requests.get(
    url,
    auth=(secret_key, ""),  # ✅ Basic Auth
    headers={"Content-Type": "application/json"}
)

print("📡 Request URL:", url)
print("📦 Status Code:", res.status_code)
try:
    print("📄 JSON Response:", res.json())
except Exception:
    print("🧨 Raw Response:", res.text)
