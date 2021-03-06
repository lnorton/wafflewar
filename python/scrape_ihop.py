from bs4 import BeautifulSoup
from os.path import isfile
from re import search
from time import sleep
from waffle_scraper import read_json, write_json, fetch_url, fetch_test_url

is_test = True
sleep_time = 0 if is_test else 5
ihop_base_url = 'https://restaurants.ihop.com/en-us/'
ihop_base_url_len = len(ihop_base_url)
ihops_json = "ihops.json"


def fetch_locations_page(regions_url):
    if is_test:
        return fetch_test_url(regions_url, 'ihop_us.html')
    else:
        return fetch_url(regions_url)


def fetch_state_page(state_url):
    if is_test:
        return fetch_test_url(ihop_base_url + 'ga/', 'ihop_ga.html')
    else:
        return fetch_url(state_url)


def fetch_city_page(city_url):
    if is_test:
        return fetch_test_url(ihop_base_url + 'ga/atlanta/', 'ihop_atlanta.html')
    else:
        return fetch_url(city_url)


def fetch_location_page(location_url):
    if is_test:
        return fetch_test_url(ihop_base_url + 'ga/atlanta/breakfast-2741-clairmont-rd-ne-413', 'ihop_413.html')
    else:
        return fetch_url(location_url)


def fetch_state_links(regions_url):
    html = fetch_locations_page(regions_url)
    bs = BeautifulSoup(html, 'html.parser')
    bs_state_list = bs.find('ul', {'id': 'bowse-content'})  # yes, "bowse"
    bs_state_links = bs_state_list.find_all('a')
    return list(map(lambda x: x['href'], bs_state_links))


def fetch_state(state_url):
    locations = []
    html = fetch_state_page(state_url)
    bs = BeautifulSoup(html, 'html.parser')
    bs_city_list = bs.find('ul', {'class': 'map-list'})
    bs_city_links = bs_city_list.find_all('a')
    city_links = list(map(lambda x: x['href'], bs_city_links))
    for city_link in city_links:
        locations.extend(fetch_city(city_link))
    return locations


def fetch_city(city_url):
    locations = []
    html = fetch_city_page(city_url)
    bs = BeautifulSoup(html, 'html.parser')
    bs_location_list = bs.find('ul', {'class': 'map-list'})
    bs_location_items = bs_location_list.find_all('div', {'class': 'map-list-item'})
    location_links = list(map(lambda x: x['href'], map(lambda c: c.find('a'), bs_location_items)))
    for location_link in location_links:
        locations.append(fetch_location(location_link))
    return locations


def fetch_location(location_url):
    html = fetch_location_page(location_url)
    bs = BeautifulSoup(html, 'html.parser')

    link = '/' + location_url[ihop_base_url_len:]

    bs_store_link = bs.find('a', {'data-fid': True})
    store_number = bs_store_link['data-fid']
    name = "IHOP #" + str(store_number)

    bs_top = bs.find('div', {'class': 'indy-location-card-wrap'})
    bs_address = bs_top.find('div', {'class': 'address'})
    bs_address_lines = bs_address.find_all('div')
    address = []
    for bs_address_line in bs_address_lines:
        text = bs_address_line.get_text().strip()
        if len(text) > 0:
            address.append(text)

    lat_pattern = r'\"latitude\":\s*\"([+-]?(\d*[.])?\d+)\"'
    lng_pattern = r'\"longitude\":\s*\"([+-]?(\d*[.])?\d+)\"'
    m = search(lat_pattern, html)
    lat = m.group(1)
    m = search(lng_pattern, html)
    lng = m.group(1)
    coords = [float(lat), float(lng)]

    location = {'link': link, 'name': name, 'address': address, 'coords': coords}
    print(location)
    sleep(sleep_time)
    return location


def state_from_state_link(link):
    return link[ihop_base_url_len:ihop_base_url_len+2].upper()


state_links = fetch_state_links(ihop_base_url)

if isfile(ihops_json):
    ihops = read_json(ihops_json)
else:
    ihops = {'states': {}}
    for state_link in state_links:
        state = state_from_state_link(state_link)
        ihops['states'][state] = {'is_complete': False}

for state_link in state_links:
    state = state_from_state_link(state_link)
    if not ihops['states'][state]['is_complete']:
        ihops['states'][state]['locations'] = fetch_state(state_link)
        ihops['states'][state]['is_complete'] = True
        write_json(ihops, ihops_json)
