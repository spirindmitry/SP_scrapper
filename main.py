from bs4 import BeautifulSoup
import requests
import csv
import os
from random import choice

BASE_URL = 'https://www.rusprofile.ru'
CODE = '241090'


def get_number_of_entries(html, scope='all'):
    params = {'page': ' – ', 'all': ' из '}
    soup = BeautifulSoup(html, 'lxml')
    num = soup.find('span', class_='num').text
    num = num[num.find(params[scope]) + 4:]
    return num


def get_proxies(number=11):
    html = requests.get('https://free-proxy-list.net/').text
    soup = BeautifulSoup(html, 'lxml')

    trs = soup.find('table', id='proxylisttable').find_all('tr')[1:number]

    proxies = []

    for tr in trs:
        tds = tr.find_all('td')
        ip = tds[0].text.strip()
        port = tds[1].text.strip()
        schema = 'https' if 'yes' in tds[6].text.strip() else 'http'
        proxy = {'schema': schema, 'address': ip + ':' + port}
        proxies.append(proxy)

    return proxies


def get_html(url, proxy=None):
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    # proxies = {'https': 'ipaddress:5000'}

    r = requests.get(url, headers=headers, proxies=proxy, timeout=5)
    if r.ok:
        print(f'URL: {url}, proxy: {proxy}, response: OK')
        return r.text

    print(r.status_code)


def write_csv(data):
    with open(CODE + '.csv', 'a') as f:
        writer = csv.writer(f)
        writer.writerow([data['name'], data['url'], data['region'], data['ogrn'], data['inn'], data['address']])
    #     reader = csv.reader(f)
    #     row_count = sum(1 for _ in reader)  # fileObject is your csv.reader
    # return row_count


def get_page_data(html):
    soup = BeautifulSoup(html, 'lxml')

    lis = soup.find('ul', class_='unitlist')
    lis = lis.find_all('li')
    for li in lis:
        url = BASE_URL + li.find("a", class_="u-name nound").get("href")
        name = li.find("span", class_="und").text
        region = li.find('div', class_='u-region').text
        address = li.find('div', class_='u-address').text

        requisites = li.find_all('div', class_='u-reqline')
        requisites = [r.text for r in requisites]
        requisites = [r[r.find(':') + 1:] for r in requisites]

        data = {
            'name': name,
            'url': url,
            'region': region,
            'address': address,
            'ogrn': requisites[0],
            'inn': requisites[1]
        }

        # print(f'{url}, {name}, {requisites}')
        write_csv(data)

    paging = soup.find('ul', class_='paging')
    next_link = paging.find('li', class_='next')

    if next_link:
        return BASE_URL + next_link.find('a').get('href')


def main():

    url = BASE_URL + '/codes/' + CODE
    filename = CODE + '.csv'
    if os.path.exists(filename):
        os.remove(filename)
    else:
        print("New parsing")

    proxies = get_proxies(20)  # {'schema': '', 'address': ''}

    while True:
        print(f'{url}')

        proxy = choice(proxies)
        proxy = {proxy['schema']: proxy['address']}
        html = get_html(url, proxy=proxy)
        print(f'{get_number_of_entries(html)}')
        url = get_page_data(html)

        if not url:
            break


if __name__ == '__main__':
    main()
