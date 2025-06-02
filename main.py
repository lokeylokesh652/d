import imaplib
import email
import re
import time
import requests
import threading
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ====== CONFIGURATION ======
GMAIL_USER = 'indoigg0111@gmail.com'
GMAIL_PASSWORD = 'esaneurrvpmcxdnk'
TELEGRAM_BOT_TOKEN = '7485486399:AAFSA0M5O5jePlIQw-hLsia_8Nv6XmjhEUw'
TELEGRAM_CHAT_ID = '7437878492'

# ─── Telegram Bot ─────────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "👋 *Welcome to OTP Bot*\n\n"
        "I monitor Gmail and send OTPs from Instagram.\n\n"
        "*You'll receive OTPs here automatically.*"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    requests.post(url, data=payload)

# ─── Email Monitor ─────────────────────────────────────────────────────
def check_email_loop():
    print("🚀 OTP Bot started... waiting for new emails.")
    while True:
        try:
            mail = imaplib.IMAP4_SSL("imap.gmail.com")
            mail.login(GMAIL_USER, GMAIL_PASSWORD)
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
                    message = f"📨 New Instagram OTP: `{otp}`"
                    print(message)
                    send_telegram_message(message)
                else:
                    print("OTP not found in email.")

            mail.logout()
        except Exception as e:
            print(f"Error: {e}")

        time.sleep(10)

# ─── Main ─────────────────────────────────────────────────────
if __name__ == '__main__':
    # Start email checker thread
    threading.Thread(target=check_email_loop, daemon=True).start()

    # Start Telegram bot
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()
