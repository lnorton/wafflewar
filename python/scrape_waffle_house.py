from bs4 import BeautifulSoup
from os.path import isfile
from re import search
from time import sleep
from waffle_scraper import read_json, write_json, fetch_url, fetch_test_url

is_test = True
sleep_time = 0 if is_test else 5
wh_base_url = "https://locations.wafflehouse.com/"
waffle_houses_json = "waffle_houses.json"


def fetch_regions_page(regions_url):
    if is_test:
        return fetch_test_url(regions_url, 'wh_us.html')
    else:
        return fetch_url(regions_url)


def fetch_state_page(state_url):
    if is_test:
        return fetch_test_url(wh_base_url + 'region/US/GA', 'wh_ga.html')
    else:
        return fetch_url(state_url)


def fetch_shop_page(shop_url):
    if is_test:
        return fetch_test_url(wh_base_url + 'shop/178075/waffle-house-1000', 'wh_1000.html')
    else:
        return fetch_url(shop_url)


def fetch_state_links(regions_url):
    html = fetch_regions_page(regions_url)
    bs = BeautifulSoup(html, 'html.parser')
    bs_state_links = bs.find('div', {'class': 'tiles'}).find_all('a')
    return list(map(lambda x: x['href'], bs_state_links))


def fetch_shops(state_url):
    shops = []
    html = fetch_state_page(state_url)
    bs = BeautifulSoup(html, 'html.parser')
    bs_links = bs.find('div', {'class': 'tiles wider'}).find_all('a')
    for bs_link in bs_links:
        link = bs_link['href']
        name = bs_link.find('span', {'class': 'name'}).get_text().strip()
        bs_address = bs_link.find('span', {'class': 'address'})
        address_lines = list(map(lambda c: c.string.strip(), filter(lambda c: c.name != 'br', bs_address)))
        shops.append([link, name, address_lines])
    return shops


def fetch_lat_long(shop_url):
    pattern = r'forceMapState\s*=\s*\[\"([+-]?(\d*[.])?\d+)\",\"([+-]?(\d*[.])?\d+)\"'
    html = fetch_shop_page(shop_url)
    m = search(pattern, html)
    return [float(m.group(1)), float(m.group(3))]


state_links = fetch_state_links(wh_base_url + "regions")

if isfile(waffle_houses_json):
    waffle_houses = read_json(waffle_houses_json)
else:
    waffle_houses = {'states': {}}
    for state_link in state_links:
        state = state_link[-2:]
        waffle_houses['states'][state] = {'is_complete': False}

for state_link in state_links:
    state = state_link[-2:]
    if not waffle_houses['states'][state]['is_complete']:
        waffle_houses['states'][state]['locations'] = []
        for shop in fetch_shops(wh_base_url + state_link):
            coords = fetch_lat_long(wh_base_url + shop[0])
            shop_dict = {'link': shop[0],
                         'name': shop[1],
                         'address': shop[2],
                         'coords': coords}
            waffle_houses['states'][state]['locations'].append(shop_dict)
            print(f'{shop[1]}, {shop[2]}, {coords}')
            sleep(sleep_time)
        waffle_houses['states'][state]['is_complete'] = True
        write_json(waffle_houses, waffle_houses_json)
