from fastapi import FastAPI, Request
import os, httpx

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "changeme123")  # برای امنیت مسیر
BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

app = FastAPI()

def tg_api(method, **params):
    return httpx.post(f"{BASE_URL}/{method}", json=params, timeout=10)

@app.get("/")
def health():
    return {"ok": True}

# مسیر وب‌هوک: /telegram/webhook/<secret>
@app.post(f"/telegram/webhook/{{secret}}")
async def webhook(secret: str, req: Request):
    if secret != WEBHOOK_SECRET:
        return {"ok": False}
    update = await req.json()
    msg = update.get("message") or update.get("edited_message")
    if not msg: 
        return {"ok": True}

    chat_id = msg["chat"]["id"]
    text = (msg.get("text") or "").strip()

    # پاسخ به /start
    if text.startswith("/start"):
        help_text = (
            "سلام! ربات easychart اینجاست.\n"
            "نماد + تایم‌فریم را بفرست: مثل «BTC 4H» یا «طلا روزانه».\n"
            "خروجی شامل خلاصه، روند، سطوح و دو سناریو است.\n"
            "⚠️ این توصیه سرمایه‌گذاری نیست."
        )
        tg_api("sendMessage", chat_id=chat_id, text=help_text)
        return {"ok": True}

    # فعلاً پاسخی ساده بدهیم؛ در فازهای بعد تحلیل را اضافه می‌کنیم
    tg_api("sendMessage", chat_id=chat_id, text="پیام دریافت شد. چند لحظه بعد تحلیل آماده می‌شود.")
    return {"ok": True}
