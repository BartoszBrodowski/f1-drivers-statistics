## F1 Scraper + PostgreSQL Database

This project is a scraper for the Formula 1 website. It scrapes the data from the website and stores it in a PostgreSQL database.

## Docker

Before running the container you should setup the credentials for PostgreSQL Database.
I used these namings for the variables:

```
POSTGRES_HOST
POSTGRES_PORT
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD
```

To run the container you can use this command:

```bash
docker compose --env-file ./{path_to_file} up
```
