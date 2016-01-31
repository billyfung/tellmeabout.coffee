from flask import Flask, render_template, send_file, send_from_directory, redirect, url_for
from google.appengine.ext import ndb
from google.appengine.api import memcache
from google.appengine.api.modules import modules
import io
import datetime
from models import Coffee
import scrapers
import logging
import os


app = Flask(__name__)
# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.
ALL_COFFEES_KEY = "coffees"
ALL_ROASTERS_KEY = "roasters"


@app.route('/')
def index():
    """Lists the coffeez"""
    coffees = memcache.get(ALL_COFFEES_KEY)
    if not coffees:
        coffees = Coffee.query(Coffee.active == True).fetch()
        # cannot store all images into memcached due to size limits
        for coffee in coffees:
            coffee.image = None
        memcache.set(ALL_COFFEES_KEY, coffees)
    roaster_query = memcache.get(ALL_ROASTERS_KEY)
    if not roaster_query:
        roaster_query = Coffee.query(projection=["roaster"], distinct=True).fetch()
        memcache.set(ALL_ROASTERS_KEY, roaster_query)
    roasters = [data.roaster for data in roaster_query]
    return render_template('index.html', coffees=coffees, roasters=roasters)

@app.route('/images/coffee/<int:coffee_id>')
def get_coffee_image(coffee_id):
    """Gets the image attached to the coffee"""
    coffee_int_id = int(coffee_id)
    coffee = memcache.get("coffee_image_{}".format(coffee_int_id))
    if not coffee:
        coffee = Coffee.get_by_id(coffee_int_id)
        memcache.set("coffee_image_{}".format(coffee_int_id), coffee)
    if coffee:
        if coffee.image:
            return send_file(io.BytesIO(coffee.image))
    return app.send_static_file('coffee.png')

@app.route('/favicon.ico')
def favicon():
    return redirect(url_for('static', filename='favicon.ico'))

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
        scrapers.scrape_intelli()
        scrapers.scrape_victrola()
        scrapers.scrape_stumptown()
        scrapers.scrape_heart()
        scrapers.scrape_bluebottle()
        memcache.flush_all()
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
            logging.info('Coffee {} was marked inactive'.format(coffee.name))
            inactive_coffees += 1
    logging.info("{} coffees were newly marked inactive".format(inactive_coffees))
    return "Finished checking active coffees"

@app.route('/cron/stop_non_default_instances')
def cron_stop_non_default_instances():
    # core logic (inside a cron or other handler)
    for m in modules.get_modules():
        dv = modules.get_default_version(m)
        for v in modules.get_versions(m):
            if v != dv: modules.stop_version(m, v)
    return "Success!"
