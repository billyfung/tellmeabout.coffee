from bs4 import BeautifulSoup
from helpers import country_from_name, add_or_update_coffee
from models import Coffee
import requests
import logging
import re


def scrape_victrola():
    roaster = 'Victrola'
    base_url = 'http://www.victrolacoffee.com'
    victrola = 'http://www.victrolacoffee.com/collections/all-coffee-offerings'

    r = requests.get(victrola)
    soup = BeautifulSoup(r.content, "html.parser")
    coffees_for_sale = soup.select('a.product-link')
    total_coffees = len(coffees_for_sale)
    coffees_entered = 0
    coffees_updated = 0
    error_coffees = []
    ignored = 'subscription'
    for item in coffees_for_sale:
        url = item['href']
        if ignored in url:
            total_coffees = total_coffees - 1
            continue
        name, description, notes, region, active, size, product_url = [""] * 7
        price = int()
        product_url = base_url + url
        logging.info("Getting url: {}".format(url))
        coffee_soup = BeautifulSoup(
            requests.get(product_url).content, "html.parser")
        if coffee_soup.find(
                'div',
            {'class': 'select single'}).find('label').text != 'Size':
            # its sold out?
            total_coffees = total_coffees - 1
            continue
        name = coffee_soup.h2.string
        try:
            size = coffee_soup.find('select').option.string.replace(" ",
                                                                    "")[:4]
        except AttributeError:
            logging.info('Cannot find size for {}'.format(name))
            continue
        active = False
        if coffee_soup.find(itemprop='price'):
            price = float(
                coffee_soup.find(itemprop='price').string.strip()[2:])
            active = True
        description_raw = coffee_soup.select_one('h4.mobile').next_siblings
        if 'Blend' in name:
            # different stuff for blends
            notes = []
            region = ''
            for x in description_raw:
                if x.string:
                    description += x.string.strip()
        else:
            # sometimes tasting notes just alone
            # sometimes they are in 'Flavor'
            # sometimes there are no tasting notes...
            flavor = coffee_soup(text=re.compile('Flavor:'))
            tasting_notes = coffee_soup.find(text="Tasting Notes")
            if flavor:
                notes = flavor[1].string.strip()[8:].rstrip(',').lower().split(
                    ',')
            elif tasting_notes:
                notes = coffee_soup.find(
                    text="Tasting Notes").next_element.strip()[2:].rstrip(
                        ',').lower().split(',')
            else:
                # can't find any tasting notes
                notes = []
                logging.info('No tasting notes for {}'.format(product_url))
        # slider image is too big so we're using the twitter one
        # image_url = coffee_soup.select_one('ul.bx-slider').select_one('img')['src']
        image_url = coffee_soup.find("meta", {"name": "twitter:image"})["content"]
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

    logging.info('Victrola New Results:{} / {}'.format(coffees_entered,
                                                       total_coffees))
    logging.info('Victrola Updated Results:{} / {}'.format(coffees_updated,
                                                           total_coffees))
    if error_coffees:
        logging.warning('Victrola Error coffees are: {}'.format(error_coffees))
