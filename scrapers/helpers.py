import string
from models import Coffee

COUNTRY_DICT = {u'japan': u'asia', u'chile': u'south america', u'azerbaijan': u'asia', u'uzbekistan': u'asia', u'djibouti': u'africa', u'french guiana': u'south america', u'cambodia': u'asia', u'guinea-bissau': u'africa', u'virgin island': u'north america', u'hungary': u'europe', u'taiwan': u'asia', u'cyprus': u'europe', u'cook islands': u'oceania', u'bhutan': u'asia', u'bahamas, the': u'north america', u'lithuania': u'europe', u'micronesia': u'oceania', u'united kingdom': u'europe', u'tunisia': u'africa', u'rwanda': u'africa', u'martinique (france)': u'north america', u'argentina': u'south america', u'norway': u'europe', u'sierra leone': u'africa', u'ghana': u'africa', u'falkland islands': u'south america', u'australia': u'oceania', u'mauritania': u'africa', u'zambia': u'africa', u'guatemala': u'north america', u'zimbabwe': u'africa', u'cayman islands (uk)': u'north america', u'belgium': u'europe', u'haiti': u'north america', u'kazakhstan': u'asia', u'burkina faso': u'africa', u'liberia': u'africa', u'kyrgyzstan': u'asia', u'netherlands': u'europe', u'kuwait': u'middle east', u'denmark': u'europe', u'philippines': u'asia', u'senegal': u'africa', u'latvia': u'europe', u'namibia': u'africa', u'chad': u'africa', u'bosnia/herzegovina': u'europe', u'switzerland': u'europe', u'anguilla (uk)': u'north america', u'guadeloupe (france)': u'north america', u'bulgaria': u'europe', u'jamaica': u'north america', u'albania': u'europe', u'samoa': u'oceania', u'colombia': u'south america', u'lebanon': u'middle east', u'malaysia': u'asia', u'mozambique': u'africa', u'greece': u'europe', u'nicaragua': u'north america', u'niger': u'africa', u'aruba (netherlands)': u'north america', u'canada': u'north america', u'afghanistan': u'asia', u'qatar': u'middle east', u'peru': u'south america', u'palau': u'oceania', u'turkmenistan': u'asia', u'equatorial guinea': u'africa', u'sudan': u'africa', u'guinea': u'africa', u'panama': u'north america', u'nepal': u'asia', u'central african republic': u'africa', u'luxembourg': u'europe', u'somalia': u'africa', u'iceland': u'europe', u'croatia': u'europe', u'nauru': u'oceania', u'venezuela': u'south america', u'brunei': u'asia', u'korea': u'asia', u'iran': u'middle east', u'united arab emirates': u'middle east', u'guyana': u'south america', u'saint kitts and nevis': u'north america', u'sri lanka': u'asia', u'paraguay': u'south america', u'china': u'asia', u'armenia': u'asia', u'kiribati': u'oceania', u'faeroe islands': u'europe', u'belize': u'north america', u'british virgin islands (uk)': u'north america', u'bangladesh': u'asia', u'ukraine': u'asia', u'libya': u'africa', u'trinidad and tobago': u'north america', u'gambia': u'africa', u'finland': u'europe', u'macedonia': u'europe', u'russia': u'asia', u'mauritius': u'africa', u'marshall islands': u'oceania', u'niue': u'oceania', u'burma (myanmar)': u'asia', u'dominican republic': u'north america', u'pakistan': u'asia', u'romania': u'europe', u'seychelles': u'africa', u'czech republic': u'europe', u'egypt': u'africa', u'papua new guinea': u'asia', u'united states': u'north america', u'austria': u'europe', u'congo': u'africa', u'mongolia': u'asia', u'ivory coast': u'africa', u'thailand': u'asia', u'angola': u'africa', u'new zealand': u'oceania', u'fiji': u'oceania', u'comoros': u'africa', u'turkey': u'asia', u'andorra': u'europe', u'madagascar': u'africa', u'iraq': u'middle east', u'portugal': u'europe', u'uruguay': u'south america', u'france': u'europe', u'slovakia': u'europe', u'gibraltar': u'europe', u'ireland': u'europe', u'laos': u'asia', u'nigeria': u'africa', u'bolivia': u'south america', u'malawi': u'africa', u'ecuador': u'south america', u'israel': u'middle east', u'south georgia': u'south america', u'swaziland': u'africa', u'western sahara': u'africa', u'india': u'asia', u'tajikistan': u'asia', u'togo': u'africa', u'jordan': u'middle east', u'macau': u'asia', u'oman': u'middle east', u'spain': u'europe', u'sao tome and principe': u'africa', u'georgia': u'asia', u'morocco': u'africa', u'sweden': u'europe', u'gabon': u'africa', u'mali': u'africa', u'grenada': u'north america', u'yemen': u'middle east', u'hong kong': u'asia', u'tanzania': u'africa', u'puerto rico (us)': u'north america', u'estonia': u'europe', u'mexico': u'north america', u'monsterrat (uk)': u'north america', u'san marino': u'europe', u'lesotho': u'africa', u'belarus': u'europe', u'uganda': u'africa', u'burundi': u'africa', u'kenya': u'africa', u'botswana': u'africa', u'italy': u'europe', u'algeria': u'africa', u'south africa': u'africa', u'bahrain': u'middle east', u'cuba': u'north america', u'malta': u'europe', u'ethiopia': u'africa', u'vanuatu': u'oceania', u'antigua and barbuda': u'north america', u'cameroon': u'africa', u'benin': u'africa', u'brazil': u'south america', u'singapore': u'asia', u'solomon islands': u'oceania', u'tuvalu': u'oceania', u'saudi arabia': u'middle east', u'costa rica': u'north america', u'slovenia': u'europe', u'honduras': u'north america', u'germany': u'europe', u'syria': u'middle east', u'vatican city': u'europe', u'dominica': u'north america', u'suriname': u'south america', u'eritrea': u'africa', u'tonga': u'oceania', u'maldives': u'asia', u'el salvador': u'north america', u'poland': u'europe', u'indonesia': u'asia', u'cape verde': u'africa', u'vietnam': u'asia', u'monaco': u'europe', u'barbados': u'north america'}

def country_from_name(name):
    countrydict = COUNTRY_DICT
    is_country_in_here = [x for x in countrydict.keys() if x in name.lower()]
    country = ''
    if is_country_in_here:
        country = string.capwords(is_country_in_here[0])
    return country


def add_or_update_coffee(coffee_data, coffees_updated, coffees_entered, error_coffees):
    old_coffees = Coffee.query(Coffee.name == coffee_data['name'], Coffee.roaster == coffee_data['roaster'], Coffee.active==True).fetch()
    if old_coffees:
        if len(old_coffees) > 1:
            logging.warning("Query for coffee name: {}, roaster: {} returned {} results. Result are {}".format(coffee_data['name'], coffee_data['roaster'], len(old_coffees), old_coffees))
        for key, value in coffee_data.iteritems():
            setattr(old_coffees[0], key, value)
        try: 
            old_coffees[0].put()
            coffees_updated +=1
        except AttributeError:
            # error putting the coffee into the datastore
            error_coffees.append(coffee_data['product_page'])
    else: 
        coffee=Coffee(**coffee_data)
        try:
            coffee.put()
            coffees_entered +=1
        except AttributeError:
            # error putting the coffee into the datastore
            error_coffees.append(coffee_data['product_page'])
    return [coffees_updated, coffees_entered, error_coffees]
