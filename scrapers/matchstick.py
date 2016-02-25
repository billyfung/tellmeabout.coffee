from bs4 import BeautifulSoup
from models import Coffee
from helpers import add_or_update_coffee
import requests
import logging


def scrape_matchstick():
    roaster = "Matchstick"
    r = requests.get('http://www.matchstickcoffee.com/coffee/')
    soup = BeautifulSoup(r.content)
    coffees_for_sale = soup.find_all('div', {'class':'type-post'})
    total_coffees = len(coffees_for_sale)
    coffees_entered = 0
    coffees_updated = 0
    error_coffees = []
    for item in coffees_for_sale:
        name,description,notes,region,active,size, product_url = [""]*7
        price = float()
        url = item.a['href']   
        region = item.find(text='Origin:').next_element.strip()
        noteloc = item.find(text='Notes:').next_element
        notes = [x.strip() for x in noteloc.split(',')]
        price_and_size = noteloc.next_element.next_element.text.split(' / ')
        price = float(price_and_size[0][1:])
        size = price_and_size[1]
        active = True
        coffee_soup = BeautifulSoup(requests.get(url).content)
        name = coffee_soup.h1.string
        # not sure if the descriptions here matter at all
        description = coffee_soup.find(text='Notes:').next_element.next_element.next_element.next_element.next_element.next_element.next_element
        # url may had unicode stuff
        image_url = item.find('img')['src']
        image_content = requests.get(image_url).content
        coffee_data = {'name':name, 'roaster':roaster, 'description':description, 'price':price, 'notes':notes, 'region':region, 'active':active, 'product_page':product_url, 'size':size, 'image': image_content}
        coffees_updated, coffees_entered, error_coffees = add_or_update_coffee(coffee_data, coffees_updated, coffees_entered, error_coffees)
    
    logging.info('Matchstick New Results:{} / {}'.format(coffees_entered, total_coffees)) 
    logging.info('Matchstic Updated Results:{} / {}'.format(coffees_updated, total_coffees))
    if error_coffees:
        logging.warning('Matchstick Error coffees are: {}'.format(error_coffees))
