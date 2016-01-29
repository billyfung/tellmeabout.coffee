from bs4 import BeautifulSoup
from helpers import country_from_name, add_or_update_coffee
from models import Coffee
import requests
import logging
import re
# scraping Victrola roasters


def scrape_victrola():
    roaster = 'Victrola'
    victrola = 'http://www.victrolacoffee.com/collections/all-coffee-offerings'
    r = requests.get(victrola)
    soup = BeautifulSoup(r.content, "html.parser")
    coffees_for_sale = soup.find_all('a', {'class':'product-link'})
    total_coffees = len(coffees_for_sale)
    coffees_entered = 0
    coffees_updated = 0
    error_coffees = []
    for item in coffees_for_sale:
        name,description,notes,region,active,size, product_url = [""]*7
        price = int()
        url = item['href']
        product_url = 'http://www.victrolacoffee.com' + url
        logging.info("Getting url: {}".format(url))
        r = requests.get(product_url)
        coffee_soup = BeautifulSoup(r.content, "html.parser")
        name = coffee_soup.h2.string
        if 'Subscription' in name:
            total_coffees-=1
            continue
        if coffee_soup.find('div', {'class': 'select single'}).find('label').text != 'Size':
            total_coffees-=1
            continue
        try:
            size = coffee_soup.find('select').option.string[:4]
        except:
            logging.info('Cannot find size for {}'.format(name))
            continue
        try:
            price = float(coffee_soup.find(itemprop='price').string.strip()[2:])
            active = True
        except:
            # its sold out
            active = False
        d = coffee_soup.find('h4', {'class':'mobile'}).next_siblings
        if 'Blend' in name:
            # different stuff for blends
            notes = []
            region = 'Blend'
            for x in d:
                description += x.string.strip()
        else:
            # sometimes tasting notes just alone
            try:
                notes = coffee_soup(text=re.compile('Flavor:'))[1].string.strip()[8:].rstrip(',').lower().split(',')
            except:
                notes = coffee_soup.find(text="Tasting Notes").next_element.strip()[2:].rstrip(',').lower().split(',')
                pass
            region = country_from_name(name)
        image_url = coffee_soup.find('ul', {'class': 'bx-slider'}).find('img')['src']
        image_content = requests.get("http:{}".format(image_url)).content
        coffee_data = {'name':name, 'roaster':roaster, 'description':description, 'price':price, 'notes':notes, 'region':region, 'active':active, 'product_page':product_url, 'size':size, 'image': image_content}
        coffees_updated, coffees_entered, error_coffees = add_or_update_coffee(coffee_data, coffees_updated, coffees_entered, error_coffees)

    logging.info('Victrola New Results:{} / {}'.format(coffees_entered, total_coffees))
    logging.info('Victrola Updated Results:{} / {}'.format(coffees_updated, total_coffees))
    if error_coffees:
        logging.warning('Victrola Error coffees are: {}'.format(error_coffees))
