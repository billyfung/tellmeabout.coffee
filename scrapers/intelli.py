from bs4 import BeautifulSoup
import requests
from models import Coffee
from google.appengine.api import urlfetch
import logging


urlfetch.set_default_fetch_deadline(45)


def scrape_intelli():
    roaster = 'Intelligentsia'
    intelli = 'http://www.intelligentsiacoffee.com/products/coffee'
    r = requests.get(intelli)
    soup = BeautifulSoup(r.content)

    # each coffee under class="grid_4 node node-type-product-coffee node-teaser build-mode-teaser""
    coffees_for_sale = soup.find_all('div', {'class': 'node-type-product-coffee'})
    for item in coffees_for_sale:
        name, price, description, notes, region, status, size, product_url = [""] * 8
        product_url = 'http://www.intelligentsiacoffee.com' + item.a['href']
        notes_list = item.p.contents
        notes = notes_list[2] + ', ' + notes_list[4] + ', ' + notes_list[6]
        name = item.find('div', {'class': 'productListingDescBox'}).strong.string
        r = requests.get(product_url)
        coffee_soup = BeautifulSoup(r.content)
        try:
            price = coffee_soup.find('p', {'class': 'coffeeDetailPrice'}).em.string[1:]
            # size gives value + unit
            size = coffee_soup.find('p', {'class': 'coffeeDetailPrice'}).em.next_sibling.strip()[2:]
            status = "Available"
        except:
            # if 'OUT' in coffee_soup.find('p', {'class': 'coffeeDetailPrice'}).string:
            status = 'Sold Out'
            pass
        blend_or_origin = coffee_soup.find_all('p', {'class': 'coffeeDetailExtraInfoHeader'})
        blend_or_origin = [x.string for x in blend_or_origin]
        # region + country
        try:
            region = coffee_soup.find(text='Region').next_element.string + ', ' + coffee_soup.find(
                text='Country').next_element.string
        except:
            if 'Blend' in blend_or_origin:
                region = 'Blend'
            pass
        description = coffee_soup.find('div', {'class': 'product-body'}).string
        coffee_data = {'name':name, 'roaster':roaster, 'description':description, 'price':price, 'notes':notes, 'region':region, 'status':status, 'product_page':product_url, 'size':size}
        old_coffees = Coffee.query(Coffee.name == coffee_data['name'], Coffee.roaster==coffee_data['roaster'], Coffee.region==coffee_data['region']).fetch()
        if old_coffees:
            if len(old_coffees)>1:
                logging.warning("Query for coffee name:{}, roaster:{}, region:{} returned {} results. Results are {}".format(coffee_data['name'], coffee_data['roaster'], coffee_data['region'], len(old_coffees), old_coffees))
            for key, value in coffee_data.iteritems():
                setattr(old_coffees[0], key,value)
            old_coffees[0].put
        else:
            coffee=Coffee(**coffee_data)
            coffee.put()
