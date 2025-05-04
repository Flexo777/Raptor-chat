from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
from datetime import datetime
import os

from app.storage import DatabaseManager

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = DatabaseManager()

# ============================
# AUTH
# ============================

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip()
        password = request.form['password'].strip()

        if not (username and email and password):
            flash("All fields are required.", "error")
            return redirect(url_for('register'))

        existing_user = db.get_user_by_email(email)
        if existing_user:
            flash("Email already registered.", "error")
            return redirect(url_for('register'))

        db.add_user(username, email, password)
        flash("Registration successful. Please login.", "success")
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form['email'].strip()
        password = request.form['password'].strip()

        user = db.get_user_by_email(email)
        if user and db.verify_password(user, password):
            session['user_id'] = user.id
            db.update_user_status(user.id, 1)
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid email or password.", "error")
    return render_template('login.html')

@app.route('/logout')
def logout():
    user_id = session.pop('user_id', None)
    if user_id:
        db.update_user_status(user_id, 0)
    return redirect(url_for('login'))

# ============================
# DASHBOARD
# ============================

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    current_user = db.get_user_by_id(session['user_id'])
    online_users = db.get_online_users()
    online_users = [user for user in online_users if user.id != current_user.id]
    return render_template('dashboard.html', current_user=current_user, online_users=online_users)

# ============================
# CHAT
# ============================

@app.route('/chat/<int:user_id>', methods=['GET', 'POST'])
def chat(user_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    current_user = db.get_user_by_id(session['user_id'])
    partner = db.get_user_by_id(user_id)

    if not partner:
        flash("User not found.", "error")
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        text_message = request.form.get('message', '').strip()
        media = request.files.get('media')
        message_type = 'text'
        content = ''

        if media and media.filename:
            filename = secure_filename(media.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            media.save(filepath)
            content = filename
            if filename.lower().endswith(('.mp4', '.avi', '.mov')):
                message_type = 'video'
            else:
                message_type = 'image'
        elif text_message:
            message_type = 'text'
            content = text_message

        if content:
            db.save_message(
                sender_id=current_user.id,
                receiver_id=partner.id,
                message_type=message_type,
                content=content,
                timestamp=datetime.now().isoformat()
            )
        return redirect(url_for('chat', user_id=partner.id))

    messages = db.get_messages(current_user.id, partner.id)
    return render_template('chat.html', current_user=current_user, partner=partner, messages=messages)

# ============================
# RUN
# ============================

if __name__ == '__main__':
    app.run(debug=True)
