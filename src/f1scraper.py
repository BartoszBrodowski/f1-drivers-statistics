from bs4 import BeautifulSoup
import requests
from unidecode import unidecode
from datetime import date
import re

# Create a session to reuse the TCP connection (much better performance)
session = requests.Session()

CURRENT_YEAR = date.today().year


def get_soup(link):
    page = session.get(link)
    page.raise_for_status()
    soup = BeautifulSoup(page.content, "lxml")
    return soup

def get_filtered_text(text):
    return text.get_text().replace("\n", " ").strip()

def filter_row_no_limiters(row):
    return row.find_all("td", class_=lambda value: value is None or "limiter" not in value.split())

def get_link_by_season(season, link):
    return get_soup(link.format(season))

def get_table_rows_without_header(soup):
    return soup.find_all("tr")[1:]


class F1StatsScraper:
    # Drivers

    def get_drivers_by_season(self, season=CURRENT_YEAR):
        link = f"https://www.formula1.com/en/results.html/{season}/drivers.html"
        soup = get_soup(link)
        table_rows = get_table_rows_without_header(soup)

        def get_name(driver):
            name_parts = driver.find("a").get_text().strip().splitlines()[:-1]
            return " ".join(name_parts)
        
        def get_nationality(driver):
            return driver.find("td", class_="dark semi-bold uppercase").get_text()

        drivers = [
            (get_name(driver), get_nationality(driver))
            for driver in table_rows
        ]

        return drivers

    def get_drivers_by_range(self, start_season, end_season):
        def get_name(driver):
            name_parts = driver.find("a").get_text().strip().splitlines()[:-1]
            return " ".join(name_parts)

        def get_nationality(driver):
            return driver.find("td", class_="dark semi-bold uppercase").get_text()
        
        drivers = {
            (get_name(driver), get_nationality(driver))
            for season in range(start_season, end_season + 1)
            for driver in get_table_rows_without_header(get_soup(f"https://www.formula1.com/en/results.html/{season}/drivers.html"))
        }

        return drivers

    # Races

    def get_races_by_season(self, season=CURRENT_YEAR):
        races = []
        link = f"https://www.formula1.com/en/results.html/{season}/races.html"
        soup = get_soup(link)
        table_rows = get_table_rows_without_header(soup)
        for race in table_rows:
            name = race.find("td", class_="dark bold").get_text().strip()
            races.append(name)
        return races

    def get_races_by_range(self, start_season, end_season):
        def get_race_name(race):
            return get_filtered_text(race.find("td", class_='dark bold'))
        
        link = "https://www.formula1.com/en/results.html/{}/races.html"

        return {
            season: [
                get_race_name(race)
                for race in get_table_rows_without_header(get_link_by_season(season, link))
            ]
            for season in range(start_season, end_season + 1)
        }

    # Links

    def get_all_championship_links(self):
        championship_links = {}
        for season in range(1950, CURRENT_YEAR + 1):
            championship_links[
                season
            ] = f"https://www.formula1.com/en/results.html/{season}/championship.html"

        return championship_links

    def get_race_link(self, season, race):
        link = f"https://www.formula1.com/en/results.html/{season}/races.html"
        soup = get_soup(link)

        def text_contains_whitespace_insensitive(element, target_text):
            return element.name == 'a' and element.get_text().strip() == target_text.strip()

        element = soup.find(lambda tag: text_contains_whitespace_insensitive(tag, race))
        if element is None:
            return None
        
        tag_link = element['href']
        race_link = f'https://formula1.com{tag_link}'

        return race_link

    def get_all_race_links_by_season(self, season):
        link = f"https://www.formula1.com/en/results.html/{season}/races.html"
        soup = get_soup(link)
        grand_prix_anchor_tags = soup.select("td > a")

        grand_prix_links = {
            get_filtered_text(tag): f"https://www.formula1.com{tag.get('href')}" for tag in grand_prix_anchor_tags
        }

        return grand_prix_links

    def get_one_races_links_every_season(self, race):
        race_links = {season: race_link for season in range(1950, CURRENT_YEAR + 1) if (race_link := self.get_race_link(season, race))}

        return race_links

    def get_driver_links_by_season(self, season):
        def get_driver_tag(driver):
            driver_name = unidecode(driver[0].replace(" ", "-").lower())
            # Get the first part of the driver tag
            tag_1st_part = driver[0][:3].upper()
            # Get second part of URL tag (e.g. LEWHAM01 for Lewis Hamilton)
            tag_2nd_part = "".join(driver[0].replace("'", "").split()[1:])[:3].upper()
            # 3rd part of URL driver tag is always 01
            tag = tag_1st_part + tag_2nd_part + "01"

            return driver_name, tag

        link = "https://www.formula1.com/en/results.html/{}/drivers/{}/{}.html" 
        drivers = self.get_drivers_by_season(season)

        links = [
            link.format(season, tag, driver_name)
            for driver in drivers 
            for driver_name, tag in [get_driver_tag(driver)]
        ]

        return links

    # Race results

    def get_all_race_results_by_range(self, start_season, end_season):
        def delete_driver_tag(name):
            return name[:-4]
        seasons = {}

        for season in range(start_season, end_season + 1):
            race_links = self.get_all_race_links_by_season(season)
            seasons[season] = {
                race: [
                    [
                        # Delete last 4 characters (tag) if the element is the drivers name
                        delete_driver_tag(get_filtered_text(elem)) if i == 3 else get_filtered_text(elem)
                        for i, elem in enumerate(filter_row_no_limiters(row))
                    ]
                    for row in filtered_rows
                ]
                for race, link in race_links.items()
                if (soup := get_soup(link))
                and (filtered_rows := [row for row in get_table_rows_without_header(soup)])
            }
        return seasons

    # Championship stats

    def get_drivers_championship_stats(self, season=CURRENT_YEAR):
        link = f"https://www.formula1.com/en/results.html/{season}/drivers.html"
        soup = get_soup(link)

        driver_table_rows = get_table_rows_without_header(soup)

        drivers_stats = [
            [get_filtered_text(stat) for stat in filter_row_no_limiters(row)]
            for row in driver_table_rows
        ]

        return drivers_stats

    def get_drivers_championship_stats_by_range(self, start_season, end_season):
        link = "https://www.formula1.com/en/results.html/{}/drivers.html"
        return {
            season: [
                [get_filtered_text(stat) for stat in filter_row_no_limiters(row)]
                for row in get_table_rows_without_header(get_link_by_season(season, link))
            ]
            for season in range(start_season, end_season + 1)
        }

    def get_constructors_championship_stats(self, season=CURRENT_YEAR):
        link = f"https://www.formula1.com/en/results.html/{season}/team.html"
        soup = get_soup(link)
        driver_table_rows = get_table_rows_without_header(soup)

        driver_stats = [
            [get_filtered_text(stat) for stat in filter_row_no_limiters(row)]
            for row in driver_table_rows
        ]

        return driver_stats

    def get_constructors_championship_stats_by_range(self, start_season, end_season):
        link = "https://www.formula1.com/en/results.html/{}/team.html"

        return {
            season: [
                [get_filtered_text(stat) for stat in filter_row_no_limiters(row)] for row in get_table_rows_without_header(get_link_by_season(season, link))]
            for season in range(start_season, end_season + 1)
        }

    # Champions

    def get_drivers_world_champion(self, season=CURRENT_YEAR - 1):
        link = "https://en.wikipedia.org/wiki/{}_Formula_One_World_Championship"
        link = get_link_by_season(season, link)
        soup = get_soup(link)
        champion = (
            soup.find(class_="motorsport-season-nav-subheader")
            .select("a")[1]
            .get_text()
        )

        return champion

    def get_constructors_world_champion(self, season=CURRENT_YEAR - 1):
        link = (
            f"https://en.wikipedia.org/wiki/{season}_Formula_One_World_Championship"
        )
        soup = get_soup(link)
        champion = (
            soup.find(class_="motorsport-season-nav-subheader")
            .select("a")[3]
            .get_text()
        )

        return champion

def main():
    scraper = F1StatsScraper()

    test = scraper.get_drivers_by_range(2016,2023)
    print(test)

    session.close()


if __name__ == "__main__":
    main()
