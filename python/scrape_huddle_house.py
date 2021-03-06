from bs4 import BeautifulSoup
from os.path import isfile
from time import sleep
from waffle_scraper import read_json, write_json, fetch_url, fetch_test_url

is_test = True
sleep_time = 0 if is_test else 5
hh_base_url = 'https://locations.huddlehouse.com/'
huddle_houses_json = "huddle_houses.json"


def fetch_locations_page(regions_url):
    if is_test:
        return fetch_test_url(regions_url, 'hh_us.html')
    else:
        return fetch_url(regions_url)


def fetch_state_page(state_url):
    if is_test:
        return fetch_test_url(hh_base_url + 'ga', 'hh_ga.html')
    else:
        return fetch_url(state_url)


def fetch_city_page(city_url):
    if is_test:
        return fetch_test_url(hh_base_url + 'ga/milledgeville', 'hh_milledgeville.html')
    else:
        return fetch_url(city_url)


def fetch_location_page(location_url):
    if is_test:
        return fetch_test_url(hh_base_url + 'ga/helen/8428-s-main-street', 'hh_helen.html')
    else:
        return fetch_url(location_url)


def fetch_state_links(regions_url):
    html = fetch_locations_page(regions_url)
    bs = BeautifulSoup(html, 'html.parser')
    bs_state_list_items = bs.find_all('li', {'class': 'Directory-listItem'})
    bs_state_links = list(map(lambda c: c.find('a'), bs_state_list_items))
    return list(map(lambda x: x['href'], bs_state_links))


def fetch_locations(link):
    locations = []
    url = hh_base_url + link
    link_components = link.split('/')
    if len(link_components) == 1:
        locations = fetch_state(url)
    elif len(link_components) == 2:
        locations = fetch_city(url)
    elif len(link_components) == 3:
        locations = [fetch_location(url)]
    return locations


def fetch_state(state_url):
    locations = []
    html = fetch_state_page(state_url)
    bs = BeautifulSoup(html, 'html.parser')
    bs_state_list_items = bs.find_all('li', {'class': 'Directory-listItem'})
    bs_state_links = list(map(lambda c: c.find('a'), bs_state_list_items))
    links = list(map(lambda x: x['href'], bs_state_links))
    for link in links:
        url = hh_base_url + link
        link_components = link.split('/')
        if len(link_components) == 2:
            locations.extend(fetch_city(url))
        elif len(link_components) == 3:
            locations.append(fetch_location(url))
    return locations


def fetch_city(city_url):
    locations = []
    html = fetch_city_page(city_url)
    bs = BeautifulSoup(html, 'html.parser')
    bs_city_list_items = bs.find_all('li', {'class': 'Directory-listTeaser'})
    bs_city_links = list(map(lambda c: c.find('a', {'class': 'Teaser-titleLink'}), bs_city_list_items))
    links = list(map(lambda x: x[3:] if x.startswith('../') else x, map(lambda x: x['href'], bs_city_links)))
    for link in links:
        url = hh_base_url + link
        locations.append(fetch_location(url))
    return locations


def fetch_location(location_url):
    html = fetch_location_page(location_url)
    bs = BeautifulSoup(html, 'html.parser')

    bs_link = bs.find('link', {'rel': 'canonical'})
    link = '/' + bs_link['href'][len(hh_base_url):]

    bs_nap_address = bs.find('div', {'class': 'NAP-address'})

    bs_city = bs_nap_address.find('meta', {'itemprop': 'addressLocality'})
    name = bs_city['content']

    bs_street_address = bs_nap_address.find('meta', {'itemprop': 'streetAddress'})
    street = bs_street_address['content']

    bs_state = bs_nap_address.find('abbr', {'itemprop': 'addressRegion'})
    state_code = bs_state.get_text().strip()

    bs_zip = bs_nap_address.find('span', {'itemprop': 'postalCode'})
    zip_code = bs_zip.get_text().strip()

    bs_country = bs_nap_address.find('abbr', {'itemprop': 'addressCountry'})
    country_code = bs_country.get_text().strip()

    address = [street, name + ", " + state_code + " " + zip_code + " " + country_code]

    bs_lat = bs_nap_address.find('meta', {'itemprop': 'latitude'})
    bs_lon = bs_nap_address.find('meta', {'itemprop': 'longitude'})
    coords = [float(bs_lat['content']), float(bs_lon['content'])]

    location = {'link': link, 'name': name, 'address': address, 'coords': coords}
    print(location)
    sleep(sleep_time)
    return location


state_links = fetch_state_links(hh_base_url)

if isfile(huddle_houses_json):
    huddle_houses = read_json(huddle_houses_json)
else:
    huddle_houses = {'states': {}}
    for state_link in state_links:
        state = state_link[:2].upper()
        huddle_houses['states'][state] = {'is_complete': False}

for state_link in state_links:
    state = state_link[:2].upper()
    if not huddle_houses['states'][state]['is_complete']:
        huddle_houses['states'][state]['locations'] = fetch_locations(state_link)
        huddle_houses['states'][state]['is_complete'] = True
        write_json(huddle_houses, huddle_houses_json)
