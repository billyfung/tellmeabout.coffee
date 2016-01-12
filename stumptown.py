from bs4 import BeautifulSoup
import requests
from models import Coffee
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
            name,price,description,notes,region,status,size = [""]*7
            product_url = 'https://www.stumptowncoffee.com'+url
            r = requests.get(product_url)
            coffee_soup = BeautifulSoup(r.content)
            # product name h1 class="product _title -desktop theme-color js-pdp-title"
            name = coffee_soup.h1.string.strip()
            price = coffee_soup.find_all('span',{'class':'js-pdp-price'})[0].string
            # div class="product _description
            description = coffee_soup.find('div', {'class':'product _description'}).p.string
            try:
                notes = coffee_soup.h3.string
            except:
                pass
            try:
                region = coffee_soup.find_all('h4')[1].span.string.strip()[8:]
            except:
                pass
            if coffee_soup.h6:
                status = 'Sold Out'
            else:
                status = 'Available'
            # size in ounces
            size = coffee_soup.find('div', {'class':'product _specs'}).find_all('p')[1].string.split()[2]
            coffee = Coffee(name=name, roaster=roaster, description=description, 
                price=price, notes=notes, region=region, status=status,
                product_page=product_url, size=size)
            coffee.put()



