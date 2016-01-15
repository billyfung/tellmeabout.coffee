import webapp2
from scrapers.stumptown import scrape
#from scrapers.intelli import scrape_intelli


class CronTask(webapp2.RequestHandler):
    def get(self):
        scrape()
        #scrape_intelli()


application = webapp2.WSGIApplication([('/cronjobs', CronTask),], debug = True)

if __name__='__main__':
    app.run()