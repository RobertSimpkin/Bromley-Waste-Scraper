from BromleyWasteScraper import BromleyWasteScraper
from datetime import datetime
from flask import Flask, json
from markupsafe import escape

app = Flask(__name__)

scrapers = {}


@app.route('/<url_code>')
def return_json(url_code: str):
    # Check if code is already scraped
    #   If the JSON is a day old, scrape again
    #   If there is a collection today, check every X mins for notification?

    url_code = escape(url_code)

    if url_code in scrapers:

        scraper = scrapers[url_code]
        
        current_data_datetime = scraper.waste_services.get('created_at')
        if (current_data_datetime.date() < datetime.now().date()):
            # Scrape once a day at least
            return scraper.scrape()
        
        # TODO: Check each service to see if collection date is today,
        # if so, check every 5? mins to facilitate notifications?

        return scrapers[url_code].grab()
    
    scrapers[url_code] = BromleyWasteScraper(url_code)
    # TODO: Error handling
    return scrapers[url_code].scrape()