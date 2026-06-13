from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import os
from datetime import datetime

app = Flask(__name__)

# Secret key for session (change this to anything you want)
app.secret_key = os.environ.get('SECRET_KEY', 'reachout-secret-2025')

# Admin password — set ADMIN_PASSWORD in Vercel env vars
# If not set, default password is: admin123
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')

# In-memory storage for submissions
submissions = []


# ─── HOME / CONTACT FORM ─────────────────────────────────────────────────────
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


# ─── HANDLE FORM SUBMISSION (CREATE) ─────────────────────────────────────────
@app.route('/submit', methods=['POST'])
def submit():
    name    = request.form.get('name', '').strip()
    email   = request.form.get('email', '').strip()
    subject = request.form.get('subject', '').strip()
    message = request.form.get('message', '').strip()

    errors = []
    if not name:
        errors.append('Name is required.')
    if not email or '@' not in email:
        errors.append('A valid email is required.')
    if not message:
        errors.append('Message cannot be empty.')

    if errors:
        return jsonify({'success': False, 'errors': errors}), 400

    entry = {
        'id':        len(submissions) + 1,
        'name':      name,
        'email':     email,
        'subject':   subject or 'No subject',
        'message':   message,
        'timestamp': datetime.utcnow().strftime('%d %b %Y, %H:%M UTC'),
    }
    submissions.append(entry)

    return jsonify({'success': True, 'message': f"Thanks {name}! Your message has been received."})


# ─── ADMIN LOGIN PAGE ─────────────────────────────────────────────────────────
@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    error = None
    if request.method == 'POST':
        password = request.form.get('password', '').strip()
        if password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('admin'))
        else:
            error = 'Wrong password. Try again.'
    return render_template('login.html', error=error)


# ─── ADMIN LOGOUT ─────────────────────────────────────────────────────────────
@app.route('/admin-logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))


# ─── ADMIN PANEL (READ) ───────────────────────────────────────────────────────
@app.route('/admin', methods=['GET'])
def admin():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    return render_template('admin.html', submissions=list(reversed(submissions)))


# ─── DELETE SUBMISSION (DELETE) ───────────────────────────────────────────────
@app.route('/delete/<int:sub_id>', methods=['POST'])
def delete(sub_id):
    if not session.get('admin_logged_in'):
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    global submissions
    submissions = [s for s in submissions if s['id'] != sub_id]
    return jsonify({'success': True})


if __name__ == '__main__':
    app.run(debug=True, port=5000)
