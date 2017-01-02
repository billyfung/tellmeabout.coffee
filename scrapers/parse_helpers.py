from bs4 import BeautifulSoup
import requests

def return_coffees(initial_url, selector):
    soup = BeautifulSoup(requests.get(initial_url).content, "html.parser")
    coffees_for_sale = soup.select(selector)
    return coffees_for_sale

def remove_ignored(coffees, selector, ignored):
    final_coffees = []
    for coffee in coffees:
        if not any(word in coffee.select_one(selector).string for word in ignored):
            final_coffees.append(coffee)
    return final_coffees

def get_single_coffee(url, base_url, price_selector, description_selector, name_selector, image_selector):
    soup = BeautifulSoup(requests.get(base_url + url).content, "html.parser")
    price = float(soup.select_one(price_selector).text)
    description = soup.select_one(description_selector).text
    name = soup.select_one(name_selector).text
    return {
            "coffee_soup": soup,
            "price": price,
            "description": description,
            "name": name 
    }
