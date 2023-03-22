import dateparser
import datetime
import json
import logging
import requests

from bs4 import BeautifulSoup
from requests.compat import urljoin


class BromleyWasteScraper:
    ''''''


    def __init__(self, url_code: int) -> None:
        ''''''

        self.url_code = url_code
        self.url = urljoin('https://recyclingservices.bromley.gov.uk/waste/', url_code)

        self.waste_services = {}


    def __format_service_names(self, name: str) -> str:
        ''''''

        if 'Food Waste' == name:
            return 'food_waste'
        if 'Mixed Recycling (Cans, Plastics & Glass)' == name:
            return 'mixed_recycling'
        if 'Garden Waste' == name:
            return 'garden_waste'
        if 'Paper & Cardboard' == name:
            return 'paper'
        if 'Non-Recyclable Refuse' == name:
            return 'refuse'
        
        return name


    def __format_service_item(self, key, value) -> dict:
        ''''''

        if 'Frequency' == key.text:
            return {'frequency': value.text.strip()}
        if 'Next collection' == key.text:
            return {'next_collection': dateparser.parse(value.text.strip()).date()}
        if 'Last collection' == key.text:
            split_value = value.text.strip().split('\n              \n              \n              \n')
            if len(split_value) == 1:
                return {'last_collection': dateparser.parse(split_value[0])}
            if len(split_value) == 2:
                return {'last_collection': dateparser.parse(split_value[0]), 'message': split_value[1]}


    def scrape(self) -> dict:
        '''Scrapes information and returns as JSON string'''

        try:
            page = requests.get(self.url)
            page.raise_for_status()
        except Exception as e:
            #HTTPError
            logging.exception(e)
            return None

        soup = BeautifulSoup(page.content, 'html.parser')

        self.address = soup.find('dd', 'waste__address__property').text

        self.waste_services['address'] = self.address
        self.waste_services['url_code'] = self.url_code
        self.waste_services['created_at'] = datetime.datetime.now()
        self.waste_services['services'] = {}

        waste_service_names = soup.find_all('h3', class_='waste-service-name')
        for waste_service_name in waste_service_names:

            summary = waste_service_name.find_next('dl', class_='govuk-summary-list')

            if summary is None:
                # Some services don't have collection dates
                continue

            keys = summary.find_all('dt', class_='govuk-summary-list__key')
            values = summary.find_all('dd', class_='govuk-summary-list__value')

            service_name = self.__format_service_names(waste_service_name.text)
            self.waste_services['services'][service_name] = { 'name': waste_service_name.text }

            for key, value in zip(keys, values):
                item = self.__format_service_item(key, value)
                self.waste_services['services'][service_name] |= item

        return self.waste_services


    def grab(self, update = False) -> dict:
        '''Return JSON string without updating data'''

        return self.waste_services


    def __str__(self) -> str:
        try:
            return f'{self.url_code} @ {self.address}'
        except AttributeError:
            # If scrape hasn't been called, address won't be initialized
            return f'{self.url_code}'