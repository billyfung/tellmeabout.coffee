from bs4 import BeautifulSoup
from helpers import COUNTRY_DICT, country_from_name
from models import Coffee
import requests
import logging
import re

# scraping heart
def scrape_heart():
    countrydict = COUNTRY_DICT
    roaster = 'Heart'
    heart_beans = 'http://www.heartroasters.com/collections/beans'
    heart_url = 'http://www.heartroasters.com'

    r = requests.get(heart_beans)
    soup = BeautifulSoup(r.content, "html.parser")
    all_coffees_for_sale = soup.find_all('a', {'class':'grid__image'})
    all_coffee_links = []
    for coffee in all_coffees_for_sale:
        if not 'Subscription' in coffee.find('img')['alt']:
            all_coffee_links.append("{}{}".format(heart_url, coffee['href']))
    total_coffees = len(all_coffee_links)
    coffees_entered = 0
    coffees_updated = 0
    error_coffees = []
    for url in all_coffee_links:
        name,price,description,notes,region,active,size = [""] * 7
        logging.info("Getting url: {}".format(url))
        r = requests.get(url)
        coffee_soup = BeautifulSoup(r.content)
        blend = False
        active = True
        name = coffee_soup.h1.text.strip()
        if 'blend' in name.lower():
            blend = True
        size_price = coffee_soup.find('option').text
        size = size_price.split(" - ")[0]
        if 'Sold Out' in size_price:
            active = False
            price = 0
        else:
            price = float(size_price.split(" - ")[1].replace('USD', '').replace('$', ''))
        description = coffee_soup.find('div', {'class':'tab-content small'}).find('div',{'id': 'tab1'}).text.encode('utf-8').strip()
        notes = coffee_soup.find('p',{'class': 'small uppercase flavors'}).text.split(',')
        if not blend:
            region = country_from_name(name)
            # region = coffee_soup.find('div', {'class':'tab-content small'}).find('div',{'id': 'tab1'}).p.text.replace(u'Location:\xa0', '').replace('Location:', '').encode('utf-8')
        image_url = "http:{}".format(coffee_soup.select('div.slide')[0].find('img')['src'])
        image_content = requests.get(image_url).content
        coffee_data = {'name': name, 'roaster': roaster, 'description': description, 'price': price, 'notes': notes, 'region': region, 'active': active, 'product_page': url, 'size': size, 'image': image_content}
        old_coffees = Coffee.query(Coffee.name == coffee_data['name'], Coffee.roaster == coffee_data['roaster'], Coffee.region == coffee_data['region'], Coffee.active==True).fetch()
        if old_coffees:
            if len(old_coffees) > 1:
                logging.warning("Query for coffee name: {}, roaster: {}, region: {} returned {} results. Result are {}".format(coffee_data['name'], coffee_data['roaster'], coffee_data['region'], len(old_coffees), old_coffees))
            for key, value in coffee_data.iteritems():
                setattr(old_coffees[0], key, value)
            try: 
                old_coffees[0].put()
                coffees_updated +=1
            except:
                error_coffees.append(coffee_data['product_page'])
        else: 
            coffee=Coffee(**coffee_data)
            try:
                coffee.put()
                coffees_entered +=1
            except:
                error_coffees.append(coffee_data['product_page'])

    logging.info('Heart New Results:{} / {}'.format(coffees_entered, total_coffees))
    logging.info('Heart Updated Results:{} / {}'.format(coffees_updated, total_coffees))
    logging.info('Error coffees are: ')
    logging.info(error_coffees)
