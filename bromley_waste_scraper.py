desc = '''Scrapes the collection dates of the various waste services
   offered by Bromley Council. The required argument is the 
   parameter taken from the URL after entering the address into
   https://recyclingservices.bromley.gov.uk/waste/'''

import argparse, dateparser, datetime, json, requests, sys

from bs4 import BeautifulSoup
from requests.compat import urljoin

parser = argparse.ArgumentParser(description=desc)
parser.add_argument('location_ID')
args = parser.parse_args()

URL = "https://recyclingservices.bromley.gov.uk/waste/"
URL = urljoin(URL, args.location_ID)

try:
    page = requests.get(URL)
    page.raise_for_status()
except requests.exceptions.HTTPError as e:
    print(e)
    sys.exit(1)

soup = BeautifulSoup(page.content, 'html.parser')

# Scrapes the address for the given URL
address = soup.find('dd', 'waste__address__property').text
print(address)

def format_service_name(name: str) -> str:
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
    
    return name # Full name will have to do

def format_service_item(key, value) -> dict:
    
    if 'Frequency' == key.text:
        return {'frequency': value.text.strip()}
    if 'Next collection' == key.text:
        return {'next_collection': dateparser.parse(value.text.strip())}
    if 'Last collection' == key.text:
        split_value = value.text.strip().split('\n              \n              \n              \n')
        if len(split_value) == 1:
            return {'last_collection': dateparser.parse(split_value[0])}
        if len(split_value) == 2:
            return {'last_collection': dateparser.parse(split_value[0]), 'message': split_value[1]}

'''For each 'waste-service-name' follows a 'govuk-summary-list', consisting of
   multiple 'govuk-summary-list__row', each holding a 'govuk-summary-list__key'
   and a 'govuk-summary-list__value', which contains each date

   e.g.
   waste-service-name (Garden waste)
        govuk-summary-list
            govuk-summary-list__row
                govuk-summary-list__key (Next collection)
                govuk-summary-list__value (Thursday, 9th March)
            ...
'''

waste_services = dict()
waste_services['address'] = address
waste_services['code'] = args.location_ID
#waste_services['scrape_datetime'] = datetime.datetime.now()
waste_services['services'] = dict()

waste_services_names = soup.find_all('h3', class_='waste-service-name')

for waste_service_name in waste_services_names:

    summary = waste_service_name.find_next('dl', class_='govuk-summary-list')
    
    if summary is None:
        # Some services don't have collection dates
        continue

    keys = summary.find_all('dt', class_='govuk-summary-list__key')
    values = summary.find_all('dd', class_='govuk-summary-list__value')

    service_name = format_service_name(waste_service_name.text)
    waste_services['services'][service_name] = { 'name': waste_service_name.text }
    for key, value in zip(keys, values):
        item = format_service_item(key, value)
        waste_services['services'][service_name] |= item

# Example output

for service in waste_services['services']:
    print(waste_services['services'][service])

# JSON Output
with open('scraped_waste.json', 'w') as file:
    file.write(json.dumps(waste_services, default=str))