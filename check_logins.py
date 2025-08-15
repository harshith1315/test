# check_logins.py
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import pytz
import smtplib
from email.mime.text import MIMEText

# Google Sheets setup
scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("config.json", scope)
client = gspread.authorize(creds)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1ak8GBZvnj2gBiuj3z-AhjcbRWyuhPSVlnrHG7zOiIFE/edit?usp=sharing"
sheet = client.open_by_url(SHEET_URL).sheet1

# Email credentials (from GitHub Secrets in Actions)
SENDER_EMAIL = "deeplearning.harshith@gmail.com"
SENDER_PASS = "harshith1234"

CUTOFF = "09:30:00"  # time for reminder
IST = pytz.timezone("Asia/Kolkata")

def send_email(to_email, name, reason):
    """Send email notification."""
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
    """Get column indices based on header names."""
    headers = [h.strip().lower() for h in sheet.row_values(1)]
    header_map = {}
    try:
        header_map["email"] = headers.index("email") + 1
        header_map["login"] = headers.index("login") + 1
        header_map["logout"] = headers.index("logout") + 1
    except ValueError as e:
        raise ValueError(f"Missing expected column in sheet: {e}")
    return header_map

def check_now():
    """Check logins and send reminders."""
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
    records = sheet.get_all_records()
    
    for row in records:
        email = (row.get("email") or "").strip()
        name = email.split("@")[0] if email else "Employee"
        login_time = (row.get("login") or "").strip()

        if not email:
            continue

        # Send email if no login or late login
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
