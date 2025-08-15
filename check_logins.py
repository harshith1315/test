# check_logins.py
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import pytz
import smtplib
from email.mime.text import MIMEText

# Google Sheets
scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("config.json", scope)
client = gspread.authorize(creds)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1ak8GBZvnj2gBiuj3z-AhjcbRWyuhPSVlnrHG7zOiIFE/edit?usp=sharing"
sheet = client.open_by_url(SHEET_URL).sheet1

# Email creds from env (GitHub Secrets will provide these)
SENDER_EMAIL = "deeplearning,harshith@gmail.com"
SENDER_PASS = "harshith1234"

CUTOFF = "09:30:00"  # used in the email text
IST = pytz.timezone("Asia/Kolkata")

def send_email(to_email, name, reason):
    body = f"Hi {name},\n\n{reason}\n\n— Automated Reminder"
    msg = MIMEText(body)
    msg["Subject"] = "Login Reminder"
    msg["From"] = SENDER_EMAIL
    msg["To"] = to_email

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASS)
        server.sendmail(SENDER_EMAIL, to_email, msg.as_string())

def get_headers():
    headers = [h.strip().lower() for h in sheet.row_values(1)]
    return {
        "employee": headers.index("employee") + 1,
        "email": headers.index("email") + 1,
        "login": headers.index("login") + 1
    }

def check_now():
    # Decide reason based on time-of-day (09:30, 15:00, 18:00 IST)
    now = datetime.now(IST)
    hour_min = now.strftime("%H:%M")

    if hour_min == "09:30":
        reason = f"You have not logged in before {CUTOFF} today. Please log in immediately."
    elif hour_min == "15:00":
        reason = "Reminder: You still have not logged in today. Please log in."
    elif hour_min == "18:00":
        reason = "Final reminder for today: please log in."
    else:
        reason = "You have not logged in yet today. Please log in."

    cols = get_headers()
    records = sheet.get_all_records()  # dicts with header keys
    for row in records:
        name = (row.get("employee") or "Employee").strip()
        email = (row.get("email") or "").strip()
        login_time = (row.get("login") or "").strip()

        if not email:
            continue

        # Send if missing OR (optional) later than cutoff
        if not login_time:
            send_email(email, name, reason)
            print(f"Email sent to {name} ({email}) - No login")
        elif login_time > CUTOFF:
            send_email(email, name, f"You logged in at {login_time}, which is after {CUTOFF}.")
            print(f"Email sent to {name} ({email}) - Late login at {login_time}")
        else:
            print(f"{name} logged in on time at {login_time}")

if __name__ == "__main__":
    check_now()
