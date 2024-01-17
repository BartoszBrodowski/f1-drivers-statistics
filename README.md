## I am a big F1 fan and one day I was wondering :racing_car:

What started as a curiosity about statistics on drivers' nationalities, such as the number of drivers from Germany or the average age of champions, evolved into the creation of a this project.

I had to somehow get access to the data, however there was no popular and well working API, so I decided to get the data myself. 

In the beggining I wanted to only scrape data from official Formula1 website. While I successfully gathered most of the information I wanted from there, the completion of the project led me to discover that Wikipedia contained more in-depth data on some of the topics like drivers in a particular seasons.

## Technologies :hammer_and_wrench:
- Python
- BeautifulSoup (scraping)
- Flask
- PostgreSQL
- Docker (database)

## Code design :desktop_computer:

My idea for creating the project was to have 3 main parts:
- Scraper
- Injector
- API

### Scraper:
Scraper was a way to conviniently insert data to DB using Python scripting. I wanted to challenge myself to create very clean and pythonic code at the same time. A lot of the code was written in a Pythonic manner ex. List Comprehensions, with few exceptions made due to code readability.

### Injector: 
I wanted to write the Injector database as a convinient way to put your data inside the database, to challenge myself if I can handle it while maintaining clean OOP code. There is some comments left for the ease of understanding, as some of the steps are just for the sake of cleaning the data of "edge cases", which otherwise created problems in the results.

### API:
If I had everything done in Python, I might as well create an API in Flask. So I did! It is a small API that uses SQLAlchemy for PostgreSQL querying (I wanted to learn SQLAlchemy which came out to be much harder than I thought, but in the end it works!). Models and API config are separated into different files for code readability. The API also uses Redis database for Limiter storage and it benefits from caching.

## Docker :whale:

I used Docker for my convenience of use (to not host online database).

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

## Thank you for checking out this project. I hope you enjoy what you see!
