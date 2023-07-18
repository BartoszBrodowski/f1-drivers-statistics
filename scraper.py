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

    def getDriversStats(self):
        drivers_stats = []
        for season in range(1950, 2023):
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

    def getDrivers(self, soup):
        pass


def main():
    website = "https://www.formula1.com/en/results.html/2022/drivers.html"

    scraper = F1StatsScraper()

    session.close()


if __name__ == "__main__":
    main()
