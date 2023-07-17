from bs4 import BeautifulSoup
import requests
from datetime import datetime
import re

website = "https://www.formula1.com/en/results.html/2022/drivers.html"


class F1StatsScraper:
    def getPage(self, url):
        page = requests.get(url)
        return page

    def makeSoup(self, page):
        # Using lxml parser for speed (as BeautifulSoup docs say)
        soup = BeautifulSoup(page.content, "lxml")
        return soup

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

    def getDriversStats(self, soup, seasons_num):
        drivers_stats = []
        for row in soup.find_all("tr")[1:]:
            driver_stats = []
            for stat in row.find_all(
                "td",
                class_=lambda value: value is None or "limiter" not in value.split(),
            ):
                driver_stats.append(stat.getText())
            drivers_stats.append(driver_stats)

        return drivers_stats

    # def getDriversStats(self, soup, seasons_num):
    #     drivers_stats = []
    #     driver_rows = soup.find_all("tr")[1:]
    #     for driver in driver_rows:
    #         driver_stats = []
    #         driver_columns = driver.find_all("td")
    #         for stats in driver_columns:
    #             driver_stats.append(stats.getText())
    #         drivers_stats.append(driver_stats)

    #     return soup.find_all("tr")[1:]


def main():
    scraper = F1StatsScraper()
    page = scraper.getPage(website)
    soup = scraper.makeSoup(page)
    column_names = scraper.getColumnNames(soup)
    drivers_stats = scraper.getDriversStats(soup, 1)
    print(len(drivers_stats[0]))


if __name__ == "__main__":
    main()
