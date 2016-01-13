from bs4 import BeautifulSoup
import requests
from models import Coffee

roaster = 'Intelligentsia'
intelli = 'http://www.intelligentsiacoffee.com/products/coffee'
r = requests.get(intelli)
soup = BeautifulSoup(r.content)

# each coffee under class="grid_4 node node-type-product-coffee node-teaser build-mode-teaser""
coffees_for_sale = soup.find_all('div', {'class':'node-type-product-coffee'})
for item in coffees_for_sale:
    product_url = 'http://www.intelligentsiacoffee.com'+item.a['href']
    notes_list = item.p.contents
    notes = noteslist[2]+', '+noteslist[4]+', '+noteslist[6]
    name = item.find('div',{'class':'productListingDescBox'}).strong.string
    r = requests.get(product_url)
    coffee_soup = BeautifulSoup(r.content)
    price = coffee_soup.find('p',{'class':'coffeeDetailPrice'}).em.string[1:]
    size = coffee_soup.find('p',{'class':'coffeeDetailPrice'}).em.next_sibling.strip()[2:]
    region = coffee_soup.find(text='Region').next_element.string + ', ' + coffee_soup.find(text='Country').next_element.string
    description = coffee_soup.find('div', {'class':'product-body'}).string


