from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import re
from datetime import datetime

app = Flask(__name__)

DATABASE = "detector.db"


# ---------------- DATABASE ----------------

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT,
            job_title TEXT,
            description TEXT,
            score INTEGER,
            status TEXT,
            reasons TEXT,
            created_at TEXT
        )
    """)

    conn.commit()
    conn.close()


# ---------------- DETECTION RULES ----------------

RULES = {

    "Payment Request": {
        "keywords": [
            "registration fee",
            "application fee",
            "processing fee",
            "joining fee",
            "security deposit",
            "pay money",
            "pay a fee",
            "send money",
            "payment required",
            "deposit amount",
            "training fee",
            "certificate fee"
        ],
        "score": 25
    },

    "Unrealistic Income": {
        "keywords": [
            "earn ₹1 lakh",
            "earn rs 1 lakh",
            "earn 1 lakh",
            "earn 100000",
            "₹50000 per day",
            "₹1 lakh per day",
            "10000 per day",
            "20000 per day",
            "guaranteed income",
            "guaranteed salary",
            "unlimited income",
            "huge income",
            "easy money"
        ],
        "score": 20
    },

    "Urgency / Pressure": {
        "keywords": [
            "limited seats",
            "apply immediately",
            "apply now",
            "act now",
            "urgent",
            "today only",
            "last chance",
            "offer expires",
            "limited time",
            "respond immediately"
        ],
        "score": 15
    },

    "Sensitive Information": {
        "keywords": [
            "otp",
            "password",
            "bank account",
            "bank details",
            "atm pin",
            "card number",
            "credit card",
            "debit card",
            "upi pin",
            "aadhaar number",
            "pan card number"
        ],
        "score": 25
    },

    "Easy Money Claims": {
        "keywords": [
            "work 1 hour",
            "work 2 hours",
            "earn from home",
            "no experience required",
            "no skills required",
            "earn while sleeping",
            "get rich",
            "instant income",
            "guaranteed job",
            "guaranteed placement"
        ],
        "score": 10
    },

    "Suspicious Contact": {
        "keywords": [
            "contact only on whatsapp",
            "whatsapp only",
            "telegram only",
            "contact on telegram",
            "message this number",
            "send your details to whatsapp"
        ],
        "score": 10
    }
}


def detect_risk(company, job_title, description):

    text = f"{company} {job_title} {description}".lower()

    score = 0
    reasons = []

    # Check suspicious keywords
    for category, rule in RULES.items():

        found = []

        for keyword in rule["keywords"]:

            if keyword.lower() in text:
                found.append(keyword)

        if found:
            score += rule["score"]

            reasons.append({
                "category": category,
                "keywords": found
            })

    # Missing information checks

    if not company.strip():
        score += 10
        reasons.append({
            "category": "Missing Company Information",
            "keywords": ["Company name not provided"]
        })

    if not job_title.strip():
        score += 5
        reasons.append({
            "category": "Missing Job Information",
            "keywords": ["Job title not provided"]
        })

    if len(description.strip()) < 80:
        score += 10
        reasons.append({
            "category": "Insufficient Job Details",
            "keywords": ["Very short job description"]
        })

    # Positive indicators reduce risk slightly

    positive_terms = [
        "official website",
        "job responsibilities",
        "requirements",
        "experience",
        "qualifications",
        "interview",
        "company address",
        "company email"
    ]

    positive_count = 0

    for term in positive_terms:
        if term in text:
            positive_count += 1

    score -= positive_count * 2

    # Keep score between 0 and 100
    score = max(0, min(score, 100))

    # Determine status

    if score >= 60:
        status = "High Risk"

    elif score >= 30:
        status = "Needs Verification"

    else:
        status = "Likely Safe"

    return score, status, reasons


# ---------------- HOME PAGE ----------------

@app.route("/")
def index():

    return render_template("index.html")


# ---------------- ANALYZE ----------------

@app.route("/analyze", methods=["POST"])
def analyze():

    company = request.form.get("company", "").strip()
    job_title = request.form.get("job_title", "").strip()
    description = request.form.get("description", "").strip()

    if not description:

        return redirect(url_for("index"))

    score, status, reasons = detect_risk(
        company,
        job_title,
        description
    )

    reason_text = ""

    for reason in reasons:

        reason_text += reason["category"] + ": "

        reason_text += ", ".join(reason["keywords"])

        reason_text += "\n"

    conn = get_db()

    cursor = conn.execute("""
        INSERT INTO analyses
        (
            company,
            job_title,
            description,
            score,
            status,
            reasons,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        company,
        job_title,
        description,
        score,
        status,
        reason_text,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    analysis_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return redirect(url_for(
        "result",
        analysis_id=analysis_id
    ))


# ---------------- RESULT ----------------

@app.route("/result/<int:analysis_id>")
def result(analysis_id):

    conn = get_db()

    analysis = conn.execute("""
        SELECT *
        FROM analyses
        WHERE id = ?
    """, (analysis_id,)).fetchone()

    conn.close()

    if not analysis:
        return redirect(url_for("index"))

    reasons = []

    if analysis["reasons"]:

        for line in analysis["reasons"].split("\n"):

            if ":" in line:

                category, keywords = line.split(":", 1)

                reasons.append({
                    "category": category.strip(),
                    "keywords": keywords.strip()
                })

    recommendations = []

    if analysis["score"] >= 60:

        recommendations = [
            "Do not send money or pay any registration fee.",
            "Do not share OTP, passwords, bank details or UPI PIN.",
            "Verify the company using its official website.",
            "Search for the company and job independently.",
            "Do not trust urgent payment or joining requests."
        ]

    elif analysis["score"] >= 30:

        recommendations = [
            "Verify the company before applying.",
            "Check whether the company has an official website.",
            "Look for the same job opening on trusted job portals.",
            "Do not make any payment without verification.",
            "Avoid sharing sensitive financial information."
        ]

    else:

        recommendations = [
            "The advertisement does not show many obvious warning signs.",
            "Still verify the company and recruiter before accepting an offer.",
            "Never share OTPs, passwords or banking PINs.",
            "Check the official company website and contact information."
        ]

    return render_template(
        "result.html",
        analysis=analysis,
        reasons=reasons,
        recommendations=recommendations
    )


# ---------------- HISTORY ----------------

@app.route("/history")
def history():

    conn = get_db()

    analyses = conn.execute("""
        SELECT *
        FROM analyses
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return render_template(
        "history.html",
        analyses=analyses
    )


# ---------------- DASHBOARD ----------------

@app.route("/dashboard")
def dashboard():

    conn = get_db()

    total = conn.execute("""
        SELECT COUNT(*) AS count
        FROM analyses
    """).fetchone()["count"]

    high_risk = conn.execute("""
        SELECT COUNT(*) AS count
        FROM analyses
        WHERE status = 'High Risk'
    """).fetchone()["count"]

    verify = conn.execute("""
        SELECT COUNT(*) AS count
        FROM analyses
        WHERE status = 'Needs Verification'
    """).fetchone()["count"]

    safe = conn.execute("""
        SELECT COUNT(*) AS count
        FROM analyses
        WHERE status = 'Likely Safe'
    """).fetchone()["count"]

    conn.close()

    return render_template(
        "dashboard.html",
        total=total,
        high_risk=high_risk,
        verify=verify,
        safe=safe
    )


# ---------------- CLEAR HISTORY ----------------

@app.route("/clear-history")
def clear_history():

    conn = get_db()

    conn.execute("DELETE FROM analyses")

    conn.commit()
    conn.close()

    return redirect(url_for("history"))


# ---------------- RUN APP ----------------

if __name__ == "__main__":

    init_db()

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )