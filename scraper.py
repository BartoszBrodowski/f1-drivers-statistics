from bs4 import BeautifulSoup
import requests
from unidecode import unidecode

# Create a session to reuse the TCP connection (much better performance)
session = requests.Session()


def getSoup(website):
    page = session.get(website)
    page.raise_for_status()
    soup = BeautifulSoup(page.content, "lxml")
    return soup


class F1StatsScraper:
    def __init__(self, start_season, end_season):
        self.start_season = start_season
        self.end_season = end_season

    def getDrivers(self):
        drivers = set()
        for season in range(self.start_season, self.end_season):
            website = f"https://www.formula1.com/en/results.html/{season}/drivers.html"
            soup = getSoup(website)
            for driver in soup.find_all("tr")[1:]:
                nationality = driver.find(
                    "td", class_="dark semi-bold uppercase"
                ).getText()
                # Transforming name to not contain a name tag
                name_array_without_tag = (
                    driver.find("a").getText().strip().splitlines()[:-1]
                )
                name_transformed = " ".join(name_array_without_tag)
                drivers.add((name_transformed, nationality))
        return drivers

    def getDriversByYear(self, year):
        drivers = set()
        website = f"https://www.formula1.com/en/results.html/{year}/drivers.html"
        soup = getSoup(website)
        for driver in soup.find_all("tr")[1:]:
            name_array_without_tag = (
                driver.find("a").getText().strip().splitlines()[:-1]
            )
            name_transformed = " ".join(name_array_without_tag)
            drivers.add(name_transformed)

        return drivers

    def getGrandPrixLinksInSeason(self, season):
        grand_prix_links = {}
        website = f"https://www.formula1.com/en/results.html/{season}/races.html"
        soup = getSoup(website)
        grand_prix_list = soup.select("td > a")
        for grand_prix in grand_prix_list:
            grand_prix_name = grand_prix.getText().strip()
            grand_prix_href = grand_prix.get("href")
            link = "https://www.formula1.com" + grand_prix_href
            grand_prix_links[grand_prix_name] = link

        return grand_prix_links

    def getDriversWebsitesBySeason(self, season):
        websites = []
        drivers = self.getDriversByYear(season)
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

    def getDriversStatsForEveryRace(self):
        seasons = {}
        column_names = [
            "Position",
            "Number",
            "Driver",
            "Car",
            "Laps",
            "Time/Retired",
            "Points",
        ]
        for season in range(self.start_season, self.end_season):
            seasons[str(season)] = {}
            race_links = self.getGrandPrixLinksInSeason(season)

            # Add race names
            for race in race_links:
                # seasons[str(season)][race] = {}
                seasons[str(season)][race] = []
            drivers = self.getDriversByYear(season)

            # Add driver names, positions and points
            for race, link in race_links.items():
                soup = getSoup(link)
                table_rows = soup.select("tr")[1:]
                filtered_rows = [row for row in table_rows]

                for row in filtered_rows:
                    row_text = [
                        elem.text.replace("\n", " ") if i != 3
                        # Delete last 4 characters from drivers name because it's always ' TAG' (TAG is always first 3 letters of drivers surname)
                        else elem.text.replace("\n", " ")[:-5]
                        for i, elem in enumerate(row.find_all(["td"]))
                        # Ignore class='limiter' elements and exclude the 6th element
                        if "limiter" not in elem.get("class")
                    ]
                    row_dict = dict(zip(column_names, row_text))
                    seasons[str(season)][race].append(row_dict)

        return seasons
        # grand_prix_name = grand_prix.getText().strip()
        # grand_prix_website = "https://www.formula1.com" + grand_prix.get("href")
        # grand_prix_soup = getSoup(grand_prix_website)
        # for driver_website in driver_websites:
        #     driver_soup = getSoup(driver_website)
        #     driver_name = driver_soup.find(
        #         "h1", class_="ResultsArchiveTitle"
        #     ).getText()
        #     driver_points = driver_soup.find_all("td", class_="bold")[
        #         1
        #     ].getText()
        #     if driver_name not in seasons[str(season)]:
        #         seasons[str(season)][driver_name] = {}
        #     seasons[str(season)][driver_name][grand_prix_name] = driver_points
        # print(grand_prix_list)
        # print(seasons)

    def getRaceResults(self):
        races = set()

    def getColumnNames(self):
        website = "https://www.formula1.com/en/results.html/2023/drivers.html"
        soup = getSoup(website)
        column_name_change_map = {
            "Car": "Team",
            "PTS": "Points",
            "Pos": "Position",
        }

        column_names = [
            column_name_change_map.get(name.getText(), name.getText())
            for name in soup.find_all("th")
            if name.getText() != ""
        ]

        return column_names

    def getDriversChampionshipStats(self):
        drivers_stats = []
        for season in range(self.start_season, self.end_season):
            website = f"https://www.formula1.com/en/results.html/{season}/drivers.html"
            soup = getSoup(website)
            for row in soup.find_all("tr")[1:]:
                driver_stats = []
                for stat in row.find_all(
                    "td",
                    class_=lambda value: value is None
                    or "limiter" not in value.split(),
                ):
                    driver_stats.append(stat.getText().replace("\n", " ").strip())
                drivers_stats.append(driver_stats)

        return drivers_stats

    # def getDriversRacePoints(self):
    #     drivers_points = []
    #     for season in range(self.start_season, self.end_season):
    #         website = f"https://www.formula1.com/en/results.html/{season}/drivers/MAXVER01/max-verstappen.html"
    #         # website = f"https://www.formula1.com/en/results.html/{season}/drivers.html"
    #         soup = getSoup(website)
    #         for grand_prix in soup.find_all("tr")[1:]:
    #             driver_points = []
    #             for points in grand_prix.find_all("td", class_="bold"):
    #                 driver_points.append(points.getText().replace("\n", " ").strip())
    #             drivers_points.append(driver_points)

    #     return drivers_points


def main():
    website = "https://www.formula1.com/en/results.html/2022/drivers.html"

    scraper = F1StatsScraper(2012, 2013)

    # drivers = scraper.getDriversStatsForEveryRace()
    season_2012_stats = scraper.getDriversStatsForEveryRace()
    print(season_2012_stats["2012"]["Australia"])

    session.close()


if __name__ == "__main__":
    main()
