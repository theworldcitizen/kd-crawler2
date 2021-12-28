from bs4 import BeautifulSoup
import requests
from models import Individual_details, Insolvency_case_details, Practitioner_contact, Service_contact, \
    Data

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

        personal_info = []
        case_info = []
        practitioner_info = []
        service_info = []
        result = []
        for link in links:
            html = self.make_request(link)
            soup = self.get_soup(html)
            lastname = self.get_lastname_by_fio(soup)
            firstname = self.get_firstname_by_fio(soup)
            title = self.get_title_by_fio(soup)
            gender = self.get_gender_by_fio(soup)
            occupation = self.get_occupation_by_fio(soup)
            birth_date = self.get_birth_date_by_fio(soup)
            personal_address = self.get_address_by_fio(soup)
            individual_details = Individual_details(lastname=lastname, firstname=firstname, title=title, gender=gender,
                                                    occupation=occupation, birth_date=birth_date,
                                                    address=personal_address)
            personal_info.append(individual_details)

            case_name = self.get_case_name_by_fio(soup)
            court = self.get_court_by_fio(soup)
            type = self.get_type_by_fio(soup)
            number = self.get_number_by_fio(soup)
            arrangement_date = self.get_arrangement_date_by_fio(soup)
            status = self.get_status_date_by_fio(soup)
            # notification_date = self.get_notification_date_by_fio(soup)
            case_details = Insolvency_case_details(fullname=case_name, court=court, type=type, number=number,
                                                   arrangement_date=arrangement_date, status=status)
            case_info.append(case_details)

            fullname = self.get_practitioners_by_fio(soup)
            org_name = self.get_firm_by_fio(soup)
            practitioner_address = self.get_practitioner_addres_by_fio(soup)
            post_code = self.get_post_code_by_fio(soup)
            practitioner_phone = self.get_practitioner_phone_by_fio(soup)
            practitioner_details = Practitioner_contact(fullname=fullname, org_name=org_name,
                                                        address=practitioner_address, post_code=post_code,
                                                        phone=practitioner_phone)
            practitioner_info.append(practitioner_details)

            ins_office = self.get_ins_ser_office(soup)
            ins_contact = self.get_ins_ser_contact(soup)
            ins_address = self.get_ins_ser_address(soup)
            ins_post_code = self.get_ins_ser_post_code(soup)
            ins_telephone = self.get_ins_ser_telephone(soup)
            contact_details = Service_contact(insolvency_service_office=ins_office, contact=ins_contact,
                                              address=ins_address, post_code=ins_post_code, phone=ins_telephone)
            service_info.append(contact_details)

            res = Data(personal_info=personal_info, case_info=case_info, practitioner_contact=practitioner_info,
                       service_contact=service_info).dict()
            result.append(res)

        return result

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
    def get_lastname_by_fio(soup: BeautifulSoup):
        try:
            table = soup.find(text="Surname").find_parent("table")
        except:
            return 'test'
        rows = table.find_all("tr")
        for row in rows:
            row = row.text
            row = row.splitlines()
            if 'Surname' in row:
                surname = row[5]
                return surname

    @staticmethod
    def get_firstname_by_fio(soup: BeautifulSoup):
        try:
            table = soup.find(text="Surname").find_parent("table")
        except:
            return 'test'
        rows = table.find_all("tr")
        for row in rows:
            row = row.text
            row = row.splitlines()
            if 'Forename(s)' in row:
                firstname = row[5]
                return firstname

    @staticmethod
    def get_title_by_fio(soup: BeautifulSoup):
        try:
            table = soup.find(text="Surname").find_parent("table")
        except:
            return 'test'
        rows = table.find_all("tr")
        for row in rows:
            row = row.text
            row = row.splitlines()
            if 'Title' in row:
                title = row[5]
                return title

    @staticmethod
    def get_gender_by_fio(soup: BeautifulSoup):
        try:
            table = soup.find(text="Surname").find_parent("table")
        except:
            return 'test'
        rows = table.find_all("tr")
        for row in rows:
            row = row.text
            row = row.splitlines()
            if 'Gender' in row:
                gender = row[5]
                return gender

    @staticmethod
    def get_occupation_by_fio(soup: BeautifulSoup):
        try:
            table = soup.find(text="Surname").find_parent("table")
        except:
            return 'test'
        rows = table.find_all("tr")
        for row in rows:
            row = row.text
            row = row.splitlines()
            if 'Occupation' in row:
                occupation = row[5]
                return occupation

    @staticmethod
    def get_birth_date_by_fio(soup: BeautifulSoup):
        try:
            table = soup.find(text="Surname").find_parent("table")
        except:
            return 'test'
        rows = table.find_all("tr")
        for row in rows:
            row = row.text
            row = row.splitlines()
            if 'Date of Birth' in row:
                date_of_birth = row[5]
                return date_of_birth

    @staticmethod
    def get_address_by_fio(soup: BeautifulSoup):
        try:
            table = soup.find(text="Surname").find_parent("table")
        except:
            return 'test'
        rows = table.find_all("tr")
        for row in rows:
            row = row.text
            row = row.splitlines()
            if 'Last Known Address' in row:
                address = row[5]
                return address

    def get_pagination(self, link):
        html = self.make_request(link)
        soup = self.get_soup(html)
        content = soup.find("div", id="mainbody")
        pagination_list = []
        for element in content:
            a = element.find('a', accesskey="iCount")
            url = a.get("href")
            pagination_list.append(url)
        return pagination_list[-1]

    @staticmethod
    def get_case_name_by_fio(soup: BeautifulSoup):
        try:
            table = soup.find_all("table")

        except:
            return 'Table 2 does not exist'
        table = table[2].find_all('tr')

        for element in table:
            row = element.find_all('td')
            name = row[0].text
            value = row[1].text
            if name == 'Case Name':
                return value

    @staticmethod
    def get_court_by_fio(soup: BeautifulSoup):
        try:
            table = soup.find_all("table")
        except:
            return 'Table 2 does not exist'
        table = table[2].find_all('tr')

        for element in table:
            row = element.find_all('td')
            name = row[0].text
            value = row[1].text
            if name == 'Court':
                return value

    @staticmethod
    def get_type_by_fio(soup: BeautifulSoup):
        try:
            table = soup.find_all("table")
        except:
            return 'Table 2 does not exist'
        rows = table[2].find_all('tr')

        for row in rows:
            data = row.find_all('td')
            name = data[0].text.strip()
            value = data[1].text
            if name == 'Type':
                return value

    @staticmethod
    def get_number_by_fio(soup: BeautifulSoup):
        try:
            table = soup.find_all("table")
        except:
            return 'Table 2 does not exist'
        rows = table[2].find_all('tr')

        for row in rows:
            data = row.find_all('td')
            name = data[0].text.strip()
            value = data[1].text
            if name == 'Number':
                return value

    @staticmethod
    def get_arrangement_date_by_fio(soup: BeautifulSoup):
        try:
            table = soup.find_all("table")
        except:
            return 'Table 2 does not exist'
        rows = table[2].find_all('tr')

        for row in rows:
            data = row.find_all('td')
            name = data[0].text.strip()
            value = data[1].text
            if name == 'Arrangement Date':
                return value

    @staticmethod
    def get_status_date_by_fio(soup: BeautifulSoup):
        try:
            table = soup.find_all("table")
        except:
            return 'Table 2 does not exist'
        rows = table[2].find_all('tr')

        for row in rows:
            data = row.find_all('td')
            name = data[0].text.strip()
            value = data[1].text
            if name == 'Status':
                return value

    @staticmethod
    def get_notification_date_by_fio(soup: BeautifulSoup):
        try:
            table = soup.find_all("table")
        except:
            return 'Table 2 does not exist'
        rows = table[2].find_all('tr')

        for row in rows:
            data = row.find_all('td')
            name = data[0].text.strip()
            value = data[1].text
            if name == 'Notification date':
                return value

    @staticmethod
    def get_practitioners_by_fio(soup: BeautifulSoup):
        fullnames = []
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
            if name == "Main Insolvency Practitioner":
                fullnames.append(value)
                return fullnames

    @staticmethod
    def get_firm_by_fio(soup: BeautifulSoup):

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
            if name == "Firm":
                return value

    @staticmethod
    def get_practitioner_addres_by_fio(soup: BeautifulSoup):

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
            if name == "Address":
                return value

    @staticmethod
    def get_post_code_by_fio(soup: BeautifulSoup):

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
            if name == "Post Code":
                return value

    @staticmethod
    def get_practitioner_phone_by_fio(soup: BeautifulSoup):

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
            if name == "Telephone":
                return value

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
