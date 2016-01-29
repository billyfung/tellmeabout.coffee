from bs4 import BeautifulSoup
import requests
from models import Coffee
from helpers import add_or_update_coffee
from google.appengine.api import urlfetch
import logging


def scrape_intelli():
    urlfetch.set_default_fetch_deadline(10)
    roaster = 'Intelligentsia'
    intelli = 'http://www.intelligentsiacoffee.com/products/coffee'
    r = requests.get(intelli)
    soup = BeautifulSoup(r.content, "html.parser")

    # each coffee under class="grid_4 node node-type-product-coffee node-teaser build-mode-teaser""
    coffees_for_sale = soup.find_all('div', {'class': 'node-type-product-coffee'})
    # there are duplicates, must check
    seen = set()
    uniq_coffees_for_sale = []
    for x in coffees_for_sale:
        if x not in seen:
            uniq_coffees_for_sale.append(x)
            seen.add(x)
    total_coffees = len(uniq_coffees_for_sale)
    coffees_entered = 0
    coffees_updated = 0
    error_coffees = []
    for item in uniq_coffees_for_sale:
        name, description, notes, region, active, size, product_url = [""] * 7
        price = int()
        product_url = 'http://www.intelligentsiacoffee.com' + item.a['href']
        logging.info("Getting url: {}".format(product_url))
        notes_list = item.p.contents
        notes = [notes_list[2].strip().lower(),notes_list[4].strip().lower(),notes_list[6].strip().lower()]
        name = item.find('div', {'class': 'productListingDescBox'}).strong.string
        r = requests.get(product_url)
        coffee_soup = BeautifulSoup(r.content, "html.parser")
        try:
            price = float(coffee_soup.find('p', {'class': 'coffeeDetailPrice'}).em.string[1:])
            # size gives value + unit
            size = coffee_soup.find('p', {'class': 'coffeeDetailPrice'}).em.next_sibling.strip()[2:]
            active = True
        except:
            # if 'OUT' in coffee_soup.find('p', {'class': 'coffeeDetailPrice'}).string:
            # its sold out
            active = False
            pass
        blend_or_origin = coffee_soup.find_all('p', {'class': 'coffeeDetailExtraInfoHeader'})
        blend_or_origin = [x.string for x in blend_or_origin]
        # region + country
        try:
            region = coffee_soup.find(text='Country').next_element.string 
        except:
            if 'Blend' in blend_or_origin:
                region = 'Blend'
            pass
        image_url = coffee_soup.find('div', {'class': 'productPhotoSlide'}).find('img')['src']
        image_blob = requests.get(image_url).content
        description = coffee_soup.find('div', {'class': 'product-body'}).string
        coffee_data = {'name':name, 'roaster':roaster, 'description':description, 'price':price, 'notes':notes, 'region':region, 'active':active, 'product_page':product_url, 'size':size, 'image': image_blob}
        coffees_updated, coffees_entered, error_coffees = add_or_update_coffee(coffee_data, coffees_updated, coffees_entered, error_coffees)

    logging.info('Intelligentsia New Results:{} / {}'.format(coffees_entered, total_coffees))
    logging.info('Intelligentsia Updated Results:{} / {}'.format(coffees_updated, total_coffees))
    if error_coffees:
        logging.warning('Intelligensia Error coffees are: {}'.format(error_coffees))
