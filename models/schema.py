from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask import Blueprint

core_models = Blueprint('core_models', __name__)
db = SQLAlchemy()

class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    due_date = db.Column(db.DateTime, nullable=False)
    user_phone = db.Column(db.String(15), nullable=False)
    notification_sent = db.Column(db.Boolean, default=False) 

    def __repr__(self):
        return f"<Task {self.title}>"

