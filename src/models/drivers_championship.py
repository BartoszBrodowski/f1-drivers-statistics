from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class DriversChampionship(db.Model):
    __tablename__ = "drivers_championships"

    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey('driver.id'))
    age = db.Column(db.Integer, nullable=False)
    points = db.Column(db.Float(3), nullable=False)
    margin = db.Column(db.Float(3), nullable=False)