from bs4 import BeautifulSoup
import requests
from models import Coffee
from google.appengine.api import urlfetch
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
        print product_url
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

        coffee = Coffee(name=name, roaster=roaster, description=description,
                        price=price, notes=notes, region=region, status=status,
                        product_page=product_url, size=size)
        coffee.put()
