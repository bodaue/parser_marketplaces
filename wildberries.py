import json
import re

import requests
from bs4 import BeautifulSoup


class ParseWildberries:

    def __init__(self, profile):

        self.profile = profile

        if self.profile[-1] == '/':
            self.profile = profile[:-1]

        self.session = requests.Session()
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/96.0.4664.174 YaBrowser/22.1.5.810 Yowser/2.5 Safari/537.36 '
        }

    # загрузка страницы
    def load_page(self, url):
        res = self.session.get(url=url)
        res.raise_for_status()
        result = BeautifulSoup(res.text, 'html.parser')
        return result

    # парсинг информации о профиле
    def parse_profile(self):
        link = self.profile
        soup = self.load_page(link)

        # название магазина
        name_of_shop = soup.find('h2', class_='seller-details__title')
        if not name_of_shop:
            name_of_shop = soup.find('h1', class_='brand-custom-header__name')
        name_of_shop = name_of_shop.text.replace('Каталог ', '')

        # айди магазина
        shop_id = soup.find('link').get('href')
        shop_id = shop_id.replace('wildberries://www.wildberries.ru/', '').replace('seller/', '').replace('brands/', '')

        profile = {'name': name_of_shop, 'shop_id': shop_id}
        result = {'profile': profile}

        return result

    # парсинг товаров
    def parse_products(self):
        profile_link = self.profile
        soup = self.load_page(profile_link)
        list_of_products = list()

        try:
            pages = soup.find_all('a', class_='pagination-item pagination__item')[-1]
            pages = int(pages.get('data-value'))  # количество страниц
        except:
            pages = 1

        # проход по каждой странице
        for page in range(pages):
            # подгружаем нужную страницу
            soup = self.load_page(profile_link + f'?page={page + 1}')
            products = soup.find_all('div', class_='product-card__wrapper')  # список продуктов на данной странице

            for product in products:
                # название бренда
                brand_name = product.find('strong', class_='brand-name').text

                # название товара
                good_name = product.find('span', class_='goods-name').text

                # ссылка на товар
                link = product.find('a', class_='product-card__main j-open-full-product-card').get('href')
                link = 'https://www.wildberries.ru' + link

                # фотография товара
                photo = product.find('img').get('data-original')
                if photo is None:
                    photo = product.find('img').get('src')

                # цена товара
                price = product.find(re.compile(r'ins|span'), class_='lower-price').text
                price = re.sub(r'[^\x00-\x7F]+', '', price).strip()

                # количество отзывов
                count_rating = product.find('span', class_='product-card__count')
                if count_rating:
                    count_rating = re.sub(r'[^\x00-\x7F]+', '', count_rating.text).strip()
                else:
                    count_rating = 0

                # рейтинг товара
                rating = product.find('span', class_=re.compile('product-card__rating stars-line'))
                if rating:
                    rating = rating.get('class')[3].replace('star', '')
                else:
                    rating = None

                list_of_products.append(
                    {'brand_name': brand_name, 'good_name': good_name, 'link': link, 'photo': photo, 'price': price,
                     'count_rating': count_rating, 'rating': rating, })
        item_dct = {'products': list_of_products}
        return item_dct

    # сохранение результата в формате json
    def save_result(self):
        profile_info = self.parse_profile()
        products_info = self.parse_products()
        result = profile_info | products_info

        with open(f'result_wildberries.json', 'w', encoding='utf-8') as file:
            json.dump(result, file, indent=4, ensure_ascii=False)


wb = ParseWildberries('https://www.wildberries.ru/brands/apple')
wb.save_result()
