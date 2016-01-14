from bs4 import BeautifulSoup
import requests
from models import Coffee
import re

# scraping Victrola roasters

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
    price = coffee_soup.find(itemprop='price').string.strip()[2:]
    d = coffee_soup.find(itemprop='description').find_all('span')
    if 'Blend' in name:
        # different stuff for blends
        notes = ''
        region = ''
        for x in d:
            description += x.string
    else:
        # sometimes tasting notes just alone
        tasting_notes = soup.find(text="Tasting Notes").next_element.strip()
        if not tasting_notes:
            # checking to see if empty
            notes = coffee_soup.find(text='Flavor:').string
        else:
            notes = tasting_notes[2:]
        try:
            region = d(text=re.compile(r'Region:'))[0][8:]
        except:
            pass
    size = coffee_soup.find('select').option.string[:4]

