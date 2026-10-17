from flask import Flask, request, jsonify, render_template
import re
import smtplib
import dns.resolver
import socket
import pandas as pd
import time
import random
import string

app = Flask(__name__)


def validate_syntax(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, 'Invalid email format'
    local, domain = email.split('@')
    if local.startswith('.') or local.endswith('.'):
        return False, 'Local part cannot start or end with a dot'
    if '..' in local:
        return False, 'Consecutive dots not allowed'
    return True, 'Valid syntax'


def validate_domain(email):
    try:
        domain = email.split('@')[1]
        mx_records = dns.resolver.resolve(domain, 'MX')
        mx_host = str(sorted(mx_records, key=lambda x: x.preference)[0].exchange).rstrip('.')
        return True, f'MX records found ({mx_host})', mx_host
    except dns.resolver.NXDOMAIN:
        return False, 'Domain does not exist', None
    except dns.resolver.NoAnswer:
        return False, 'No MX records found', None
    except Exception as e:
        return False, str(e), None


def check_catch_all(domain, mx_host, timeout=8):
    fake_local = ''.join(random.choices(string.ascii_lowercase, k=20))
    fake_email = f"{fake_local}@{domain}"
    try:
        server = smtplib.SMTP(timeout=timeout)
        server.connect(mx_host, 25)
        server.helo('verifier.local')
        server.mail('check@verifier.local')
        code, message = server.rcpt(fake_email)
        server.quit()
        return code == 250
    except Exception:
        return None


def validate_smtp(email, mx_host, timeout=8):
    try:
        domain = email.split('@')[1]
        is_catch_all = check_catch_all(domain, mx_host, timeout)
        if is_catch_all:
            return 'CATCH_ALL', 'Domain accepts all emails - cannot verify individual mailbox'
        server = smtplib.SMTP(timeout=timeout)
        server.connect(mx_host, 25)
        server.helo('verifier.local')
        server.mail('check@verifier.local')
        code, message = server.rcpt(email)
        server.quit()
        if code == 250:
            return 'EXISTS', 'Mailbox confirmed (250 OK)'
        elif code == 550:
            return 'NOT_EXISTS', 'User unknown (550)'
        else:
            return 'UNCERTAIN', f'Code {code}'
    except smtplib.SMTPServerDisconnected:
        return 'BLOCKED', 'Server blocked verification'
    except (smtplib.SMTPConnectError, ConnectionRefusedError, OSError):
        return 'PORT_BLOCKED', 'Port 25 blocked on this server'
    except socket.timeout:
        return 'TIMEOUT', 'Server timeout'
    except Exception as e:
        return 'ERROR', str(e)


def assess_risk(email):
    local = email.split('@')[0].lower()
    role_based = ['info', 'admin', 'sales', 'support', 'contact',
                  'hello', 'noreply', 'help', 'service', 'team',
                  'billing', 'accounts']
    suspicious = ['test', 'demo', 'fake', 'sample', 'dummy', 'temp']
    if any(local == r for r in role_based):
        return 'MEDIUM', 'Role-based email (team inbox)'
    if any(s in local for s in suspicious):
        return 'HIGH', 'Suspicious pattern detected'
    return 'LOW', 'Individual email address'


def validate_email_full(email):
    email = email.strip().lower()
    result = {
        'email': email,
        'overall': 'UNKNOWN',
        'safe_to_send': False,
        'checks': {
            'syntax': {'passed': False, 'message': ''},
            'domain': {'passed': False, 'message': ''},
            'smtp': {'status': 'NOT_CHECKED', 'message': ''},
            'risk': {'level': 'UNKNOWN', 'message': ''}
        }
    }

    syntax_valid, syntax_msg = validate_syntax(email)
    result['checks']['syntax']['passed'] = syntax_valid
    result['checks']['syntax']['message'] = syntax_msg
    if not syntax_valid:
        result['overall'] = 'INVALID'
        return result

    domain_valid, domain_msg, mx_host = validate_domain(email)
    result['checks']['domain']['passed'] = domain_valid
    result['checks']['domain']['message'] = domain_msg
    if not domain_valid:
        result['overall'] = 'INVALID'
        return result

    smtp_status, smtp_msg = validate_smtp(email, mx_host)
    result['checks']['smtp']['status'] = smtp_status
    result['checks']['smtp']['message'] = smtp_msg

    risk_level, risk_msg = assess_risk(email)
    result['checks']['risk']['level'] = risk_level
    result['checks']['risk']['message'] = risk_msg

    if smtp_status == 'NOT_EXISTS':
        result['overall'] = 'INVALID'
        result['safe_to_send'] = False
    elif smtp_status == 'EXISTS' and risk_level != 'HIGH':
        result['overall'] = 'VALID'
        result['safe_to_send'] = True
    elif smtp_status in ['CATCH_ALL', 'PORT_BLOCKED', 'TIMEOUT', 'BLOCKED', 'ERROR']:
        result['overall'] = 'UNCERTAIN'
        result['safe_to_send'] = False
    elif risk_level == 'HIGH':
        result['overall'] = 'RISKY'
        result['safe_to_send'] = False
    else:
        result['overall'] = 'UNCERTAIN'
        result['safe_to_send'] = False

    return result


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/validate', methods=['POST'])
def validate():
    data = request.get_json()
    email = data.get('email', '').strip()
    if not email:
        return jsonify({'error': 'No email provided'}), 400
    result = validate_email_full(email)
    return jsonify(result)


@app.route('/validate-bulk', methods=['POST'])
def validate_bulk():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    file = request.files['file']
    if not file.filename.endswith('.csv'):
        return jsonify({'error': 'Please upload a CSV file'}), 400
    try:
        df = pd.read_csv(file)
        email_col = None
        for col in df.columns:
            if 'email' in col.lower():
                email_col = col
                break
        if not email_col:
            return jsonify({'error': 'No email column found in CSV'}), 400
        emails = df[email_col].dropna().head(50).tolist()
        results = []
        for email in emails:
            result = validate_email_full(str(email))
            results.append(result)
            time.sleep(1)
        summary = {
            'total': len(results),
            'valid': sum(1 for r in results if r['overall'] == 'VALID'),
            'invalid': sum(1 for r in results if r['overall'] == 'INVALID'),
            'uncertain': sum(1 for r in results if r['overall'] == 'UNCERTAIN'),
            'risky': sum(1 for r in results if r['overall'] == 'RISKY'),
            'results': results
        }
        return jsonify(summary)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)