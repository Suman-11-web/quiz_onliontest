import os
import sqlite3
import json
from datetime import datetime
from flask import Flask, render_template, jsonify, request, session, redirect, url_for

app = Flask(__name__)
app.secret_key = "suman_academy_pro_v4_master_reset"

# Absolute paths so Pydroid 3 never gets confused
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'students.db')
QUESTIONS_FILE = os.path.join(BASE_DIR, 'questions.json')

# Student credentials
STUDENTS_LIST = {
    "Suman": "Suman@2026", "Kiran": "Kiran123", "Rahul": "Rah@456",
    "Priya": "Priya_88", "Arun": "Arun#77", "Deepa": "Deepa101",
    "Vijay": "Vijay_Pro", "Ananya": "Anu@2026", "Suraj": "Suraj#22",
    "Meghana": "Meg_456", "Chethan": "Chethu_1", "Sneha": "Sne@99",
    "Manoj": "Manoj_Pro", "Pooja": "Pooja_88", "Harish": "Hari@123",
    "Divya": "Divu_00", "Santhosh": "Santhu#1", "Roopa": "Roopa_123",
    "Naveen": "Nav@99", "Kavya": "Kavya_2026"
}

# Initialize SQLite DB
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS users (username TEXT UNIQUE, password TEXT)')
    cursor.execute('CREATE TABLE IF NOT EXISTS scores (username TEXT, score INTEGER, timestamp TEXT)')
    
    for name, pwd in STUDENTS_LIST.items():
        try:
            cursor.execute("INSERT INTO users VALUES (?, ?)", (name, pwd))
        except:
            pass
    conn.commit()
    conn.close()

init_db()

# Home Page / Quiz
@app.route('/')
def home():
    if 'user' in session:
        return render_template('index.html', user=session['user'])
    return render_template('login.html')

# Login Route 
@app.route('/login', methods=['POST'])
def login():
    u = request.form.get('username', '').strip()
    p = request.form.get('password', '').strip()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE LOWER(username)=LOWER(?) AND password=?", (u, p))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        session.clear() # Clear old data
        session.permanent = True
        session['user'] = user[0]
        return redirect(url_for('home'))
        
    error_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Access Denied</title>
        <link rel="stylesheet" href="/static/style.css?v=11">
    </head>
    <body style="background: linear-gradient(-45deg, #2a0808, #1a0000, #3d0000);">
        <div class="intro-overlay" style="animation: fadeOutOverlay 0.8s forwards 0.8s; background: #1a0000;">
            <div class="magic-orb" style="background: linear-gradient(135deg, #ff416c, #ff4b2b); box-shadow: 0 0 50px rgba(255, 65, 108, 0.6);"></div>
            <div style="color: #ff416c; font-weight: 900; letter-spacing: 5px; text-shadow: 0 0 10px #ff416c;">SECURITY ALERT</div>
        </div>
        <div class="main-card" style="border: 1px solid rgba(255,65,108,0.3);">
            <h2 class="epic-title" style="background: linear-gradient(90deg, #ff416c, #ff4b2b); -webkit-background-clip: text; text-shadow: 0 0 20px rgba(255, 65, 108, 0.3);">ACCESS DENIED</h2>
            <p style="color: #94a3b8; font-size: 1rem; font-weight: bold; margin-top: 15px;">Invalid Username or Password.</p>
            <div style="margin-top: 25px;">
                <a href="/" style="text-decoration: none;">
                    <button class="btn-login" style="background: linear-gradient(90deg, #ff416c, #ff4b2b); box-shadow: 0 0 20px rgba(255, 65, 108, 0.4);">RETRY LOGIN</button>
                </a>
            </div>
        </div>
    </body>
    </html>
    """
    return error_html

# API: Questions
@app.route('/api/questions')
def get_questions():
    try:
        with open(QUESTIONS_FILE, 'r', encoding='utf-8') as f:
            return jsonify(json.load(f))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Save Score
@app.route('/save_score', methods=['POST'])
def save_score():
    if 'user' not in session:
        return jsonify({"error": "Not logged in"}), 401

    data = request.get_json()
    score = int(data.get('score', 0))
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO scores VALUES (?,?,?)", (session['user'], score, now))
    conn.commit()
    conn.close()

    result_file = os.path.join(BASE_DIR, 'results.txt')
    with open(result_file, 'a') as f:
        f.write(f"{session['user']} - {score} at {now}\n")

    return jsonify({"status": "success"})

# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

# --- GOD-MODE APIs ---
@app.route('/admin/add_question', methods=['POST'])
def add_question():
    if not session.get('is_admin'): return jsonify({"error": "Unauthorized"}), 403
    try:
        data = request.get_json()
        with open(QUESTIONS_FILE, 'r', encoding='utf-8') as f:
            q_list = json.load(f)
        
        q_list.append({
            "question": data['question'],
            "options": data['options'],
            "answer": int(data['answer'])
        })
        
        with open(QUESTIONS_FILE, 'w', encoding='utf-8') as f:
            json.dump(q_list, f, indent=4)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/admin/delete_question', methods=['POST'])
def delete_question():
    if not session.get('is_admin'): return jsonify({"error": "Unauthorized"}), 403
    try:
        data = request.get_json()
        idx = int(data['index'])
        with open(QUESTIONS_FILE, 'r', encoding='utf-8') as f:
            q_list = json.load(f)
            
        if 0 <= idx < len(q_list):
            q_list.pop(idx)
            with open(QUESTIONS_FILE, 'w', encoding='utf-8') as f:
                json.dump(q_list, f, indent=4)
            return jsonify({"status": "success"})
        return jsonify({"error": "Invalid index"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- UNLOCKED ADMIN DASHBOARD ROUTE ---
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if request.method == 'POST':
        secret_key = request.form.get('admin_key', '').strip() 
        if secret_key == 'SumanAdmin':  
            session['is_admin'] = True
        else:
            return """
            <!DOCTYPE html>
            <html lang="en">
            <head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Access Denied</title><link rel="stylesheet" href="/static/style.css?v=11"></head>
            <body style="background: linear-gradient(-45deg, #2a0808, #1a0000, #3d0000);">
                <div class="main-card" style="border: 1px solid rgba(255, 65, 108, 0.5); box-shadow: 0 20px 50px rgba(0,0,0,0.8), inset 0 0 20px rgba(255, 65, 108, 0.2);">
                    <div style="font-size: 3.5rem; margin-bottom: 10px;">🚨</div>
                    <h2 class="epic-title" style="background: linear-gradient(90deg, #ff416c, #ff4b2b); -webkit-background-clip: text; text-shadow: 0 0 20px rgba(255, 65, 108, 0.5);">INVALID KEY</h2>
                    <p style="color: #cbd5e1; font-size: 1.1rem; font-weight: bold; margin-top: 15px;">Admin access denied.</p>
                    <div style="margin-top: 30px;"><a href="/dashboard" style="text-decoration: none;"><button class="btn-login" style="background: linear-gradient(90deg, #ff416c, #ff4b2b); box-shadow: 0 0 20px rgba(255, 65, 108, 0.5); color: #fff; font-weight: 900;">TRY AGAIN</button></a></div>
                </div>
            </body>
            </html>
            """
            
    if not session.get('is_admin'):
        admin_html = """
        <!DOCTYPE html>
        <html lang="en">
        <head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Admin Lock</title><link rel="stylesheet" href="/static/style.css?v=11"></head>
        <body>
            <div class="main-card">
                <div style="font-size: 3rem; margin-bottom: 10px;">🔒</div>
                <h2 class="epic-title" style="background: linear-gradient(90deg, #f59e0b, #fbbf24); -webkit-background-clip: text; text-shadow: 0 0 20px rgba(245, 158, 11, 0.4);">RESTRICTED AREA</h2>
                <form action="/dashboard" method="POST" class="login-form">
                    <div style="position: relative; margin: 10px 0;">
                        <input type="password" id="admin-pwd" name="admin_key" placeholder="Admin Password" required style="margin: 0; width: 100%; padding-right: 45px; border-color: #f59e0b; box-shadow: 0 0 10px rgba(245, 158, 11, 0.2); color: white; background: rgba(0,0,0,0.4);">
                        <span onclick="var x = document.getElementById('admin-pwd'); if(x.type==='password'){x.type='text'; this.innerText='🙈';}else{x.type='password'; this.innerText='👁️';}" style="position: absolute; right: 15px; top: 50%; transform: translateY(-50%); cursor: pointer; font-size: 1.2rem;" title="Show Password">👁️</span>
                    </div>
                    <button type="submit" class="btn-login" style="background: linear-gradient(90deg, #f59e0b, #fbbf24); box-shadow: 0 0 20px rgba(245, 158, 11, 0.4); color: #000;">UNLOCK LEADERBOARD</button>
                </form>
                <a href="/" style="display: block; margin-top: 20px; color: #64748b; text-decoration: none; font-weight: bold;">← Return to Login</a>
            </div>
        </body>
        </html>
        """
        return admin_html
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    current_user = session.get('user', 'ADMIN HQ')
    
    if current_user == 'ADMIN HQ':
        cursor.execute("SELECT score FROM scores")
    else:
        cursor.execute("SELECT score FROM scores WHERE username=?", (current_user,))
        
    scores_data = [r[0] for r in cursor.fetchall()]
    total_quizzes = len(scores_data)
    highest_score = max(scores_data) if scores_data else 0
    average_score = round(sum(scores_data)/total_quizzes, 2) if total_quizzes > 0 else 0
    
    cursor.execute("SELECT username, score, timestamp FROM scores ORDER BY score DESC LIMIT 10")
    leaderboard = cursor.fetchall()
    conn.close()

    # Load questions for the God-Mode Editor
    admin_questions = []
    try:
        with open(QUESTIONS_FILE, 'r', encoding='utf-8') as f:
            admin_questions = json.load(f)
    except:
        pass
    
    return render_template('dashboards.html', 
                           user=current_user,
                           total_quizzes=total_quizzes,
                           highest_score=highest_score,
                           average_score=average_score,
                           leaderboard=leaderboard,
                           questions=admin_questions)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

