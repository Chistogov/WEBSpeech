from userApp.dbc import db, NameRec


class Names(db.Model):
    __tablename__ = "names"
    id = db.Column(db.Integer, primary_key=True)
    surname = db.Column(db.String(50))
    name = db.Column(db.String(50))
    middle_name = db.Column(db.String(50))
    short_surname = db.Column(db.String(50))
    short_name = db.Column(db.String(50))
    short_middle_name = db.Column(db.String(50))

    name_rec = db.relationship('NameRec', back_populates='names_',
                               lazy='dynamic',
                               primaryjoin=id == NameRec.NameRec.name_id)