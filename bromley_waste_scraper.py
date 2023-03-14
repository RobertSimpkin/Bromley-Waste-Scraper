desc = '''Scrapes the collection dates of the various waste services
   offered by Bromley Council. The required argument is the 
   parameter taken from the URL after entering the address into
   https://recyclingservices.bromley.gov.uk/waste/'''


import argparse, requests, sys

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

def parse_list_value(data: str):
    '''
    The list__value may contain a message about a missed collection, alongside the
    time and date. Format and return the data
    '''
    split = data.strip().split("\n              \n              \n              \n")

    if len(split) == 1:
        return { "Date": split[0] }
    
    if len(split) == 2:
        return { "Date": split[0], "Message": split[1] }
    
    return None # Unexpected

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

waste_services_dates = dict()

waste_services_names = soup.find_all('h3', class_='waste-service-name')

for waste_service_name in waste_services_names:

    summary = waste_service_name.find_next('dl', class_='govuk-summary-list')
    
    if summary is None:
        # Some services don't have collection dates
        continue

    keys = summary.find_all('dt', class_='govuk-summary-list__key')
    values = summary.find_all('dd', class_='govuk-summary-list__value')

    waste_services_dates[waste_service_name.text] = dict(zip([k.text for k in keys], [parse_list_value(v.text) for v in values]))


# Example output

for key, value in waste_services_dates.items():
    print(key)
    for item, date in value.items():
        print(f'   {item}: {date}')

print(waste_services_dates.get('Food Waste').get('Next collection'))