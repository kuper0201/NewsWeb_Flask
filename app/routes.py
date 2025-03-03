import csv
from flask import render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, db, login_manager
from app.models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/")
def home():
    titles = read_tsv()
    return render_template("news_list.html", titles=titles)

@app.route("/save_click", methods=["POST"])
def save_click():
    data = request.json
    code = data.get("code")

    if code and current_user.is_authenticated:
        current_user.add_history(code)
        return jsonify({"message": "Click saved!", "history": current_user.history}), 200

    return jsonify({"message": "Invalid request"}), 400

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']
    confirm_password = request.form['confirm_password']

    if password != confirm_password:
        flash('Passwords do not match')
    elif User.query.filter_by(username=username).first():
        flash('Username already exists')
    else:
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Account created! Please log in.')
        return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    histories = current_user.history.split(",") if current_user.history else []
    return render_template('dashboard.html', histories=histories)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

def read_tsv(file_path='datasets/news.tsv'):
    with open(file_path, "r", encoding="utf-8") as file:
        reader = csv.reader(file, delimiter="\t")
        contents = [{"title": row[3], "code": row[0], "url": row[5]} for row in reader]
        return contents[:12] if len(contents) >= 12 else contents