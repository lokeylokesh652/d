import imaplib
import email
import re
import time
import requests
import threading
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ====== CONFIGURATION ======
GMAIL_USER = 'indoigg0111@gmail.com'
GMAIL_PASSWORD = 'esaneurrvpmcxdnk'  # App Password
TELEGRAM_BOT_TOKEN = '7485486399:AAFSA0M5O5jePlIQw-hLsia_8Nv6XmjhEUw'
TELEGRAM_CHAT_ID = '7437878492'

# ─── Email Check + Send OTP ─────────────────────────────────────────────
def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text
    }
    requests.post(url, data=payload)

def check_email():
    while True:
        try:
            mail = imaplib.IMAP4_SSL("imap.gmail.com")
            mail.login(GMAIL_USER, GMAIL_PASSWORD)
            print("✅ Logged into Gmail successfully.")
            mail.select("inbox")

            result, data = mail.search(None, '(UNSEEN FROM "no-reply@mail.instagram.com")')
            email_ids = data[0].split()

            for e_id in email_ids:
                result, msg_data = mail.fetch(e_id, "(RFC822)")
                mail.store(e_id, '+FLAGS', '\\Seen')

                raw_email = msg_data[0][1]
                msg = email.message_from_bytes(raw_email)

                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            body = part.get_payload(decode=True).decode()
                else:
                    body = msg.get_payload(decode=True).decode()

                otp_match = re.search(r'\b\d{6}\b', body)
                if otp_match:
                    otp = otp_match.group()
                    message = f"📨 New Instagram OTP: {otp}"
                    print(message)
                    send_telegram_message(message)
                else:
                    print("OTP not found.")
            mail.logout()

        except Exception as e:
            print(f"Error: {e}")
        time.sleep(10)

# ─── Telegram Bot /start Handler ─────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "👋 *OTP Bot Activated!*\n\n"
        "This bot monitors Gmail for Instagram OTPs and sends them here 📬\n\n"
        "*Status:* ✅ Running 24/7\n"
        "*Features:*\n"
        "🔹 Auto-detect 6-digit OTPs\n"
        "🔹 Instant Telegram alerts"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

# ─── Run Both Together ──────────────────────────────────────────────────
if __name__ == "__main__":
    print("🚀 OTP Bot started...")

    # Start email checker in background
    threading.Thread(target=check_email, daemon=True).start()

    # Start Telegram bot
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()
