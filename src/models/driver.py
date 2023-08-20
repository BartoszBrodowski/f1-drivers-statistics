from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class Driver(db.Model):
    __tablename__ = "drivers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    nationality = db.Column(db.String(3), nullable=False)