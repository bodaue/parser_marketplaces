import json
import re

import requests
from bs4 import BeautifulSoup


class ParseOzon:

    def __init__(self, profile):
        self.profile = profile
        self.session = requests.Session()
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.174 YaBrowser/22.1.5.810 Yowser/2.5 Safari/537.36'
        }

    # загрузка страницы
    def load_page(self, url):
        res = self.session.get(url=url)
        res.raise_for_status()
        result = BeautifulSoup(res.text, 'html.parser')
        return result

    # парсинг основной информации о профиле
    def parse_profile(self):
        link = self.profile + '/profile/'
        soup = self.load_page(link)

        data_of_charaterictics = soup.find_all("div", class_="tsCaption th8 t9h")
        data_of_values = soup.find_all("div", class_="tsBodyL t8h")
        dct = dict()

        for i in range(len(data_of_charaterictics)):
            charasteristic = data_of_charaterictics[i].text
            value = data_of_values[i].text
            if charasteristic and value:
                dct.update({charasteristic: value})
        result = {'profile': dct}

        return result

    # парсинг товаров
    def parse_products(self):
        link = self.profile + '/products/'
        soup = self.load_page(link)
        products = soup.find_all('div', class_='y7h yh8')

        list_of_products = []
        for product in products:
            price = product.find('span', class_=re.compile('ui-q3 ui-q6')).text  #

            product_name = product.find("span", class_='vc6 cv7 vc7 c9v tsBodyL hx2').text

            product_link = product.find('a')
            product_link = 'www.ozon.ru' + product_link.get('href')

            comments = product.find('a', class_='v4c').text

            photo = product.find('img')
            photo = photo.get('src')

            rating = product.find('div', class_='ui-ab8')
            rating = rating.get('style').split(':')[1].replace(';', '')  # соотношение хороших отзывов к плохим

            list_of_products.append(
                {'product_name': product_name, "product_link": product_link, "photo": photo, "price": price,
                 'comments': comments, 'rating': rating})
        item_dct = {'products': list_of_products}

        return item_dct

    def get_result(self):
        profile_info = self.parse_profile()
        products_info = self.parse_products()
        result = profile_info | products_info

        return result

    # сохранение результата в формате json
    def save_result(self):
        res = self.get_result()
        with open(f'result_ozon.json', 'w', encoding='utf-8') as file:
            json.dump(res, file, indent=4, ensure_ascii=False)


parse = ParseOzon('https://www.ozon.ru/seller/riva-6253')

(parse.save_result())
