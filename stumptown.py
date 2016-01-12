from bs4 import BeautifulSoup
import requests
from main import app
# scraping stumptown
def scrape():
    roaster = 'Stumptown'
    stumptown = 'https://www.stumptowncoffee.com/coffee'

    r = requests.get(stumptown)
    soup = BeautifulSoup(r.content)
    # class="product-grid _link"
    coffees_for_sale = soup.find_all('a', {'class':'product-grid _link'})

    for items in coffees_for_sale:
        url = items['href']
        if not 'trio' in url:
            r = requests.get('https://www.stumptowncoffee.com'+url)
            coffee_soup = BeautifulSoup(r.content)
            # product name h1 class="product _title -desktop theme-color js-pdp-title"
            name = coffee_soup.h1.string.strip()
            price = coffee_soup.find_all('span',{'class':'js-pdp-price'})[0].string
            # div class="product _description
            description = coffee_soup.find('div', {'class':'product _description'}).p.string
            notes = coffee_soup.h3.string
            region = coffee_soup.find_all('h4')[1].span.string.strip()[8:]
            if coffee_soup.h6:
                status = 'Sold Out'
            else:
                status = 'Available'
            coffee = Coffee(name=name, roaster=roaster, description=description, price=price, notes =notes, region=region, status=status)
            coffee.put()



