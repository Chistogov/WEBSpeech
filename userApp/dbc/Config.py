from flask_login import UserMixin
from userApp.dbc import db


class Config(db.Model, UserMixin):
    __tablename__ = "config"
    id = db.Column(db.Integer, primary_key=True)
    delta_rec = db.Column(db.Integer)
    config_name = db.Column(db.String(50), unique=True)
    cleanerTimeout = db.Column(db.Integer)
    new_calls = db.Column(db.Boolean)
    repeat_calls = db.Column(db.Boolean)
    pacient_voice = db.Column(db.Boolean)
    admin_voice = db.Column(db.Boolean)
    task_call = db.Column(db.Boolean)
    input_call = db.Column(db.Boolean)
    output_call = db.Column(db.Boolean)
    internal_call = db.Column(db.Boolean)
    status = db.Column(db.String(150))
    google = db.Column(db.Boolean)
    yandex = db.Column(db.Boolean)
