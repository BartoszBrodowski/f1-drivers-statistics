from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from models.driver import Driver
from models.drivers_championship import DriversChampionship
import os

from app import db, app

@app.route("/test")
def test():
    return 'Hello world'

@app.route("/drivers")
def get_drivers():
    drivers = db.session.scalars(db.select(Driver)).all()

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
                    Driver.nationality,
                    db.func.count(Driver.nationality).label("amount_of_drivers"),
                )
            )
            .group_by(Driver.nationality)
            .order_by(db.desc("amount_of_drivers"))
        )
        .scalars()
        .all()
    )

    result = [
        {"nationality": result[0], "count": result[1]} for result in nationality_counts
    ]

    return result

@app.route('/drivers/championships')
def get_constructor_championships():
    query = db.session.query(
        DriversChampionship.year,
        Driver.name.label('name'),
        DriversChampionship.age,
        DriversChampionship.points,
        DriversChampionship.margin
    ).join(
        Driver, DriversChampionship.driver_id == Driver.id
    )

    results = query.all()

    formatted_results = [
        {
            "year": result.year,
            "name": result.name,
            "age": result.age,
            "points": result.points,
            "margin": result.margin
        }
        for result in results
    ]

    return formatted_results

@app.route('/drivers/championships/average_age')
def get_age_categories():
    age_categories = [
        {"category": "20-25", "min_age": 20, "max_age": 25},
        {"category": "25-30", "min_age": 25, "max_age": 30},
        {"category": "30-35", "min_age": 30, "max_age": 35},
        {"category": "35-40", "min_age": 35, "max_age": 40},
        {"category": "45-50", "min_age": 45, "max_age": 50}
    ]

    age_category_counts = {category["category"]: 0 for category in age_categories}

    for category in age_categories:
        min_age = category["min_age"]
        max_age = category["max_age"]

        query = db.session.query(
            db.func.count().label('driver_count')
        ).filter(
            DriversChampionship.age >= min_age,
            DriversChampionship.age <= max_age
        )

        result = query.one()
        age_category_counts[category["category"]] = result.driver_count

    age_category_results = [
        {"category": category, "count": age_category_counts[category]}
        for category in age_category_counts
    ]

    return age_category_results