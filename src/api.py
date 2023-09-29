from flask import jsonify, request
from models.driver import Driver
from models.drivers_championship import DriversChampionship

from app import db, app

@app.route("/test")
def test():
    return 'Hello world'

@app.route("/drivers")
def get_drivers():
    try:
        drivers = db.session.query(Driver).all()

        if not drivers:
            return jsonify({"error": "Resource not found"}), 404

        result = [
            {"id": driver.id, "name": driver.name, "nationality": driver.nationality}
            for driver in drivers
        ]

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": "Database connection error"}), 500

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

@app.route('/drivers/championships/winners/amount')
def get_most_titles_amount():

    subquery = db.session.query(DriversChampionship.driver_id, db.func.count(DriversChampionship.id).label('titles')).group_by(DriversChampionship.driver_id).subquery()
    query = db.session.query(subquery.c.titles, db.func.count(subquery.c.driver_id).label('drivers_amount')).group_by(subquery.c.titles).order_by(subquery.c.titles.desc())

    results = query.all()

    formatted_results = [
        {
            "titles": result.titles,
            "drivers_amount": result.drivers_amount
        }
        for result in results
    ]

    return formatted_results
    
@app.route('/drivers/championships/most_titles')
def get_most_titles():
    query = db.session.query(
        Driver.name.label('name'),
        db.func.count(DriversChampionship.id).label('title_count'),
        db.func.count(Driver.nationality).label("amount_of_drivers"),
    ).join(
        DriversChampionship, DriversChampionship.driver_id == Driver.id
    ).group_by(
        Driver.name
    ).order_by(
        db.desc('title_count')
    )

    results = query.all()

    formatted_results = [
        {
            "name": result.name,
            "title_count": result.title_count
        }
        for result in results
    ]

    return formatted_results