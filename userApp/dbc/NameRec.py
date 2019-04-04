from flask_login import UserMixin
from userApp.dbc import db


class NameRec(db.Model, UserMixin):
    __tablename__ = "namerec"
    id = db.Column(db.Integer, primary_key=True)
    name_id = db.Column(db.Integer, db.ForeignKey('names.id'), nullable=False)
    journal_id = db.Column(db.Integer, db.ForeignKey('journal.id'), nullable=False)
    pacient = db.Column(db.Boolean, default=True)

    journal = db.relationship("Journal", back_populates="name_rec")

    names_ = db.relationship("Names", back_populates="name_rec")
