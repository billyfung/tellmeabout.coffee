from bs4 import BeautifulSoup
import requests
import logging
import re

from models import Coffee
from helpers import add_or_update_coffee


def scrape_matchstick():
    roaster = "Matchstick"
    base_url = "http://www.matchstickyvr.com"
    r = requests.get("http://www.matchstickyvr.com/collections/coffee/")
    soup = BeautifulSoup(r.content, "html.parser")

    coffees_for_sale = soup.select('div.productItem')
    total_coffees = len(coffees_for_sale)
    coffees_entered = 0
    coffees_updated = 0
    error_coffees = []
    ignored = 'subscription'

    for item in coffees_for_sale:
        if ignored in item.text.lower():
            total_coffees = total_coffees - 1
            continue

        name, description, notes, region, active, size, product_url = [""] * 7
        price = float()
        product_url = item.a['href']
        coffee_soup = BeautifulSoup(requests.get(base_url + product_url).content)
        name = coffee_soup.h1.text
        location_string = coffee_soup.find(text=re.compile('Location:'))
        region_string = coffee_soup.find(text=re.compile('Region:'))
        if 'text' in dir(location_string.next_element):
            location_str = location_string.next_element.text.strip()
        else:
            location_str = location_string.next_element.strip()
        if 'text' in dir(region_string.next_element):
            region_str = region_string.next_element.text.strip()
        else:
            region_str = region_string.next_element.strip()
        region = u"{} - {}".format(location_str, region_str)
        if coffee_soup.find(text=re.compile('Tasting Notes')):
            notes_string = coffee_soup.find(text=re.compile('Tasting Notes')).next_element
            notes = [note.strip() for note in notes_string.text.split(',')]
        else:
            notes = []
        price = float(coffee_soup.select_one('span#ProductPrice').text.strip().strip('$'))
        size_container = coffee_soup.select_one('div.swatchBox')
        size_container.select_one('input[checked]')['value']
        active = True
        product_info = coffee_soup.select_one('div.product-info') or coffee_soup.select_one('span.s1')
        if product_info.find('strong'):
            product_info.find('strong').decompose()
        description = product_info.text.strip()
        image_container = coffee_soup.select_one('div#ProductPhoto')
        image_url = 'http:' + image_container.find('img')['src']
        image_content = requests.get(image_url).content
        coffee_data = {
            'name': name,
            'roaster': roaster,
            'description': description,
            'price': price,
            'notes': notes,
            'region': region,
            'active': active,
            'product_page': base_url + product_url,
            'size': size,
            'image': image_content
        }
        coffees_updated, coffees_entered, error_coffees = add_or_update_coffee(
            coffee_data, coffees_updated, coffees_entered, error_coffees)

    logging.info('Matchstick New Results:{} / {}'.format(coffees_entered,
                                                         total_coffees))
    logging.info('Matchstic Updated Results:{} / {}'.format(coffees_updated,
                                                            total_coffees))
    if error_coffees:
        logging.warning('Matchstick Error coffees are: {}'.format(
            error_coffees))
