from bs4 import BeautifulSoup
import requests

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


def main():
    scraper = F1StatsScraper()
    page = scraper.getPage(website)
    soup = scraper.makeSoup(page)
    column_names = scraper.getColumnNames(soup)


if __name__ == "__main__":
    main()
