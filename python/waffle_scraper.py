from json import load, dump
from os.path import isfile
from urllib.request import Request, urlopen

user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36'


def read_file(filename):
    with open(filename, mode='r') as f:
        return f.read()


def write_file(text, filename):
    with open(filename, mode='w') as f:
        f.write(text)


def read_json(filename):
    with open(filename, mode='r') as f:
        return load(f)


def write_json(obj, filename):
    with open(filename, mode='w') as f:
        dump(obj, f, indent=1)


def fetch_url(url):
    req = Request(url, headers={'User-Agent': user_agent})
    res = urlopen(req)
    return res.read().decode('utf-8')


def fetch_test_url(url, filename):
    if isfile(filename):
        return read_file(filename)
    else:
        html = fetch_url(url)
        write_file(html, filename)
        return html
