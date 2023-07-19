from bs4 import BeautifulSoup
import requests
from unidecode import unidecode

# Create a session to reuse the TCP connection (much better performance)
session = requests.Session()


def get_soup(website):
    page = session.get(website)
    page.raise_for_status()
    soup = BeautifulSoup(page.content, "lxml")
    return soup


class F1StatsScraper:
    def get_drivers_by_season(self, season):
        drivers = set()
        website = f"https://www.formula1.com/en/results.html/{season}/drivers.html"
        soup = get_soup(website)
        for driver in soup.find_all("tr")[1:]:
            nationality = driver.find("td", class_="dark semi-bold uppercase").getText()
            # Transforming name to not contain a name tag
            name_array_without_tag = (
                driver.find("a").getText().strip().splitlines()[:-1]
            )
            name_transformed = " ".join(name_array_without_tag)
            drivers.add((name_transformed, nationality))
        return drivers

    def get_drivers_by_range(self, start_season, end_season):
        drivers = set()
        for season in range(start_season, end_season + 1):
            website = f"https://www.formula1.com/en/results.html/{season}/drivers.html"
            soup = get_soup(website)
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

    def get_drivers_by_season(self, season):
        drivers = set()
        website = f"https://www.formula1.com/en/results.html/{season}/drivers.html"
        soup = get_soup(website)
        for driver in soup.find_all("tr")[1:]:
            name_array_without_tag = (
                driver.find("a").getText().strip().splitlines()[:-1]
            )
            name_transformed = " ".join(name_array_without_tag)
            drivers.add(name_transformed)

        return drivers

    def get_race_results_link(self, season, race):
        website = f"https://www.formula1.com/en/results.html/{season}/races.html"
        soup = get_soup(website)
        race_tag = soup.find(lambda tag: tag.name == "a" and race in tag.text)
        link = race_tag.get("href")
        return "https://www.formula1.com" + link

    def get_race_links_by_season(self, season):
        grand_prix_links = {}
        website = f"https://www.formula1.com/en/results.html/{season}/races.html"
        soup = get_soup(website)
        grand_prix_list = soup.select("td > a")
        for grand_prix in grand_prix_list:
            grand_prix_name = grand_prix.getText().strip()
            grand_prix_href = grand_prix.get("href")
            link = "https://www.formula1.com" + grand_prix_href
            grand_prix_links[grand_prix_name] = link

        return grand_prix_links

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
        column_names = [
            "Position",
            "Number",
            "Driver",
            "Car",
            "Laps",
            "Time/Retired",
            "Points",
        ]
        for season in range(start_season, end_season + 1):
            seasons = {}
            race_links = self.get_race_links_by_season(season)

            # Add race names
            for race in race_links:
                seasons[str(season)][race] = []

            # Add driver names, positions and points
            for race, link in race_links.items():
                soup = get_soup(link)
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

    def get_column_names(self):
        website = "https://www.formula1.com/en/results.html/2023/drivers.html"
        soup = get_soup(website)
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

    def get_drivers_championship_stats(self, season):
        website = f"https://www.formula1.com/en/results.html/{season}/drivers.html"
        soup = get_soup(website)

        rows = soup.find_all("tr")[1:]

        drivers_stats = [
            [
                stat.getText().replace("\n", " ").strip()
                for stat in row.find_all(
                    "td",
                    class_=lambda value: value is None
                    or "limiter" not in value.split(),
                )
            ]
            for row in rows
        ]

        return drivers_stats

    def get_drivers_championship_stats_by_range(self, start_season, end_season):
        drivers_stats = []

        for season in range(start_season, end_season + 1):
            website = f"https://www.formula1.com/en/results.html/{season}/drivers.html"
            soup = get_soup(website)

            rows = soup.find_all("tr")[1:]

            driver_stats = [
                [
                    stat.getText().replace("\n", " ").strip()
                    for stat in row.find_all(
                        "td",
                        class_=lambda value: value is None
                        or "limiter" not in value.split(),
                    )
                ]
                for row in rows
            ]

        drivers_stats.extend(driver_stats)

        return drivers_stats


def main():
    scraper = F1StatsScraper()

    test = scraper.get_drivers_championship_stats(2022)
    print(test)

    session.close()


if __name__ == "__main__":
    main()
