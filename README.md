# -fake_job_internship_detector
A Flask-based web application that detects potential fake job and internship scams using text-based risk analysis and provides risk scores, warning signs, and safety recommendations.
# 🛡️ JobShield – Fake Job & Internship Detector

JobShield is a web-based application designed to help students and job seekers identify potentially fake or suspicious job and internship advertisements.

The system analyzes the information provided in a job advertisement and generates a **Risk Score from 0 to 100**, along with warning signs and safety recommendations.

---

## 📌 Project Overview

Fake job and internship advertisements are becoming increasingly common. Students and fresh graduates may receive offers that ask for registration fees, personal information, banking details, or promise unrealistic salaries.

JobShield provides a simple way to screen such advertisements before applying or sharing personal information.

The application checks the entered advertisement for suspicious patterns such as:

- 💰 Registration or processing fee requests
- 🚨 Unrealistic salary or income promises
- ⏰ Urgent or pressure-based language
- 🔐 Requests for sensitive information
- 📱 Suspicious WhatsApp or Telegram communication
- 📄 Missing company or job information
- 🎓 Guaranteed job or internship claims

---

## ✨ Features

### 🔍 Job Advertisement Analysis
Users can enter:

- Company name
- Job or internship title
- Job description

The system analyzes the entered information and calculates a risk score.

### 📊 Risk Score

The system provides a score between **0 and 100**.

| Score | Result |
|------:|--------|
| 0–29 | 🟢 Likely Safe |
| 30–59 | 🟡 Needs Verification |
| 60–100 | 🔴 High Risk |

### 🚨 Warning Detection

JobShield identifies suspicious phrases related to:

- Payment requests
- Unrealistic earnings
- Urgency and pressure
- Sensitive information
- Easy-money claims
- Suspicious communication methods

### 🛡️ Safety Recommendations

After analysis, the application provides recommendations based on the detected risk level.

### 📋 Analysis History

Previous analyses are stored in an SQLite database so users can view their previous results.

### 📈 Dashboard

The dashboard displays:

- Total analyses
- High-risk advertisements
- Advertisements requiring verification
- Likely safe advertisements

---

## 🛠️ Technologies Used

- **Python**
- **Flask**
- **HTML5**
- **CSS3**
- **SQLite**
- **Jinja2**
- **Regular Expression / Text Analysis**

---

## 🏗️ Project Structure

```text
fake_job_internship_detector/
│
├── app.py
├── requirements.txt
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── result.html
│   ├── history.html
│   └── dashboard.html
│
├── static/
│   └── style.css
│
└── detector.db
