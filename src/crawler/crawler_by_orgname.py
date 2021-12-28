from bs4 import BeautifulSoup
import requests
import pydantic
import json
from models import Individual_details, Insolvency_case_details, Practitioner_contact, Service_contact, \
    Result_by_fullname, Individual_insolvency_register, Result_by_organization

ENTRY_POINT = "https://www.insolvencydirect.bis.gov.uk/eiir/"


class Crawler:
    headers = {
        'sec-ch-ua': '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
        'sec-ch-ua-platform': '"Linux"',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-dest': 'document',
        'referer': 'https://www.insolvencydirect.bis.gov.uk/eiir',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    }

    def make_request(self, url: str, data: dict = None, params=None):
        response = requests.post(ENTRY_POINT + url, data=data, headers=self.headers, params=params)
        # print(response.url)
        if response.ok:
            return response.text

    def get_soup(self, html) -> BeautifulSoup:
        soup = BeautifulSoup(html, "html.parser")
        return soup

    def get_main_page_by_organization(self, trading_name: str):
        params = {'option': 'TRADING',
                  'court': 'ALL'
                  }

        data = {'tradingnamesearch': trading_name}

        html = self.make_request("IIRSearchNames.asp", data=data, params=params)
        links = self.get_links_by_organization(html)

        info_by_organization = []
        for link in links:
            html = self.make_request(link)
            soup = self.get_soup(html)
            firstname = self.get_firstname_by_trading(soup)
            lastname = self.get_lastname_by_trading(soup)
            date_of_birth = self.get_birth_date_by_trading(soup)
            name_of_organization = self.get_organization_name(soup)
            court = self.get_court_by_trading(soup)
            number = self.get_phone_number_by_trading(soup)
            start_date = self.get_start_date_by_trading(soup)
            type = self.get_type_by_trading(soup)
            info = Individual_insolvency_register(firtname=firstname, lastname=lastname, birth_date=date_of_birth,
                                                  org_name=name_of_organization,
                                                  court=court, number=number, start_date=start_date, type=type)
            info_by_organization.append(info)
        return info_by_organization

    def get_links_by_organization(self, html):
        soup = self.get_soup(html)

        links_by_surname_in_organization = []
        content = soup.find("table", class_="DataTable", id="MyTable")
        body = content.find("tbody")
        rows = body.find_all("tr")
        for row in rows:
            data = row.find_all("td")

            surname = data[1]
            a = surname.find("a")
            link = a.get("href")
            links_by_surname_in_organization.append(link)
        return links_by_surname_in_organization

    @staticmethod
    def get_firstname_by_trading(soup: BeautifulSoup):
        content = soup.find("table", class_="DataTable", id="MyTable")
        body = content.find("tbody")
        rows = body.find_all("tr")
        for row in rows:
            data = row.find_all("td")

            firstname = data[0].text
        return firstname

    @staticmethod
    def get_lastname_by_trading(soup: BeautifulSoup):
        content = soup.find("table", class_="DataTable", id="MyTable")
        body = content.find("tbody")
        rows = body.find_all("tr")
        for row in rows:
            data = row.find_all("td")

            lastname = data[1].text
        return lastname

    @staticmethod
    def get_birth_date_by_trading(soup: BeautifulSoup):
        content = soup.find("table", class_="DataTable", id="MyTable")
        body = content.find("tbody")
        rows = body.find_all("tr")
        for row in rows:
            data = row.find_all("td")

            birth_date = data[2].text
        return birth_date

    @staticmethod
    def get_organization_name(soup: BeautifulSoup):
        content = soup.find("table", class_="DataTable", id="MyTable")
        body = content.find("tbody")
        rows = body.find_all("tr")
        for row in rows:
            data = row.find_all("td")

            org_name = data[3].text
        return org_name

    @staticmethod
    def get_court_by_trading(soup: BeautifulSoup):
        content = soup.find("table", class_="DataTable", id="MyTable")
        body = content.find("tbody")
        rows = body.find_all("tr")
        for row in rows:
            data = row.find_all("td")

            court = data[4].text
        return court

    @staticmethod
    def get_phone_number_by_trading(soup: BeautifulSoup):
        content = soup.find("table", class_="DataTable", id="MyTable")
        body = content.find("tbody")
        rows = body.find_all("tr")
        for row in rows:
            data = row.find_all("td")

            number = data[5].text
        return number

    @staticmethod
    def get_start_date_by_trading(soup: BeautifulSoup):
        content = soup.find("table", class_="DataTable", id="MyTable")
        body = content.find("tbody")
        rows = body.find_all("tr")
        for row in rows:
            data = row.find_all("td")

            start_date = data[6]
        return start_date

    @staticmethod
    def get_type_by_trading(soup: BeautifulSoup):
        content = soup.find("table", class_="DataTable", id="MyTable")
        body = content.find("tbody")
        rows = body.find_all("tr")
        for row in rows:
            data = row.find_all("td")

            type = data[7].text
        return type

    def demo(self, name: str):
        params = (
            ('court', 'ALL'),
            ('courtname', ''),
            ('office', ''),
            ('officename', ''),
            ('OPTION', 'TRADING'),
        )

        data = {'tradingnamesearch': name,
                }

        html = self.make_request("IIRSearchNames.asp", data=data, params=params)

        soup = self.get_soup(html)
        return soup


if __name__ == "__main__":
    from pprint import pprint

    result = Crawler().get_main_page_by_organization('Ali')
    pprint(result)
