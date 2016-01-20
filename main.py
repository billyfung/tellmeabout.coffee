from flask import Flask, render_template, send_file
from google.appengine.ext import ndb
from google.appengine.api import images
import io
import datetime
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
    coffees = Coffee.query(Coffee.active==True).fetch()
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

@app.route('/cron/scrape_all')
def cron_scrape():
    try:
        scrape_intelli()
        scrape_victrola()
        scrape_stumptown()
    except Exception as e:
        logging.warning("Error: {}".format(e))
    return "Finished scraping"

@app.route('/cron/check_active_coffees')
def cron_update():
    """ Checks active coffees to see if theyre inactive """
    coffees = Coffee.query(Coffee.active==True).fetch()
    logging.info('Checking for inactive coffees. Currently {} coffees are active'.format(len(coffees)))
    inactive_coffees = 0
    for coffee in coffees:
        if coffee.date_updated < datetime.datetime.now() - datetime.timedelta(days=2):
            coffee.active = False
            coffee.date_removed = datetime.datetime.now()
            coffee.put()
            logging.degug('Coffee {} was marked inactive'.format(coffee.name))
            inactive_coffees += 1
    logging.info("{} coffees were newly marked inactive".format(inactive_coffees))
    return "Finished checking active coffees"
