from bs4 import BeautifulSoup
import requests
from datetime import datetime
import asyncio

# Create a session to reuse the TCP connection (much better performance)
session = requests.Session()


def getSoup(website):
    page = session.get(website)
    page.raise_for_status()
    soup = BeautifulSoup(page.content, "lxml")
    return soup


class F1StatsScraper:
    def __init__(self):
        pass

    def getDrivers(self):
        drivers = set()
        for season in range(1950, 2024):
            website = f"https://www.formula1.com/en/results.html/{season}/drivers.html"
            soup = getSoup(website)
            for driver in soup.find_all("tr")[1:]:
                name = driver.find("a").getText()

                # Transforming name to not contain a name tag
                name_array_without_tag = (
                    driver.find("a").getText().strip().splitlines()[:-1]
                )

                name_transformed = " ".join(name_array_without_tag)
                nationality = driver.find(
                    "td", class_="dark semi-bold uppercase"
                ).getText()
                drivers.add((name_transformed, nationality))
        return drivers

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
        for season in range(1950, 2024):
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

    def getDriversRacePoints(self):
        drivers_points = []
        for season in range(2022, 2023):
            website = f"https://www.formula1.com/en/results.html/{season}/drivers/MAXVER01/max-verstappen.html"
            # website = f"https://www.formula1.com/en/results.html/{season}/drivers.html"
            soup = getSoup(website)
            for grand_prix in soup.find_all("tr")[1:]:
                driver_points = []
                for points in grand_prix.find_all("td", class_="bold"):
                    driver_points.append(points.getText().replace("\n", " ").strip())
                drivers_points.append(driver_points)

        return drivers_points


def main():
    website = "https://www.formula1.com/en/results.html/2022/drivers.html"

    scraper = F1StatsScraper()

    drivers = scraper.getDrivers()
    print(drivers)

    session.close()


if __name__ == "__main__":
    main()
