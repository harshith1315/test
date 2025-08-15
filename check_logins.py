# check_logins.py
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import smtplib

# ---------------- Google Sheets Setup ----------------
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name("config.json", scope)
client = gspread.authorize(creds)

SHEET_URL = "https://docs.google.com/spreadsheets/d/1ak8GBZvnj2gBiuj3z-AhjcbRWyuhPSVlnrHG7zOiIFE/edit?usp=sharing"
sheet = client.open_by_url(SHEET_URL).sheet1

# ---------------- Email Setup ----------------
SENDER_EMAIL = "deeplearing.harshith@gmail.com"
SENDER_PASS = "tlfk vdit gfvc jnjj"  # or use environment variable

# ---------------- Functions ----------------
def send_email(to_email):
    """Send simple email if login is empty."""
    subject = "Login Reminder"
    body = f"Hi ,\n\nYou have not logged in today. Please log in.\n\n— Automated Reminder"
    message = f"Subject: {subject}\n\n{body}"

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login('deeplearning.harshith@gmail.com', 'tlfk vdit gfvc jnjj')
    server.sendmail('deeplearning.harshith@gmail.com', to_email, message.encode('utf-8'))
    server.quit()
    print('Mail sent')


def check_logins():
    """Check the login column and send email if empty."""
    records = sheet.get_all_records()
    # print(records)
    for row in records:
        email = (row.get("email") or "").strip()
        print(email)
        login_time = (row.get("login") or "").strip()
        print(login_time)
        name = email.split("@")[0] if email else "Employee"

        if login_time is '':
            send_email(email)
        else:
            print(f"{name} has logged in.")

# ---------------- Main ----------------
if __name__ == "__main__":
    check_logins()
