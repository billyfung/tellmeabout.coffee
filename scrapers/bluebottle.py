from bs4 import BeautifulSoup
from models import Coffee
from helpers import COUNTRY_DICT, country_from_name
import requests
import logging

# scraping Blue Bottle roasters

def scrape_bluebottle():
    countrydict = COUNTRY_DICT
    roaster = 'Blue Bottle'
    bluebottle = 'https://bluebottlecoffee.com/store/coffee'
    r = requests.get(bluebottle)
    soup = BeautifulSoup(r.content)
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
            coffee_soup = BeautifulSoup(r.content)
            active = True
            price = float(coffee_soup.find('span', {'class':'js-variant-price'}).string[1:])
            description = coffee_soup.find('p', {'class':'spec-overview'}).string
            notes = coffee_soup.p.string.lower().split(',')
            try:
                # only works for not single origin
                region = coffee_soup.find('p', {'class':'spec-details'}).contents[0].strip()
            except AttributeError:
                # for single origin, region is in name [country][region]
                # otherwise if espresso, no region
                # grab only country for now
                if 'Espresso' in name:
                    region = ""
                else:
                    # not sure how to grab just the country right now
                    region = country_from_name(name)   
            size = coffee_soup.find('label', {'for':'cart_item_quantity'}).string[10:-1].replace('Bag', '').strip()
            image_url = coffee_soup.img['src']
            image_content = requests.get(image_url).content
            coffee_data = {'name': name, 'roaster': roaster, 'description': description, 'price': price, 'notes': notes, 'region': region, 'active': active, 'product_page': product_url, 'size': size, 'image': image_content}
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

    logging.info('Blue Bottle New Results:{} / {}'.format(coffees_entered, total_coffees))
    logging.info('Blue Bottle Updated Results:{} / {}'.format(coffees_updated, total_coffees))
    logging.info('Error coffees are: ')
    logging.info(error_coffees)




