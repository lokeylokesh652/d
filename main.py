import imaplib
import email
import re
import time
import requests

# ====== CONFIGURATION ======
GMAIL_USER = 'indoigg0111@gmail.com'
GMAIL_PASSWORD = 'esaneurrvpmcxdnk'  # Use your Gmail App Password here
TELEGRAM_BOT_TOKEN = '7485486399:AAFSA0M5O5jePlIQw-hLsia_8Nv6XmjhEUw'
TELEGRAM_CHAT_ID = '7437878492'

# ====== Send Telegram Message ======
def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"  # ✅ Monospace formatting enabled
    }
    requests.post(url, data=payload)

# ====== Check Gmail Inbox for OTP ======
def check_email():
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(GMAIL_USER, GMAIL_PASSWORD)
    print("✅ Logged into Gmail successfully.")
    mail.select("inbox")

    # Search for unread emails from Instagram
    result, data = mail.search(None, '(UNSEEN FROM "no-reply@mail.instagram.com")')
    email_ids = data[0].split()

    for e_id in email_ids:
        result, msg_data = mail.fetch(e_id, "(RFC822)")
        mail.store(e_id, '+FLAGS', '\\Seen')  # ✅ Mark as read immediately

        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)

        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode()
        else:
            body = msg.get_payload(decode=True).decode()

        # Search for 6-digit OTP
        otp_match = re.search(r'\b\d{6}\b', body)
        if otp_match:
            otp = otp_match.group()
            message = f"📨 New Instagram OTP: `{otp}`"  # ✅ Wrapped in backticks
            print(message)
            send_telegram_message(message)
        else:
            print("OTP not found in email.")

    mail.logout()

# ====== Main Loop ======
if __name__ == "__main__":
    print("🚀 OTP Bot started... waiting for new emails.")
    while True:
        try:
            check_email()
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(10)
