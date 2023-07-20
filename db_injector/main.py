import psycopg2

# PostgreSQL connection parameters
host = "localhost"
port = "5432"  # Default PostgreSQL port
database = "postgres"
user = "postgres"
password = "mypassword"

# Create a connection to the PostgreSQL server
try:
    connection = psycopg2.connect(
        host=host, port=port, database=database, user=user, password=password
    )

    # Create a cursor to perform database operations
    cursor = connection.cursor()

    # Execute a sample query
    cursor.execute("SELECT version();")

    # Fetch and print the result
    db_version = cursor.fetchone()
    print(f"Connected to PostgreSQL server: {db_version[0]}")

    # Don't forget to close the cursor and connection
    cursor.close()
    connection.close()

except psycopg2.Error as e:
    print(f"Error connecting to PostgreSQL: {e}")
