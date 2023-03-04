'''Scrapes the collection dates of the various waste services
   offered by Bromley Council. The required argument is the 
   parameter taken after entering the address into
   https://recyclingservices.bromley.gov.uk/waste/'''


import requests, sys

from bs4 import BeautifulSoup
from requests.compat import urljoin


if len(sys.argv) < 2:
    print("Need 7 digit URL code argument")
    sys.exit()

URL_code = sys.argv[1]

# Basic argument validation
if not URL_code.isnumeric() or not len(URL_code) == 7:    #Bad code?
    print("7 digit URL code argument is invalid.")
    sys.exit()


URL = "https://recyclingservices.bromley.gov.uk/waste/"
URL = urljoin(URL, URL_code)

page = requests.get(URL)


soup = BeautifulSoup(page.content, 'html.parser')

# Scrapes the address for the given URL
address = soup.find('dd', 'waste__address__property').text
print(address)


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

    waste_services_dates[waste_service_name.text] = dict(zip([k.text for k in keys], [v.text.strip() for v in values]))


# Example output

for key, value in waste_services_dates.items():
    print(key)
    for item, date in value.items():
        print(f'   {item}: {date}')

print(waste_services_dates.get('Food Waste').get('Next collection'))