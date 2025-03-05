from flask import render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, db, login_manager
from app.models import User, News
from datetime import datetime, time
import json

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/")
def home():
    titles = read_from_db()
    codes = [title.get("id") for title in titles]
    return render_template("news_list.html", titles=titles, codes=codes)

@app.route("/save_click", methods=["POST"])
def save_click():
    data = request.json
    id = data.get("code")
    impressions = json.loads(data.get("impressions"))

    if id and current_user.is_authenticated:
        current_user.add_history(id)
        current_user.add_impressions(impressions)
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
            flash('Invalid username or password', category='error')

    return render_template('signin.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Passwords do not match', category='error')
        elif User.query.filter_by(username=username).first():
            flash('Username already exists', category='error')
        else:
            hashed_password = generate_password_hash(password)
            new_user = User(username=username, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            flash('Account created! Please log in.', category='info')
            return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/dashboard')
@login_required
def dashboard():
    histories = current_user.history.split(",") if current_user.history else []
    impressions = current_user.impressions.split(",") if current_user.impressions else []
    return render_template('dashboard.html', histories=histories, impressions=impressions)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

def read_from_db():
    # 오늘 아침 7시 이후 뉴스 가져오기
    # today = datetime.now().date()
    # morning_7am = datetime.combine(today, time(7, 0))
    # news = News.query.filter(News.date_time >= morning_7am).order_by(News.date_time.desc()).all()

    # 최신 뉴스 12개 가져오기
    news = News.query.order_by(News.date_time.desc()).limit(12).all()

    return [{
        'id': n.id,
        'category': n.category,
        'url': n.url,
        'title': n.title,
        'press': n.press,
        'author': n.author,
        'date_time': n.date_time,
        'image_url': n.image_url,
        'original_text': n.original_text,
        'summary': n.summary,
        'original_caption': n.original_caption,
        'generated_caption': n.generated_caption
    } for n in news]