from bs4 import BeautifulSoup
import json
import requests
from models import Coffee
from helpers import add_or_update_coffee
from google.appengine.api import urlfetch
import logging


def scrape_intelli():
    urlfetch.set_default_fetch_deadline(10)
    roaster = 'Intelligentsia'
    intelli = 'https://www.intelligentsiacoffee.com/catalog/ajax/products/?filter%5Bcat%5D=5'
    r = requests.get(intelli)
    soup = BeautifulSoup(r.content, "html.parser")
    x = json.loads(soup.text)

    total_coffees = len(x['data'])
    coffees_entered = 0
    coffees_updated = 0
    error_coffees = []
    for item in x['data']:
        name, description, notes, region, active, size, product_url = [""] * 7
        price = int()
        product_url = item['productUrl']
        logging.info("Getting url: {}".format(product_url))
        try:
            notes = item['flavor_profile_text'].split(',')
        except KeyError:
            notes = [""]
        name = item['original_name']
        description = item['description']
        region = item['country']
        price = float(item['price'])
        size = '12oz'
        active = True
        image_url = 'https://www.intelligentsiacoffee.com/media/catalog/product' + item[
            'small_image']
        image_blob = requests.get(image_url).content
        coffee_data = {
            'name': name,
            'roaster': roaster,
            'description': description,
            'price': price,
            'notes': notes,
            'region': region,
            'active': active,
            'product_page': product_url,
            'size': size,
            'image': image_blob
        }
        coffees_updated, coffees_entered, error_coffees = add_or_update_coffee(
            coffee_data, coffees_updated, coffees_entered, error_coffees)

    logging.info('Intelligentsia New Results:{} / {}'.format(coffees_entered,
                                                             total_coffees))
    logging.info('Intelligentsia Updated Results:{} / {}'.format(
        coffees_updated, total_coffees))
    if error_coffees:
        logging.warning('Intelligensia Error coffees are: {}'.format(
            error_coffees))
