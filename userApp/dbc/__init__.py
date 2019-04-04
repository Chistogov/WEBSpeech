from flask_sqlalchemy import SQLAlchemy
from userApp import userApp


userApp.config.from_object('config')
db = SQLAlchemy(userApp)
db.create_all()


