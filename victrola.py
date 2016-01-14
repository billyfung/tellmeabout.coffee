from bs4 import BeautifulSoup
import requests
from models import Coffee
import re

# scraping Victrola roasters


def victrola_scraping():
    roaster = 'Victrola'
    victrola = 'http://www.victrolacoffee.com/collections/all-coffee-offerings'
    r = requests.get(victrola)
    soup = BeautifulSoup(r.content)

    coffees_for_sale = soup.find_all('a', {'class':'product-link'})
    for item in coffees_for_sale:
        name,price,description,notes,region,status,size, product_url = [""]*8
        url = item['href']
        product_url = 'http://www.victrolacoffee.com' + url
        r = requests.get(product_url)
        coffee_soup = BeautifulSoup(r.content)
        name = coffee_soup.h2.string
        if 'Subscription' in name:
            break
        print product_url
        price = coffee_soup.find(itemprop='price').string.strip()[2:]
        print price
        d = coffee_soup.find(itemprop='description').find_all('span')
        if 'Blend' in name:
            # different stuff for blends
            notes = ''
            region = ''
            for x in d:
                description += x.string
        else:
            # sometimes tasting notes just alone
            try:
                notes = coffee_soup(text=re.compile('Flavor:'))[1].string.strip()[8:]
            except:
                notes = coffee_soup.find(text="Tasting Notes").next_element.strip()[2:]
                pass
            try:
                region = coffee_soup(text=re.compile(r'Region:'))[1][8:]
            except:
                region = 'n/a'
                pass
        size = coffee_soup.find('select').option.string[:4]
        coffee = Coffee(name=name, roaster=roaster, description=description,
                price=price, notes=notes, region=region, status=status,
                product_page=product_url, size=size)
        coffee.put()

