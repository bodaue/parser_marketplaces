import json
import re

import requests
from bs4 import BeautifulSoup


class ParseYandexMarket:

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

    # парсинг информации о профиле
    def parse_profile(self):
        link = self.profile + '/info'
        soup = self.load_page(link)
        try:
            name_of_shop = soup.find('h2', class_='_24r_4').text
            name_of_firm = soup.find('h1', class_='_1wcJv').text
            info = soup.find_all('p', class_='_2iK1L')

            guarantees = info[0].text
            adress = info[2].text.replace('Адрес: ', '')

            profile = {'name_of_shop': name_of_shop, 'name_of_firm': name_of_firm, 'guarantees': guarantees,
                       'adress': adress}

        except:
            profile = {}

        result = {'profile': profile}
        return result

    # парсинг товаров
    def parse_products(self):
        link = self.profile
        soup = self.load_page(link)
        products = (soup.find_all('div', class_=re.compile('2im8')))
        list_of_products = list()

        for product in products:
            product_name = product.find('span', class_='_66nxG _3WROT Qg8Jj _35WYJ').text  # название товара

            product_link = product.find('a').get('href')
            product_link = 'https://market.yandex.ru/' + product_link  # ссылка на товар

            photo = product.find('img').get('src')  # фотография
            price = product.find('span', class_=re.compile('X17hD')).text  # цена
            reviews = product.find('span', class_='_66nxG _2h8uc Qg8Jj _3ZAO4')  # отзывы

            if reviews:
                reviews = reviews.find('span').text.split('о')[0]
            rating = product.find('div', class_='_1W7aq _1jdeI _3mt0Y').get('aria-label')  # оценка товара
            rating = rating.replace('Рейтинг: ', '')

            list_of_products.append(
                {'product_name': product_name, "product_link": product_link, "photo": photo, "price": price,
                 'reviews': reviews, 'rating': rating})
        item_dct = {'products': list_of_products}

        return item_dct

    # парсинг отзывов о магазине
    def parse_reviews(self):
        link = self.profile + '/reviews'
        soup = self.load_page(link)
        reviews = soup.find_all('div', class_=re.compile('_1T0L5'))
        list_of_reviews = list()
        for review in reviews:
            name_of_reviewer = review.find('div', class_='_1UL8e').text
            rating = review.find('div', class_=re.compile('_3iy4z _3DD8b')).get('data-rate')
            commentaries = review.find_all('dl', class_='_27K1P')
            commentary = None
            for comment in commentaries:
                if comment != None and 'Комментарий' in str(comment.text):
                    commentary = comment.text.replace('Комментарий: ', '')
                    break

            list_of_reviews.append({'name_of_reviewer': name_of_reviewer, 'rating': rating, 'commentary': commentary})

        review_dict = {'reviews': list_of_reviews}
        return review_dict

    def get_result(self):
        profile_info = self.parse_profile()
        products_info = self.parse_products()а
        review_info = self.parse_reviews()
        result = profile_info | products_info | review_info

        return result

    # сохранение результата в формате json
    def save_result(self):
        res = self.get_result()
        with open(f'result_ym.json', 'w', encoding='utf-8') as file:
            json.dump(res, file, indent=4, ensure_ascii=False)


ym = ParseYandexMarket('https://market.yandex.ru/business--www-video-shoper-ru/779321')
ym.save_result()
