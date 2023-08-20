from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class Race(db.Model):
    __tablename__ = "races"

    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(30), nullable=False)