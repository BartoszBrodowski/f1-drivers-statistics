import psycopg2
from f1scraper import F1StatsScraper
import os
from dotenv import load_dotenv

import time

load_dotenv()

db_params = {
    "host": os.getenv("POSTGRES_HOST"),
    "port": os.getenv("POSTGRES_PORT"),
    "database": os.getenv("POSTGRES_DB"),
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
}


class DbInjector:
    def __init__(self, db_params):
        self.connection = None
        self.cursor = None
        self.connect(db_params)

    def connect(self, db_params):
        try:
            self.connection = psycopg2.connect(**db_params)
            self.cursor = self.connection.cursor()
            self.cursor.execute("SELECT version();")
            db_version = self.cursor.fetchone()
            print(f"Connected to PostgreSQL server: {db_version[0]}")
        except psycopg2.Error as e:
            print(f"Error connecting to PostgreSQL: {e}")
            exit(1)

    def disconnect(self):
        if self.connection:
            self.cursor.close()
            self.connection.close()
            print("PostgreSQL connection is closed")

    def truncate_table(self, table_name):
        truncate_query = f"""
            TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE;
        """
        self.cursor.execute(truncate_query)
        self.connection.commit()

    def truncate_all_tables(self):
        truncate_query = """
            SELECT table_name FROM information_schema.tables WHERE table_schema = %s;
        """
        self.cursor.execute(truncate_query, ["public"])
        for table in self.cursor.fetchall():
            self.truncate_table(table[0])

        self.connection.commit()

    def create_drivers_table(self):
        create_drivers_table_query = """
            CREATE TABLE IF NOT EXISTS drivers (
                id SERIAL PRIMARY KEY,
                name VARCHAR(30) NOT NULL,
                nationality VARCHAR(3) NOT NULL
            );
        """
        self.cursor.execute(create_drivers_table_query)
        self.connection.commit()

    def insert_into_drivers_table(self, data):
        insert_query = """
            INSERT INTO drivers (name, nationality) VALUES (%s, %s);
        """
        self.cursor.executemany(insert_query, data)
        self.connection.commit()

    def print_drivers_table(self):
        print("Drivers table:")
        self.cursor.execute("SELECT * FROM drivers;")
        for row in self.cursor.fetchall():
            print(row)

    def create_races_table(self):
        create_races_table_query = """
            CREATE TABLE IF NOT EXISTS races (
                id SERIAL PRIMARY KEY,
                year INTEGER NOT NULL,
                name VARCHAR(30) NOT NULL
            );
        """
        self.cursor.execute(create_races_table_query)
        self.connection.commit()

    def insert_into_races_table(self, data):
        races = [(year, race) for year, races in data.items() for race in races]
        insert_query = """
            INSERT INTO races (year, name) VALUES (%s, %s);
        """
        self.cursor.executemany(insert_query, races)
        self.connection.commit()

    def print_races_table(self):
        print("Races table:")
        self.cursor.execute("SELECT * FROM races;")
        for row in self.cursor.fetchall():
            print(row)

    def create_results_table(self):
        create_results_table_query = """
            CREATE TABLE IF NOT EXISTS results (
                result_id SERIAL PRIMARY KEY,
                race_id INTEGER NOT NULL,
                race_position VARCHAR(2) NOT NULL,
                racing_number VARCHAR(2) NOT NULL,
                driver_id INTEGER NOT NULL,
                team VARCHAR(30) NOT NULL,
                laps INTEGER NOT NULL,
                time VARCHAR(11) NOT NULL,
                race_points VARCHAR(4) NOT NULL,
                FOREIGN KEY (race_id) REFERENCES races (id),
                FOREIGN KEY (driver_id) REFERENCES drivers (id)
            );
        """
        self.cursor.execute(create_results_table_query)
        self.connection.commit()

    def insert_into_results_table(self, data):
        # print(data)
        insert_query = """
            INSERT INTO results (race_id, race_position, racing_number, driver_id, team, laps, time, race_points) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
        """
        results = []

        for races in data.values():
            for race_name, race_results in races.items():
                for race_data in race_results:
                    race_result = race_data
                    # Edge case for when F1 data is faulty, meaning when driver has no laps completed,
                    # instead of data displaying 0 it displays an empty string
                    laps = race_result[4]
                    if laps == '':
                        race_result[4] = 0


                    driver_name = race_data[2]
                    get_driver_id_query = """SELECT id FROM drivers WHERE name = %s;"""
                    self.cursor.execute(get_driver_id_query, [driver_name])
                    driver_id = self.cursor.fetchone()
                    # If driver isn't listed on the F1 website, skip
                    # (This only happens with drivers that didnt get any points in their F1 career)
                    if driver_id is None:
                        continue

                    get_driver_id_query = """SELECT id FROM races WHERE name = %s;"""
                    self.cursor.execute(get_driver_id_query, [race_name])
                    race_id = self.cursor.fetchone()

                    # Delete driver name because we will use driver_id instead
                    race_result.pop(2)
                    # Insert race_id and driver_id in the correct positions
                    race_result.insert(0, race_id[0])
                    race_result.insert(3, driver_id[0])

                    results.append(race_result)

        self.cursor.executemany(insert_query, results)

    def print_results_table(self):
        print("Results table:")
        self.cursor.execute("SELECT * FROM results;")
        for row in self.cursor.fetchall():
            print(row)

    def create_drivers_championship_table(self):
        create_drivers_championship_table_query = """
            CREATE TABLE IF NOT EXISTS drivers_championships (
                id SERIAL PRIMARY KEY,
                year INTEGER NOT NULL,
                driver_id INTEGER NOT NULL,
                age INTEGER NOT NULL,
                points FLOAT NOT NULL,
                margin FLOAT,
                FOREIGN KEY (driver_id) REFERENCES drivers (id)
            );
        """
        self.cursor.execute(create_drivers_championship_table_query)
        self.connection.commit()

    def insert_into_drivers_championship_table(self, data):
        insert_query = """
            INSERT INTO drivers_championships (year, driver_id, age, points, margin) VALUES (%s, %s, %s, %s, %s);
        """
        drivers = []

        for driver in data:
            driver_data = driver
            driver_name = driver_data[1]
            get_driver_id_query = """SELECT id FROM drivers WHERE name = %s;"""
            self.cursor.execute(get_driver_id_query, [driver_name])
            driver_id = self.cursor.fetchone()
            # If driver isn't listed on the F1 website, skip
            # (This only happens with drivers that didnt get any points in their F1 career)
            if driver_id is None:
                continue

            # Delete driver name because we will use driver_id instead
            driver_data.pop(1)
            # Insert driver_id in the correct position
            driver_data.insert(1, driver_id[0])

            drivers.append(driver_data)
        self.cursor.executemany(insert_query, drivers)
        self.connection.commit()

    def print_drivers_championship_table(self):
        print("Drivers Championship table:")
        self.cursor.execute("SELECT * FROM drivers_championships;")
        for row in self.cursor.fetchall():
            print(row)

def main():
    dbinjector = DbInjector(db_params)
    scraper = F1StatsScraper()

    start = time.time()

    # dbinjector.truncate_table('results')
    # dbinjector.print_results_table()

    # results = scraper.get_all_race_results_by_range(1990, 1999)
    # print(results)
    # dbinjector.create_results_table()
    # dbinjector.insert_into_results_table(results)
    
    # print(results)

    # dbinjector.print_results_table()
    # constructor_championships = scraper.get_constructors_championship_stats_by_range(1950, 2020)
    # print(constructor_championships)

    end = time.time()
    print(end-start)


if __name__ == '__main__':
    main()