from bs4 import BeautifulSoup
import requests
from models import PersonalInfo, Insolvency_case_details, Practitioner_contact, Service_contact
import re

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

        if response.ok:
            return response.text

    def get_soup(self, html) -> BeautifulSoup:
        soup = BeautifulSoup(html, "html.parser")
        return soup

    def get_main_page_by_fullname(self, name: str):
        params = {'option': 'NAME',
                  'court': 'ALL'
                  }
        data = {
            "surnamesearch": name
        }

        html = self.make_request("IIRSearchNames.asp", data=data, params=params)
        links = self.get_links_by_surname(html)

        service_info = []
        for link in links:

            html = self.make_request(link)

            soup = self.get_soup(html)

            try:
                ins_office = self.get_ins_ser_office(soup)
                ins_contact = self.get_ins_ser_contact(soup)
                ins_address = self.get_ins_ser_address(soup)
                ins_post_code = self.get_ins_ser_post_code(soup)
                ins_telephone = self.get_ins_ser_telephone(soup)
                contact_details = Service_contact(insolvency_service_office=ins_office, contact=ins_contact,
                                                  address=ins_address, post_code=ins_post_code, phone=ins_telephone)
                service_info.append(contact_details)


            except AttributeError:
                print('error')
        return service_info

    def get_links_by_surname(self, html):
        soup = self.get_soup(html)

        links_by_surname = []

        content = soup.find("table", class_="DataTable")
        body = content.find("tbody")
        rows = body.find_all("tr")
        for row in rows:
            data = row.find_all("td")

            surname = data[1]
            a = surname.find('a')
            link = a.get("href")
            links_by_surname.append(link.strip())
        return links_by_surname

    @staticmethod
    def get_ins_ser_office(soup: BeautifulSoup):
        offices = []
        try:
            table = soup.find_all("table")
        except:
            return 'Table 2 does not exist'
        rows = table[2].find_all('tr')

        for row in rows:

            # print(row.text)
            data = row.find_all('td')
            try:
                name = data[0].text.strip()
                value = data[1].text.strip()
            except:
                if name == ' ' and value == ' ' or None:
                    continue
            if name == "Insolvency Service Office":
                offices.append(value)
                return offices

    @staticmethod
    def get_ins_ser_contact(soup: BeautifulSoup):

        try:
            table = soup.find_all("table")
        except:
            return 'Table 2 does not exist'
        rows = table[2].find_all('tr')

        for row in rows:

            # print(row.text)
            data = row.find_all('td')
            try:
                name = data[0].text.strip()
                value = data[1].text.strip()
            except:
                if name == ' ' and value == ' ' or None:
                    continue
            if name == "Contact":
                return value

    @staticmethod
    def get_ins_ser_address(soup: BeautifulSoup):
        full_info = []

        try:
            table = soup.find_all("table")
        except:
            return 'Table 2 does not exist'
        rows = table[2].find_all('tr')
        for row in rows:
            data = row.find_all('td')
            try:
                name = data[0].text.strip()
                value = data[1].text.strip()
                res = {
                    'name': name,
                    'value': value
                }

                full_info.append(res)
            except:
                if name == ' ' and value == ' ' or None:
                    continue
        info = full_info[-3]
        answer = info.get('value')
        return answer

    @staticmethod
    def get_ins_ser_post_code(soup: BeautifulSoup):
        full_info = []

        try:
            table = soup.find_all("table")
        except:
            return 'Table 2 does not exist'
        rows = table[2].find_all('tr')
        for row in rows:
            data = row.find_all('td')
            try:
                name = data[0].text.strip()
                value = data[1].text.strip()
                res = {
                    'name': name,
                    'value': value
                }

                full_info.append(res)
            except:
                if name == ' ' and value == ' ' or None:
                    continue
        info = full_info[-2]
        answer = info.get('value')
        return answer



    @staticmethod
    def get_ins_ser_telephone(soup: BeautifulSoup):
        full_info = []

        try:
            table = soup.find_all("table")
        except:
            return 'Table 2 does not exist'
        rows = table[2].find_all('tr')
        for row in rows:
            data = row.find_all('td')
            try:
                name = data[0].text.strip()
                value = data[1].text.strip()
                res = {
                    'name': name,
                    'value': value
                }

                full_info.append(res)
            except:
                if name == ' ' and value == ' ' or None:
                    continue
        info = full_info[-1]
        answer = info.get('value')
        return answer




if __name__ == "__main__":
    from pprint import pprint

    result = Crawler().get_main_page_by_fullname('Ikram')
    pprint(result)
