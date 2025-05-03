from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from app.network import Server, NetworkScanner
from app.security import Encryption
from app.storage import DatabaseManager, User
import threading
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Inisialisasi komponen
db_manager = DatabaseManager()
encryption = Encryption()

# Dummy data untuk contoh
users = [
    User(id=1, username="Gregory Floyd", email="gregory@example.com", online=True),
    User(id=2, username="Sandy Smith", email="sandy@example.com", online=True),
    User(id=3, username="Leroy Floyd", email="leroy@example.com", online=False)
]

# Route untuk halaman login
@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            return render_template('login.html', error="Email and password are required")
        
        # Validasi login (sederhana)
        user = next((u for u in users if u.email == email), None)
        if user:
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('dashboard'))
        
        return render_template('login.html', error="Invalid credentials")
    
    return render_template('login.html')

# Route untuk halaman register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        gender = request.form.get('gender')
        
        if not all([username, email, password]):
            return render_template('register.html', error="All fields are required")
        
        # Buat user baru
        new_user = User(
            id=len(users) + 1,
            username=username,
            email=email,
            online=True
        )
        users.append(new_user)
        
        # Login user baru
        session['user_id'] = new_user.id
        session['username'] = new_user.username
        return redirect(url_for('dashboard'))
    
    return render_template('register.html')

# Route untuk dashboard
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    current_user = next((u for u in users if u.id == session['user_id']), None)
    if not current_user:
        session.clear()
        return redirect(url_for('login'))
    
    online_users = [u for u in users if u.online and u.id != current_user.id]
    
    recent_activity = [
        {"message": "Connected to chat server", "timestamp": "Just now"},
        {"message": "Logged in successfully", "timestamp": "2 minutes ago"}
    ]
    
    return render_template('dashboard.html', 
                         current_user=current_user,
                         online_users=online_users,
                         recent_activity=recent_activity)

# Route untuk halaman chat utama
@app.route('/chat')
def chat():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    current_user = next((u for u in users if u.id == session['user_id']), None)
    if not current_user:
        session.clear()
        return redirect(url_for('login'))
    
    return render_template('chat.html', current_user=current_user)

# Route untuk memulai chat dengan user tertentu
@app.route('/chat/<int:user_id>')
def start_chat(user_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    current_user = next((u for u in users if u.id == session['user_id']), None)
    if not current_user:
        session.clear()
        return redirect(url_for('login'))
    
    partner = next((u for u in users if u.id == user_id), None)
    if not partner:
        return redirect(url_for('dashboard'))
    
    # Dummy messages
    messages = [
        {"sender_id": current_user.id, "content": "Hi there!", "timestamp": datetime.now()},
        {"sender_id": partner.id, "content": "Hello! How are you?", "timestamp": datetime.now()},
        {"sender_id": current_user.id, "content": "I'm good, thanks!", "timestamp": datetime.now()}
    ]
    
    return render_template('chat.html', 
                         current_user=current_user,
                         partner=partner,
                         messages=messages)

# Route untuk logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

def run_chat_server():
    try:
        server = Server(port=12346)  # Gunakan port berbeda
        print("Starting chat server on port 12346...")
        server.start()
    except OSError as e:
        print(f"[ERROR] Failed to start chat server: {e}")
    except Exception as e:
        print(f"[ERROR] Unexpected error in chat server: {e}")

if __name__ == '__main__':
    # Buat folder static dan subfolder jika belum ada
    os.makedirs('static/images', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    
    # Jalankan server chat di thread terpisah
    server_thread = threading.Thread(target=run_chat_server, daemon=True)
    server_thread.start()
    
    # Jalankan aplikasi Flask
    app.run(debug=True, port=5000)