import psycopg2

db_params = {
    "host": "localhost",
    "port": "5432",
    "database": "postgres",
    "user": "postgres",
    "password": "mypassword",
}

try:
    connection = psycopg2.connect(**db_params)

    cursor = connection.cursor()

    cursor.execute("SELECT version();")
    db_version = cursor.fetchone()
    print(f"Connected to PostgreSQL server: {db_version[0]}")

    truncate_table = """
        TRUNCATE TABLE drivers RESTART IDENTITY;
    """
    cursor.execute(truncate_table)

    create_drivers_table = """
    CREATE TABLE IF NOT EXISTS drivers (
        id SERIAL PRIMARY KEY,
        name VARCHAR(30) NOT NULL,
        nationality VARCHAR(3) NOT NULL
    );
    """
    cursor.execute(create_drivers_table)

    driver_data = [
        ("Max Verstappen", "NED"),
        ("Lewis Hamilton", "GBR"),
        ("Valtteri Bottas", "FIN"),
    ]

    insert_query = """INSERT INTO drivers (name, nationality) VALUES (%s, %s);"""

    cursor.executemany(insert_query, driver_data)

    connection.commit()

    select_data_query = "SELECT * FROM drivers;"
    cursor.execute(select_data_query)
    inserted_data = cursor.fetchall()

    print("Contents of 'drivers':")
    for row in inserted_data:
        print(f"ID: {row[0]}, name: {row[1]}, nationality: {row[2]}")

    cursor.close()
    connection.close()

except psycopg2.Error as e:
    print(f"Error connecting to PostgreSQL: {e}")
