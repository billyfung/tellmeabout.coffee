from bs4 import BeautifulSoup
from helpers import country_from_name, add_or_update_coffee
from models import Coffee
import requests
import logging
import re

# scraping stumptown
def scrape_stumptown():
    roaster = 'Stumptown'
    stumptown = 'https://www.stumptowncoffee.com/coffee'
    r = requests.get(stumptown)
    soup = BeautifulSoup(r.content, "html.parser")
    # class="product-grid _link"
    coffees_for_sale = soup.find_all('a', {'class':'product-grid _link'})
    # keeping track of how many coffees
    total_coffees = len(coffees_for_sale)
    coffees_entered = 0
    coffees_updated = 0
    error_coffees = []
    for items in coffees_for_sale:
        url = items['href']
        if not 'trio' in url:
            name,price,description,notes,region,active,size = [""]*7
            product_url = 'https://www.stumptowncoffee.com'+url
            logging.info("Getting url: {}".format(url))
            r = requests.get(product_url)
            coffee_soup = BeautifulSoup(r.content, "html.parser")
            # product name h1 class="product _title -desktop theme-color js-pdp-title"
            name = coffee_soup.h1.string.strip()
            try:
                price = float(coffee_soup.find_all('span',{'class':'js-pdp-price'})[0].string)
            except IndexError as e:
                logging.warn("Error while getting price for {} : {}".format(name, e))
            # div class="product _description
            description = coffee_soup.find('div', {'class':'product _description'}).p.string
            try:
                notes = coffee_soup.h3.string.replace('&',',').lower().split(',')
            except:
                pass
            region = country_from_name(name)
            if coffee_soup.h6:
                # its sold out
                active = False
            else:
                active = True
            # size in ounces
            try:
                size = '{} oz'.format(re.findall('\d+', coffee_soup.find('div', {'class':'product _specs'}).find_all('p')[1].string)[0])
            except Exception as e:
                logging.warn("Error while getting size for {} : {}".format(name, e))
            image_url = coffee_soup.select('div.product._image')[0].find('span')['data-src']
            image_content = requests.get(image_url).content
            coffee_data = {'name': name, 'roaster': roaster, 'description': description, 'price': price, 'notes': notes, 'region': region, 'active': active, 'product_page': product_url, 'size': size, 'image': image_content}
            coffees_updated, coffees_entered, error_coffees = add_or_update_coffee(coffee_data, coffees_updated, coffees_entered, error_coffees)
        else:
            total_coffees -= 1

    logging.info('Stumptown New Results:{} / {}'.format(coffees_entered, total_coffees))
    logging.info('Stumptown Updated Results:{} / {}'.format(coffees_updated, total_coffees))
    if error_coffees:
        logging.warning('Stumptown Error coffees are: {}'.format(error_coffees))
