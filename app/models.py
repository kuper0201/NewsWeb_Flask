from app import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)
    history = db.Column(db.String(15), nullable=True)
    impressions = db.Column(db.String(15), nullable=True)

    def add_history(self, code):
        if self.history:
            history_list = self.history.split(",")
            if code not in history_list:
                history_list.append(code)
        else:
            history_list = [code]
        self.history = ",".join(history_list)
        db.session.commit()