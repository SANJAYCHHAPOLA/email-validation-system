# Email Validation and Deliverability Analysis System
A complete 8-step email validation pipeline built during a Data Science internship.

## Project Overview
The company had a raw dataset of 10,525 financial services contacts. The goal was to identify which email addresses were real, active, and safe to 
send to — without bouncing.
This project builds a full pipeline from raw data to validated, risk-rated output, and packages it as a Flask web application.

## Key Results
- 10,525 raw contacts processed
- 7,261 verified, risk-rated emails delivered
- 18% data decay rate identified (confirmed dead emails)
- 35% catch-all domains detected via SMTP sampling
- 97% of validated emails rated LOW RISK (safe to send)

## Validation Pipeline (8 Steps)

| Step | Task                    | Method                            |

| 1    | Remove null emails      | `df.dropna()`                     |
| 2    | Clean text quality      | `str.strip()`, `str.lower()`      |
| 3    | Remove duplicates       | `drop_duplicates()`               |
| 4    | Email format check      | Regex pattern matching            |
| 5    | Domain validation       | DNS / MX record lookup            |
| 6    | Risk assessment         | LOW / MEDIUM / HIGH               |
| 7    | Generate output files   | CSV + JSON reports                |
| 8    | SMTP verification       | Statistical sampling (150 emails) |


## Web Application

A Flask web app wraps the full pipeline into a browser-based tool — no Python knowledge needed.

**Features:**
- Single email check with instant results
- Bulk CSV upload and validation
- 4-layer validation: Syntax, Domain, SMTP, Risk
- Safe to Send: YES / NO for every email

**To run locally:**
```bash
git clone https://github.com/sanjaychhapola/email-validation-system.git
cd email-validation-system
pip install -r requirements.txt
python app.py
# Open: http://localhost:5000
```

---

## Project Structure
