# Email Validation and Deliverability Analysis System
A complete email validation pipeline and web-based tool built during a Data Science internship.

## Project Overview
Built an end-to-end email validation system for a dataset of 10,525  financial services contacts. The system cleans, validates, and risk-rates 
email addresses across multiple layers, and is deployed as a live web application accessible from any browser.

## Key Results
- Processed 10,525 raw contact records
- Delivered 7,261 verified, risk-rated emails
- Identified 18% data decay rate (confirmed dead emails)
- Detected catch-all domains using SMTP sampling
- Deployed as live web product (no Python knowledge needed)

## Features
- Single email validation with instant results
- Bulk CSV upload for multiple email validation
- 4-layer validation: Syntax, Domain, SMTP, Risk
- Risk rating: LOW / MEDIUM / HIGH
- Safe to Send: YES / NO decision for every email

## Validation Pipeline (8 Steps)
1. Remove null/missing email rows
2. Clean text quality (spaces, lowercase)
3. Remove exact duplicate entries
4. Email format validation using Regex
5. Domain validation via DNS/MX record lookup
6. Risk assessment (LOW / MEDIUM / HIGH)
7. Generate organized output files by risk level
8. SMTP verification using statistical sampling

## Technology Stack
| Category              | Technology |
|----------             |-----------|
| Language              | Python, JavaScript, HTML/CSS |
| Data Processing       | Pandas, NumPy, openpyxl |
| Web Framework         | Flask |
| Email Validation      | dnspython, smtplib, Regex |
| Deployment            | PythonAnywhere |
| Development           | Jupyter Notebook, Google Colab |

## Validation Layers Explained
- **Syntax Check** — Regex pattern matching for email format
- **Domain Check** — DNS lookup + MX record verification
- **SMTP Check** — Connects to mail server, checks mailbox existence
- **Risk Assessment** — Classifies email as individual, role-based, or suspicious

## Project Structure
