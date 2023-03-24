from BromleyWasteScraper import BromleyWasteScraper
from datetime import datetime
from flask import Flask, json
from markupsafe import escape

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
            return scraper.scrape()

        # If it is collection day, scrape new data to get collection time asap
        waste_services = scraper.waste_services.get('services').values()
        for waste_service in waste_services:
            if (waste_service.get('next_collection') == datetime.now().date()):
                return scraper.scrape()

        # No need to scrape the same data again
        return scrapers[url_code].grab()

    scrapers[url_code] = BromleyWasteScraper(url_code)
    # TODO: Error handling
    return scrapers[url_code].scrape()

if (__name__ == '__main__'):
    app.run(debug=True)