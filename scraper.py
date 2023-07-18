from bs4 import BeautifulSoup
import requests
from datetime import datetime
import asyncio


def getSoup(website):
    page = requests.get(website)
    soup = BeautifulSoup(page.content, "lxml")
    return soup


class F1StatsScraper:
    def __init__(self, soup):
        self.soup = soup

    def getColumnNames(self, soup):
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

    def getDriversStats(self, start_season, end_season):
        drivers_stats = []
        for season in range(start_season, end_season):
            website = f"https://www.formula1.com/en/results.html/{season}/drivers.html"
            print(website)
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
    soup = getSoup(website)

    scraper = F1StatsScraper(soup)
    column_names = scraper.getColumnNames(soup)
    drivers_stats = scraper.getDriversStats(2020, 2023)
    print(drivers_stats)
    # print(column_names)
    # print(drivers_stats)


if __name__ == "__main__":
    main()
