import argparse
import json

from BromleyWasteScraper import BromleyWasteScraper
from BromleyWasteURLCodeFinder import BromleyWasteURLCodeFinder


def display_waste_data(url_code: str) -> None:
    ''''''
    bold = '\033[1m'
    end = '\033[0m'

    scraper = BromleyWasteScraper(url_code)
    data = scraper.scrape()
    
    data = json.loads(data)

    print(f"{bold}Bromley Waste Services\n{data.get('address')}{end}\n")

    for service in data.get('services').values():
        print(f"{bold}{service.get('name')}{end}")
        print(f"  Next collection: {service.get('next_collection')}")
        print(f"  Last collection: {service.get('last_collection')}")
        print(f"  Frequency: {service.get('frequency')}")
        if service.get('message') is not None:
            print(f"  Message: {service.get('message')}")


def main():
    ''''''

    desc = '''Scrapes the collection dates of the various waste services
   offered by Bromley Council. The required argument is the 
   parameter taken from the URL after entering the address into
   https://recyclingservices.bromley.gov.uk/waste/'''

    argparser = argparse.ArgumentParser(description=desc)
    argparser.add_argument('-u', '--url_code', required=False)
    args = argparser.parse_args()
    
    if args.url_code:
        display_waste_data(args.url_code)
    else:
        url_code = BromleyWasteURLCodeFinder.search()
        display_waste_data(url_code)

if __name__ == '__main__':
    main()