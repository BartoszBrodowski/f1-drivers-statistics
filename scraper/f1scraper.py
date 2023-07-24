from bs4 import BeautifulSoup
import requests
from unidecode import unidecode
from datetime import date
import re

# Create a session to reuse the TCP connection (much better performance)
session = requests.Session()

CURRENT_YEAR = date.today().year


def get_soup(website):
    page = session.get(website)
    page.raise_for_status()
    soup = BeautifulSoup(page.content, "lxml")
    return soup


class F1StatsScraper:
    def get_drivers_by_season(self, season):
        drivers = []
        website = f"https://www.formula1.com/en/results.html/{season}/drivers.html"
        soup = get_soup(website)
        for driver in soup.find_all("tr")[1:]:
            nationality = driver.find(
                "td", class_="dark semi-bold uppercase"
            ).get_text()
            # Transforming name to not contain a name tag
            name_array_without_tag = (
                driver.find("a").get_text().strip().splitlines()[:-1]
            )
            name_transformed = " ".join(name_array_without_tag)
            drivers.append((name_transformed, nationality))
        return drivers

    def get_drivers_by_range(self, start_season, end_season):
        drivers = set()
        for season in range(start_season, end_season + 1):
            website = f"https://www.formula1.com/en/results.html/{season}/drivers.html"
            soup = get_soup(website)
            for driver in soup.find_all("tr")[1:]:
                nationality = driver.find(
                    "td", class_="dark semi-bold uppercase"
                ).get_text()
                # Transforming name to not contain a name tag
                name_array_without_tag = (
                    driver.find("a").get_text().strip().splitlines()[:-1]
                )
                name_transformed = " ".join(name_array_without_tag)
                drivers.add((name_transformed, nationality))
        return drivers

    def get_all_championship_links(self):
        championship_links = {}
        for season in range(1950, CURRENT_YEAR + 1):
            championship_links[
                season
            ] = f"https://www.formula1.com/en/results.html/{season}/championship.html"
        return championship_links

    def get_race_link(self, season, race):
        website = f"https://www.formula1.com/en/results.html/{season}/races.html"
        soup = get_soup(website)
        race_tag = soup.find(lambda tag: tag.name == "a" and race in tag.text)
        if race_tag is not None:
            link = race_tag.get("href")
            return "https://www.formula1.com" + link
        return None

    def get_all_race_links_by_season(self, season):
        grand_prix_links = {}
        website = f"https://www.formula1.com/en/results.html/{season}/races.html"
        soup = get_soup(website)
        grand_prix_list = soup.select("td > a")
        for grand_prix in grand_prix_list:
            grand_prix_name = grand_prix.get_text().strip()
            grand_prix_href = grand_prix.get("href")
            link = "https://www.formula1.com" + grand_prix_href
            grand_prix_links[grand_prix_name] = link

        return grand_prix_links

    def get_race_links_every_season(self, race):
        race_links = {}
        for season in range(1950, CURRENT_YEAR + 1):
            race_link = self.get_race_results_link(season, race)
            if race_link is not None:
                race_links[season] = race_link

        return race_links

    def get_driver_links_by_season(self, season):
        websites = []
        drivers = self.get_drivers_by_season(season)
        for driver in drivers:
            driver_name = unidecode(driver.replace(" ", "-").lower())
            tag_1st_part = driver[:3].upper()
            # Get second part of URL driver tag (e.g. LEWHAM01 for Lewis Hamilton)
            tag_2nd_part = "".join(driver.replace("'", "").split()[1:])[:3].upper()
            # 3rd part of URL driver tag is always 01
            tag = tag_1st_part + tag_2nd_part + "01"
            website = f"https://www.formula1.com/en/results.html/{season}/drivers/{tag}/{driver_name}.html"
            websites.append(website)

        return websites

    def get_all_race_results_by_range(self, start_season, end_season):
        seasons = {}
        for season in range(start_season, end_season + 1):
            seasons[season] = {}
            race_links = self.get_all_race_links_by_season(season)

            # Add race names
            for race in race_links:
                seasons[season][race] = []

            # Add driver names, positions and points
            for race, link in race_links.items():
                soup = get_soup(link)
                table_rows = soup.select("tr")[1:]
                filtered_rows = [row for row in table_rows]

                for row in filtered_rows:
                    row_text = [
                        elem.text.replace("\n", " ")[:-5]
                        if i == 3
                        else elem.text.replace("\n", " ")
                        for i, elem in enumerate(row.find_all(["td"]))
                        if "limiter" not in elem.get("class")
                    ]
                    seasons[season][race].append(row_text)

        return seasons

    def get_column_names(self):
        website = "https://www.formula1.com/en/results.html/2023/drivers.html"
        soup = get_soup(website)
        column_name_change_map = {
            "Car": "Team",
            "PTS": "Points",
            "Pos": "Position",
        }

        column_names = [
            column_name_change_map.get(name.get_text(), name.get_text())
            for name in soup.find_all("th")
            if name.get_text() != ""
        ]

        return column_names

    # Championship stats

    def get_drivers_championship_stats(self, season=CURRENT_YEAR - 1):
        drivers_stats = []
        website = f"https://www.formula1.com/en/results.html/{season}/drivers.html"
        soup = get_soup(website)

        driver_table_rows = soup.find_all("tr")[1:]

        drivers_stats = [
            [
                stat.get_text().replace("\n", " ").strip()
                for stat in row.find_all(
                    "td",
                    class_=lambda value: value is None
                    or "limiter" not in value.split(),
                )
            ]
            for row in driver_table_rows
        ]

        return drivers_stats

    def get_drivers_championship_stats_by_range(self, start_season, end_season):
        drivers_stats = {}

        for season in range(start_season, end_season + 1):
            website = f"https://www.formula1.com/en/results.html/{season}/drivers.html"
            soup = get_soup(website)

            driver_table_rows = soup.find_all("tr")[1:]

            driver_stats = [
                [
                    stat.get_text().replace("\n", " ").strip()
                    for stat in row.find_all(
                        "td",
                        class_=lambda value: value is None
                        or "limiter" not in value.split(),
                    )
                ]
                for row in driver_table_rows
            ]

            drivers_stats[season] = driver_stats

        return drivers_stats

    def get_constructors_championship_stats(self, season=CURRENT_YEAR - 1):
        website = f"https://www.formula1.com/en/results.html/{season}/team.html"
        soup = get_soup(website)

        driver_table_rows = soup.find_all("tr")[1:]

        driver_stats = [
            [
                stat.get_text().replace("\n", " ").strip()
                for stat in row.find_all(
                    "td",
                    class_=lambda value: value is None
                    or "limiter" not in value.split(),
                )
            ]
            for row in driver_table_rows
        ]

        return driver_stats

    def get_constructors_championship_stats_by_range(self, start_season, end_season):
        constructor_stats = {}

        for season in range(start_season, end_season + 1):
            website = f"https://www.formula1.com/en/results.html/{season}/team.html"
            soup = get_soup(website)

            driver_table_rows = soup.find_all("tr")[1:]

            driver_stats = [
                [
                    stat.get_text().replace("\n", " ").strip()
                    for stat in row.find_all(
                        "td",
                        class_=lambda value: value is None
                        or "limiter" not in value.split(),
                    )
                ]
                for row in driver_table_rows
            ]

            constructor_stats[season] = driver_stats

        return constructor_stats

    # Champions

    # By default, get the current season championship
    def get_drivers_world_champion(self, season=CURRENT_YEAR - 1):
        website = (
            f"https://en.wikipedia.org/wiki/{season}_Formula_One_World_Championship"
        )
        soup = get_soup(website)
        champion = (
            soup.find(class_="motorsport-season-nav-subheader")
            .select("a")[1]
            .get_text()
        )

        return champion

    def get_constructors_world_champion(self, season=CURRENT_YEAR - 1):
        website = (
            f"https://en.wikipedia.org/wiki/{season}_Formula_One_World_Championship"
        )
        soup = get_soup(website)
        champion = (
            soup.find(class_="motorsport-season-nav-subheader")
            .select("a")[3]
            .get_text()
        )

        return champion


def main():
    scraper = F1StatsScraper()

    test = scraper.get_drivers_by_season(2015)
    print(test)

    session.close()


if __name__ == "__main__":
    main()
