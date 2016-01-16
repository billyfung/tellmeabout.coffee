from flask import Flask, render_template
import webapp2
from google.appengine.ext import ndb
from models import Coffee
from scrapers.stumptown import scrape


app = Flask(__name__)
# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.

@app.route('/')
def index():
    """Lists the coffeez"""
    coffees = Coffee.query().fetch()
    return render_template('index.html', coffees=coffees)


@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, Nothing at this URL.', 404


@app.errorhandler(500)
def application_error(e):
    """Return a custom 500 error."""
    return 'Sorry, unexpected error: {}'.format(e), 500

@app.route('/cronjob')
def cron_scrape():
    try:
        scrape()
    except Exception as e:
        logging.warning("Error: {}".format(e))
    return "Finished scrape"

