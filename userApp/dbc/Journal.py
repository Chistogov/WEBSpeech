from userApp.dbc import db, NameRec


class Journal(db.Model):
    __tablename__ = "journal"
    id = db.Column(db.Integer, primary_key=True)
    record_name = db.Column(db.String(150))
    text = db.Column(db.Text)
    admin_text = db.Column(db.Text)
    recognizer = db.Column(db.String(50))
    date = db.Column(db.DATETIME)
    admin_name = db.Column(db.String(150))
    pacient_name = db.Column(db.String(150))
    new_call = db.Column(db.Boolean, default=False)

    name_rec = db.relationship('NameRec', back_populates='journal',
                               lazy='dynamic',
                               primaryjoin=id == NameRec.NameRec.journal_id)
