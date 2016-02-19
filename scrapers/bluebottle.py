from bs4 import BeautifulSoup
from models import Coffee
from helpers import country_from_name, add_or_update_coffee
import requests
import logging

# scraping Blue Bottle roasters

def scrape_bluebottle():
    roaster = 'Blue Bottle'
    bluebottle = 'https://bluebottlecoffee.com/store/coffee'
    r = requests.get(bluebottle)
    soup = BeautifulSoup(r.content, "html.parser")
    coffees_for_sale = soup.find_all('h2', {'class':'f5 lh-title man'})
    total_coffees = len(coffees_for_sale)
    coffees_entered = 0
    coffees_updated = 0
    error_coffees = []
    ignored = ['Box', 'Kit', 'Subscriptions', 'at Home']
    for item in coffees_for_sale:
        name,description,notes,region,active,size, product_url = [""]*7
        price = float()
        name = item.string
        if any(word in name for word in ignored):
            total_coffees -= 1
        else:
            url = item.a['href']
            product_url = 'https://bluebottlecoffee.com' + url
            logging.info("Getting url: {}".format(url))
            r = requests.get(product_url)
            coffee_soup = BeautifulSoup(r.content, "html.parser")
            active = True
            price = float(coffee_soup.find('span', {'class':'js-variant-price'}).string[1:])
            description = coffee_soup.find('p', {'class':'spec-overview'}).string
            notes = coffee_soup.p.string.lower().split(',')
                # only works for not single origin
            region = country_from_name(name) 
            try:
                details = coffee_soup.find('p', {'class':'spec-details'}).contents[0].strip()
                if country_from_name(details) != '':
                    region = details
            except AttributeError:
                # if it's an espresso, then it's okay to not have region
                if 'Espresso' in name:
                    region = ""        
            size = coffee_soup.find('label', {'for':'cart_item_quantity'}).string[10:-1].replace('Bag', '').strip()
            image_url = coffee_soup.img['src']
            image_content = requests.get(image_url).content
            coffee_data = {'name': name, 'roaster': roaster, 'description': description, 'price': price, 'notes': notes, 'region': region, 'active': active, 'product_page': product_url, 'size': size, 'image': image_content}
            coffees_updated, coffees_entered, error_coffees = add_or_update_coffee(coffee_data, coffees_updated, coffees_entered, error_coffees)

    logging.info('Blue Bottle New Results:{} / {}'.format(coffees_entered, total_coffees))
    logging.info('Blue Bottle Updated Results:{} / {}'.format(coffees_updated, total_coffees))
    if error_coffees:
        logging.warning('Blue Bottle Error coffees are: {}'.format(error_coffees))



