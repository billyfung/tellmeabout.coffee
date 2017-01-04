from bs4 import BeautifulSoup
from helpers import country_from_name, add_or_update_coffee
from models import Coffee
import requests
import logging
import re

# scraping heart
def scrape_heart():
    roaster = 'Heart'
    heart_beans = 'https://www.heartroasters.com/collections/beans'
    heart_url = 'https://www.heartroasters.com'

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
        coffee_soup = BeautifulSoup(r.content, "html.parser")
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
        coffees_updated, coffees_entered, error_coffees = add_or_update_coffee(coffee_data, coffees_updated, coffees_entered, error_coffees)

    logging.info('Heart New Results:{} / {}'.format(coffees_entered, total_coffees))
    logging.info('Heart Updated Results:{} / {}'.format(coffees_updated, total_coffees))
    if error_coffees:
        logging.warning('Heart Error coffees are: {}'.format(error_coffees))
