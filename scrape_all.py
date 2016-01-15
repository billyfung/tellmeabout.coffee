from scrapers.stumptown import scrape
from scrapers.intelli import scrape_intelli


class CronTask(Handler):

    def get(self):
        scrape()
        scrape_intelli()
