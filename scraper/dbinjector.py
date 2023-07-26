import psycopg2
from f1scraper import F1StatsScraper

db_params = {
    "host": "localhost",
    "port": "5432",
    "database": "postgres",
    "user": "postgres",
    "password": "mypassword",
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

    def close_connection(self):
        self.cursor.close()
        self.connection.close()

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
                race_points INTEGER NOT NULL,
                FOREIGN KEY (race_id) REFERENCES races (id),
                FOREIGN KEY (driver_id) REFERENCES drivers (id)
            );
        """
        self.cursor.execute(create_results_table_query)
        self.connection.commit()

    def insert_into_results_table(self, data):
        results = []
        insert_query = """
            INSERT INTO results (race_id, race_position, racing_number, driver_id, team, laps, time, race_points) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);"""
        for year, races in data.items():
            for race_name, race_results in races.items():
                for result in race_results:
                    result_formatted = result
                    get_driver_id_query = """SELECT id FROM drivers WHERE name = %s;"""
                    self.cursor.execute(get_driver_id_query, [result[2]])
                    driver_id = self.cursor.fetchone()
                    get_driver_id_query = """SELECT id FROM races WHERE name = %s;"""
                    self.cursor.execute(get_driver_id_query, [race_name])
                    race_id = self.cursor.fetchone()
                    result_formatted.pop(2)
                    result_formatted.insert(0, race_id[0])
                    result_formatted.insert(3, driver_id[0])
                    results.append(result_formatted)
        # print(results)
        self.cursor.executemany(insert_query, results)


def main():
    injector = DbInjector(db_params)
    f1scraper = F1StatsScraper()

    injector.truncate_table("results")

    # driver_data = f1scraper.get_drivers_by_range(2022, 2023)
    # races = f1scraper.get_races_by_range(2022, 2023)
    races_data = f1scraper.get_all_race_results_by_range(2022, 2023)

    # injector.create_drivers_table()
    # injector.create_races_table()
    injector.create_results_table()

    # injector.insert_into_drivers_table(driver_data)
    # injector.insert_into_races_table(races)
    injector.insert_into_results_table(races_data)

    cursor = injector.cursor
    select_query = """SELECT * FROM results;"""
    cursor.execute(select_query)
    inserted_data = cursor.fetchall()

    print("Contents of 'results':")
    for row in inserted_data:
        print(
            f"result_id: {row[0]}, position: {row[1]}, racing_number: {row[2]}, driver_id: {row[3]}, team: {row[4]}, laps: {row[5]}, time: {row[6]} points: {row[7]}"
        )


if __name__ == "__main__":
    main()
