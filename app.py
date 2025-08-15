from flask import Flask, request, jsonify, render_template
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import pytz

app = Flask(__name__)

# Google Sheets auth
scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("config.json", scope)
client = gspread.authorize(creds)

SHEET_URL = "https://docs.google.com/spreadsheets/d/1ak8GBZvnj2gBiuj3z-AhjcbRWyuhPSVlnrHG7zOiIFE/edit?usp=sharing"
sheet = client.open_by_url(SHEET_URL).sheet1

IST = pytz.timezone("Asia/Kolkata")

def normalize_headers(headers):
    return [h.strip().lower() for h in headers]

@app.route("/")
def home():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json(force=True)
    email = (data.get("email") or "").strip()
    if not email:
        return jsonify({"message": "Email is required"}), 400

    # Read all values once; header row is row 1
    values = sheet.get_all_values()
    if not values:
        return jsonify({"message": "Sheet is empty"}), 500

    headers = normalize_headers(values[0])
    try:
        email_col = headers.index("email") + 1
        login_col = headers.index("login") + 1
        emp_col   = headers.index("employee") + 1
    except ValueError:
        return jsonify({"message": "Sheet must have 'employee', 'email', 'login' headers"}), 500

    # Search for the row with matching email (case-insensitive)
    target_row_idx = None
    for r_idx in range(2, len(values) + 1):  # 1-based rows; skip header
        cell_val = (sheet.cell(r_idx, email_col).value or "").strip().lower()
        if cell_val == email.lower():
            target_row_idx = r_idx
            break

    if not target_row_idx:
        return jsonify({"message": "Email not found in records"}), 404

    now_ist = datetime.now(IST).strftime("%H:%M:%S")
    sheet.update_cell(target_row_idx, login_col, now_ist)
    return jsonify({"message": f"Login successful at {now_ist}"}), 200

if __name__ == "__main__":
    app.run(debug=True)
