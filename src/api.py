from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)


host = os.getenv("POSTGRES_HOST")
port = os.getenv("POSTGRES_PORT")
database = os.getenv("POSTGRES_DB")
user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")

db_uri = f"postgresql://{user}:{password}@{host}:{port}/{database}"
app.config["SQLALCHEMY_DATABASE_URI"] = db_uri

db = SQLAlchemy()
db.init_app(app)


# To import form dbinjector.py:
class Drivers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    nationality = db.Column(db.String(3), nullable=False)


@app.route("/drivers")
def get_drivers():
    # drivers = db.session.query(Drivers).all()
    drivers = db.session.scalars(db.select(Drivers)).all()

    result = [
        {"id": driver.id, "name": driver.name, "nationality": driver.nationality}
        for driver in drivers
    ]

    return jsonify(result)


@app.route("/drivers/top/nationalities")
def get_top_nationalities():
    nationality_counts = (
        db.session.execute(
            db.select(
                db.Bundle(
                    "driver",
                    Drivers.nationality,
                    db.func.count(Drivers.nationality).label("amount_of_drivers"),
                )
            )
            .group_by(Drivers.nationality)
            .order_by(db.desc("amount_of_drivers"))
        )
        .scalars()
        .all()
    )

    result = [
        {"nationality": result[0], "count": result[1]} for result in nationality_counts
    ]

    return result
