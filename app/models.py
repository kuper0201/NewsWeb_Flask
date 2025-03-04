from app import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)
    history = db.Column(db.String, nullable=True)
    impressions = db.Column(db.String, nullable=True)

    def add_history(self, code):
        if self.history:
            history_list = self.history.split(",")
            if code not in history_list:
                history_list.append(code)
        else:
            history_list = [code]
        self.history = ",".join(history_list)
        db.session.commit()

    def add_impressions(self, impressions):
        histories = self.history.split(",") if self.history else []

        imp_list = []
        for item in impressions:
            if str(item) in histories:
                imp_list.append(f'{item}_1')
            else:
                imp_list.append(f'{item}_0')
        self.impressions = ",".join(imp_list)
        db.session.commit()

class News(db.Model):
    __tablename__ = 'news'
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String)
    url = db.Column(db.String)
    title = db.Column(db.String)
    press = db.Column(db.String)
    author = db.Column(db.String)
    date_time = db.Column(db.DateTime)
    image_url = db.Column(db.String)
    original_text = db.Column(db.String)
    summary = db.Column(db.String)
    original_caption = db.Column(db.String)
    generated_caption = db.Column(db.String)