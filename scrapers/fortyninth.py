from bs4 import BeautifulSoup
from models import Coffee
from helpers import add_or_update_coffee
import requests
import logging


def scrape_fortyninth():
    roaster = '49th Parallel'
    base_url = 'http://49thcoffee.com/collections/coffee'
    r = requests.get(base_url)
    soup = BeautifulSoup(r.content, "html.parser")
    coffees_for_sale = soup.find_all('li', {'class': 'product-listing'})
    total_coffees = len(coffees_for_sale)
    coffees_entered = 0
    coffees_updated = 0
    error_coffees = []
    ignored = ['Subscription']
    for item in coffees_for_sale:
        name, description, notes, region, active, size, product_url = [""] * 7
        price = float()
        name = item.h1.string
        if any(word in name for word in ignored):
            total_coffees -= 1
        else:
            url = item.a['href']
            product_url = 'http://49thcoffee.com' + url
            logging.info("Getting url: {}".format(product_url))
            r = requests.get(product_url)
            coffee_soup = BeautifulSoup(r.content, "html.parser")
            # logging.info("Title: {}".format(coffee_soup.title))
            details = coffee_soup.find('div', itemprop='description')
            d = coffee_soup.find_all('p', {'class': 'p1'})
            if d == []:
                try:
                    description = details.p.string
                except AttributeError:
                    description = details.span.string
            else:
                description = d[0].string
            notes = details.h3.string.lower()
            notes = notes.split(' // ')
            region = coffee_soup.find(
                'li', {'class': 'product-detail-country'}).string.split()[1]
            size = item.find('data', {'class': 'product-size'}).string.strip()
            price = float(
                item.find('data', {'class': 'product-price'}).string[1:])
            active = True
            image_url = 'https:' + coffee_soup.find(
                'meta', itemprop='image')['content']
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

    logging.info('49 Parallel New Results:{} / {}'.format(coffees_entered,
                                                          total_coffees))
    logging.info('49 Parallel  Updated Results:{} / {}'.format(coffees_updated,
                                                               total_coffees))
    if error_coffees:
        logging.warning('49 Paralell Error coffees are: {}'.format(
            error_coffees))
