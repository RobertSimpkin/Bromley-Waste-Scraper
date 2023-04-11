from BromleyWasteScraper import BromleyWasteScraper
from datetime import datetime
from flask import Flask, json
import logging
from markupsafe import escape
import sys

log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s" 
logging.basicConfig(format=log_format, level=logging.INFO)
app = Flask(__name__)

scrapers = {}

@app.route('/<url_code>')
def return_json(url_code: str):

    url_code = escape(url_code)

    if url_code in scrapers:

        scraper = scrapers[url_code]

        # If the data is a day old, scrape new data
        current_data_datetime = scraper.waste_services.get('created_at')
        if (current_data_datetime.date() < datetime.now().date()):
            app.logger.info("Scraping data: New day")
            return scraper.scrape()

        # If it is collection day, scrape new data to get collection time asap
        waste_services = scraper.waste_services.get('services').values()
        for waste_service in waste_services:
            if (waste_service.get('next_collection') == datetime.now().date()):
                app.logger.info(f"Scraping data: {waste_service.get('name')} Collection day")
                return scraper.scrape()

        # No need to scrape the same data again
        return scrapers[url_code].grab()

    scrapers[url_code] = BromleyWasteScraper(url_code)
    # TODO: Error handling
    app.logger.info("Scraping data: new address")
    return scrapers[url_code].scrape()

if (__name__ == '__main__'):
    app.run(debug=True)