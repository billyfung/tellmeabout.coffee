from bs4 import BeautifulSoup
from helpers import country_from_name, add_or_update_coffee
from models import Coffee
import requests
import logging
import re


def scrape_stumptown():
    roaster = 'Stumptown'
    stumptown = 'https://www.stumptowncoffee.com/coffee'
    base_url = 'https://www.stumptowncoffee.com'

    r = requests.get(stumptown)
    soup = BeautifulSoup(r.content, "html.parser")
    coffees_for_sale = soup.select('a.product-grid._link')
    total_coffees = len(coffees_for_sale)
    coffees_entered = 0
    coffees_updated = 0
    error_coffees = []
    ignored = "trio"
    for items in coffees_for_sale:
        url = items['href']
        if ignored in url:
            total_coffees = total_coffees - 1
            continue

        name, price, description, notes, region, active, size = [""] * 7

        product_url = base_url + url
        logging.info("Getting url: {}".format(url))
        r = requests.get(product_url)
        coffee_soup = BeautifulSoup(r.content, "html.parser")

        name = coffee_soup.h1.string.strip()
        price = float(coffee_soup.select_one('span.js-pdp-price').text)
        description = coffee_soup.select_one('div.product._description').p.text
        try:
            notes = coffee_soup.h3.string.replace('&', ',').lower().split(',')
        except AttributeError: # no notes found
            pass
        region = country_from_name(name)
        active = True
        if coffee_soup.h6: # its sold out
            active = False
        try:
            size = '{} oz'.format(
                re.findall('\d+',
                           coffee_soup.select_one('div.product._specs')
                           .find_all('p')[1].string)[0])
        except Exception as e:
            logging.warn("Error while getting size for {} : {}".format(name,
                                                                       e))
        image_url = coffee_soup.select_one('div.product._image span')[
            'data-src']
        image_content = requests.get(image_url).content
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
            'image': image_content
        }
        coffees_updated, coffees_entered, error_coffees = add_or_update_coffee(
            coffee_data, coffees_updated, coffees_entered, error_coffees)

    logging.info('Stumptown New Results:{} / {}'.format(coffees_entered,
                                                        total_coffees))
    logging.info('Stumptown Updated Results:{} / {}'.format(coffees_updated,
                                                            total_coffees))
    if error_coffees:
        logging.warning('Stumptown Error coffees are: {}'.format(
            error_coffees))
