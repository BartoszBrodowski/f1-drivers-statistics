## I am a big F1 fan and one day I was wondering :racing_car:

What would a statistic on the drivers nationality like, how many drivers come from Germany or what is the average age of Champions. This led to creation of this project which is a F1 Statistics Database.

I had to somehow get access to data, however there was no popular and well working API, so I decided to get the data myself. 

At the start I wanted to only scrape data from official Formula1 website. Most of the data is scraped from there, however finishing this project I saw that Wikipedia has more in-depth data and decided to add scraping this website as well.

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
The concept was to scrape the data mainly from the official Formula1 website as this should be the best place to get legit F1 data. Finishing the project I realised there is some better in-depth info on Wikipedia comparing to Formula1.com as for example drivers that finished seasons with no points. I didn't include these drivers in the first years of F1 as there was too many and they didn't have much historic impact. I've added some from the recent years

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
