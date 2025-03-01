import csv
from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'this_is_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)
    # time = db.Column(db.DateTime, nullable=False)
    
    history = db.Column(db.String(15), nullable=True)
    impressions = db.Column(db.String(15), nullable=True)

    def add_history(self, code):
        """ 클릭한 코드값을 history 컬럼에 추가 """
        if self.history:
            history_list = self.history.split(",")  # 기존 코드값 불러오기
            if code not in history_list:  # 중복 방지
                history_list.append(code)
        else:
            history_list = [code]
        self.history = ",".join(history_list)  # 다시 문자열로 변환
        db.session.commit()

def read_tsv(file_path='datasets/news.tsv'):
    with open(file_path, "r", encoding="utf-8") as file:
        # TimeStamp 기준 정렬하여 데이터 읽는 부분 추가 필요
        reader = csv.reader(file, delimiter="\t")
        contents = [{"title": row[3], "code": row[0], "url": row[5]} for row in reader]
        if len(contents) < 12:
            return contents
        else:
            return contents[:12]

@app.route("/")
def home():
    titles = read_tsv()
    return render_template("news_list.html", titles=titles)

@app.route("/save_click", methods=["POST"])
def save_click():
    data = request.json
    code = data.get("code")

    if code and current_user.is_authenticated:
        current_user.add_history(code)  # 코드값 저장
        return jsonify({"message": "Click saved!", "history": current_user.history}), 200

    return jsonify({"message": "Invalid request"}), 400

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user:
            if check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for('home'))
            else:
                flash('Incorrect password. Please try again.')
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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
