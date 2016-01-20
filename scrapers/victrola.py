from bs4 import BeautifulSoup
import requests
from models import Coffee
import re
import logging

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
        name,description,notes,region,status,size, product_url = [""]*7
        price = int()
        url = item['href']
        product_url = 'http://www.victrolacoffee.com' + url
        logging.info("Getting url: {}".format(url))
        r = requests.get(product_url)
        coffee_soup = BeautifulSoup(r.content)
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
            status = 'Available'
        except:
            status = "Sold Out"
        d = coffee_soup.find(itemprop='description').find_all('span')
        if 'Blend' in name:
            # different stuff for blends
            notes = []
            region = ''
            for x in d:
                description += x.string
        else:
            # sometimes tasting notes just alone
            try:
                notes = coffee_soup(text=re.compile('Flavor:'))[1].string.strip()[8:].rstrip(',').lower().split(',')
            except:
                notes = coffee_soup.find(text="Tasting Notes").next_element.strip()[2:].rstrip(',').lower().split(',')
                pass
            try:
                region = coffee_soup(text=re.compile(r'Region:'))[1][8:]
            except:
                region = 'n/a'
                pass
        image_url = coffee_soup.find('ul', {'class': 'bx-slider'}).find('img')['src']
        image_content = requests.get("http:{}".format(image_url)).content
        coffee_data = {'name':name, 'roaster':roaster, 'description':description, 'price':price, 'notes':notes, 'region':region, 'status':status, 'product_page':product_url, 'size':size, 'image': image_content}
        old_coffees = Coffee.query(Coffee.name == coffee_data['name'], Coffee.roaster==coffee_data['roaster'], Coffee.region==coffee_data['region']).fetch()
        # check if coffee already in db
        if old_coffees:
            if len(old_coffees)>1:
                logging.warning("Query for coffee name:{}, roaster:{}, region:{} returned {} results. Results are {}".format(coffee_data['name'], coffee_data['roaster'], coffee_data['region'], len(old_coffees), old_coffees))
            for key, value in coffee_data.iteritems():
                setattr(old_coffees[0], key,value)
            try:
                old_coffees[0].put()
                coffees_updated += 1
            except:
                error_coffees.append(coffee_data['product_page'])
        else:
            coffee=Coffee(**coffee_data)
            try:
                coffee.put()
                coffees_entered +=1
            except:
                error_coffees.append(coffee_data['product_page'])
    # display results of scrape in logs
    logging.info('Victrola New Results:{} / {}'.format(coffees_entered, total_coffees))
    logging.info('Victrola Updated Results:{} / {}'.format(coffees_updated, total_coffees))
    logging.info(error_coffees)
