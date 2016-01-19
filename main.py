from flask import Flask, render_template, send_file
from google.appengine.ext import ndb
from google.appengine.api import images
import io
from models import Coffee
from scrapers.intelli import scrape_intelli
from scrapers.stumptown import scrape_stumptown
from scrapers.victrola import scrape_victrola
import logging


app = Flask(__name__)
# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.

@app.route('/')
def index():
    """Lists the coffeez"""
    coffees = Coffee.query().fetch()
    return render_template('index.html', coffees=coffees)

@app.route('/images/coffee/<int:coffee_id>')
def get_coffee_image(coffee_id):
    """Gets the image attached to the coffee"""
    coffee_int_id = int(coffee_id)
    coffee = Coffee.get_by_id(coffee_int_id)
    if coffee:
        if coffee.image:
            return send_file(io.BytesIO(coffee.image))
    return app.send_static_file('coffee.png')


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
        scrape_intelli()
        scrape_victrola()
        scrape_stumptown()
    except Exception as e:
        logging.warning("Error: {}".format(e))
    return "Finished scraping"
