import psycopg2

db_params = {
    "host": "localhost",
    "port": "5432",
    "database": "postgres",
    "user": "postgres",
    "password": "mypassword",
}


class DbInjector:
    def __init__(self, db_params):
        self.db_params = db_params
        self.connection = None
        self.cursor = None

    def connect(self):
        try:
            self.connection = psycopg2.connect(**db_params)
            self.cursor = self.connection.cursor()
            self.cursor.execute("SELECT version();")
            db_version = self.cursor.fetchone()
            print(f"Connected to PostgreSQL server: {db_version[0]}")
        except psycopg2.Error as e:
            print(f"Error connecting to PostgreSQL: {e}")

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


def main():
    injector = DbInjector(db_params)
    injector.connect()

    cursor = injector.cursor

    truncate_table = """
        TRUNCATE TABLE drivers RESTART IDENTITY;
    """
    cursor.execute(truncate_table)

    injector.create_drivers_table()

    driver_data = [
        ("Max Verstappen", "NED"),
        ("Lewis Hamilton", "GBR"),
        ("Valtteri Bottas", "FIN"),
    ]

    injector.insert_into_drivers_table(driver_data)

    select_query = """SELECT * FROM drivers;"""
    cursor.execute(select_query)
    inserted_data = cursor.fetchall()

    print("Contents of 'drivers':")
    for row in inserted_data:
        print(f"ID: {row[0]}, name: {row[1]}, nationality: {row[2]}")


if __name__ == "__main__":
    main()
