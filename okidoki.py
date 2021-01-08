import sqlighter
from bs4 import BeautifulSoup as bs
import config
import requests

sql = sqlighter.sql
HOST = config.settings['HOST']
TEST_MODE = False
UPDATE_SQL = False




class Okidoki:
    def __init__(self, category, city):

        self.url = HOST + '/' + category['link'] + '?' + city['cid'] + '&' + config.sort['new_is_first']
        self.category = category['eng']
        self.city = city['eng']
        self.new_premium_posts = []
        self.old_premium_posts = []
        self.new_last_posts = []
        self.count_of_premiums = 0

    def test_mode(self):
        if TEST_MODE == 'links':
            if UPDATE_SQL:
                self.update_bd()
            exit()

        if TEST_MODE == 'pets':
            if self.category != 'pets': return True
            if self.city != 'tallinn': return True
        if TEST_MODE == 'parsing_off': return True

    def get_data(self):
        return self.start()

    def start(self):
        if self.test_mode(): return False
        users = sql.cursor.execute(
            f"SELECT cities.user_id FROM cities,categories WHERE cities.user_id = categories.user_id AND cities.{self.city} = 1 AND categories.{self.category} = 1").fetchall()
        if len(users) == 0:  # Если нет подписчиков
            return False

        post_links, premium_links = self.parse_page()  # Получили все ссылки на все посты

        is_main = len(post_links) > 0
        is_premium = len(premium_links) > 0

        # Сортировка новых от старых
        # main
        if is_main: main_links_sorted = self.sort_main_posts(post_links)

        # premium
        if is_premium: premium_links_sorted = self.sort_premium_posts(premium_links)

        if not is_main and not is_premium: return False
        self.test_mode()

        # Получаем доп. ин-фу о постах
        premium_links_info, main_links_info = [], []
        if is_main: main_links_info = self.get_posts_info(main_links_sorted)
        if is_premium: premium_links_info = self.get_posts_info(premium_links_sorted)

        return {'users': users, 'posts': premium_links_info + main_links_info}

    # Сортировка основных постов
    def sort_main_posts(self, main_links):
        main_links_sorted = main_links.copy()

        # Сортировка основных постов
        is_exist_last_main_posts = f"SELECT last_post,before_last_post,before_before_last_post FROM posts  WHERE category = '{self.category}' AND city = '{self.city}'"
        lasts_posts = sql.cursor.execute(is_exist_last_main_posts).fetchone()

        if lasts_posts is None:  # Если в бд нету вообще записей о постах данной тиматики
            create_new_row = f"INSERT INTO posts(category,city) Values ('{self.category}','{self.city}')"
            sql.cursor.execute(create_new_row)
            sql.conn.commit()
        else:
            main_links_sorted = []
            for post in main_links:
                if lasts_posts[0] == post or post == lasts_posts[1] or post == lasts_posts[2]:
                    break
                else:
                    main_links_sorted.append(post)

        self.new_last_posts = main_links_sorted[:3]
        return main_links_sorted

    # Сортировка премиум постов
    def sort_premium_posts(self, premium_links):
        premium_links_sorted = []

        all_premiums_from_bd = f"SELECT link FROM premium  WHERE category = '{self.category}' AND city = '{self.city}'"
        bd_premium_links = sql.cursor.execute(all_premiums_from_bd).fetchall()

        deleted_premium_from_site = [link[0] for link in bd_premium_links]

        for premium_link in premium_links:
            if (premium_link,) in bd_premium_links:  # Если ссылка есть в бд, то
                deleted_premium_from_site.remove(premium_link)
            else:
                premium_links_sorted.append(premium_link)  # Список с новыми прем. постами

        self.old_premium_posts = deleted_premium_from_site
        self.new_premium_posts = premium_links_sorted
        return premium_links_sorted

    # Получение информации о постах
    def get_posts_info(self, links):
        posts_info = []
        for link in links:
            r = requests.get(link)
            html = bs(r.content, 'html.parser')

            price = 'Цена не указана.'  # TODO запилить указатель "Бесплатно"
            title = 'Без названия'
            poster = 'https://www.ruprom.ru/templates/images/newdesign/noimage2.png'
            description = 'Без описания'
            city = f"{config.find_item(config.cities, 'eng', self.city, 'ru')}"

            try:
                price = html.select_one('.item-details .price').text
            except:
                pass
            try:
                price = html.select_one('.item-details .free').text
            except:
                pass
            try:
                poster = html.select_one('.large-photo img').get('src')[2:]
            except:
                pass

            try:
                title = html.select_one('.item-title h1').text
            except:
                pass

            try:
                description = html.select_one('.description').text
            except:
                pass

            if len(description) > 200:
                description = description[:196] + ' ...'

            if title.lower() == description.lower():
                description = 'Без описания.'

            info = {
                "title": title,
                "link": link,
                "image": poster,
                "description": description,
                "price": price,
                "city": city
            }
            posts_info.append(info)
        return posts_info

    # Получить все ссылки на посты
    def parse_page(self):
        r = requests.get(self.url)
        html = bs(r.content, 'html.parser')

        posts = html.select('.horiz-offer-card__inner')
        get_posts = []
        get_premiums = []

        for item in posts:
            link = HOST + item.select('.horiz-offer-card__image-link')[0]['href']

            if not item.select('.offer-label.offer-label--top'):  # Если не премиум
                get_posts.append(link)
            else:
                get_premiums.append(link)

        return [get_posts, get_premiums]

    def update_bd(self):
        last_posts = self.new_last_posts

        if len(last_posts) > 0:
            if len(last_posts) == 3:
                query_update_last_posts = f"UPDATE  posts SET last_post = '{last_posts[0]}', before_last_post = '{last_posts[1]}', before_before_last_post = '{last_posts[2]}'  WHERE category = '{self.category}' AND city = '{self.city}'"
            elif len(last_posts) == 2:
                query_update_last_posts = f"UPDATE  posts SET last_post = '{last_posts[0]}', before_last_post = '{last_posts[1]}'  WHERE category = '{self.category}' AND city = '{self.city}'"
            elif len(last_posts) == 1:
                query_update_last_posts = f"UPDATE  posts SET last_post = '{last_posts[0]}'  WHERE category = '{self.category}' AND city = '{self.city}'"
            sql.cursor.execute(query_update_last_posts)

        # Premium
        if len(self.old_premium_posts) > 0:
            for link in self.old_premium_posts:
                sql.cursor.execute(f"DELETE FROM premium WHERE link='{link}'")

        if len(self.new_premium_posts) > 0:
            for link in self.new_premium_posts:
                sql.cursor.execute(
                    f"INSERT INTO premium(link, category, city) VALUES ('{link}', '{self.category}', '{self.city}')")

        sql.conn.commit()

