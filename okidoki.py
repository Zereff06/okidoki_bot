from bs4 import BeautifulSoup as bs
import config
import requests
import sqlighter
sql = sqlighter.sql
HOST = config.settings['HOST']


class Okidoki:
    def __init__(self, category, city):

        self.url = HOST + '/' + category['link'] + '?' + city['cid'] + '&' + config.sort['new_is_first']
        self.category = category['eng']
        self.city = city['eng']

    def start(self):
        users = sql.cursor.execute(
            f"SELECT cities.user_id FROM cities,categories WHERE cities.user_id = categories.user_id AND cities.{self.city} = 1 AND categories.{self.category} = 1").fetchall()
        if len(users) == 0:
            return False

        new_posts_link = self.get_new_posts()
        if len(new_posts_link) == 0:
            return False

        new_posts_info = self.get_posts_info(new_posts_link)
        self.update_last_posts(new_posts_link[:3])

        return {'users': users, 'posts': new_posts_info}

    def parse_page(self):
        r = requests.get(self.url)
        html = bs(r.content, 'html.parser')

        li = html.select('.classifieds > ul > li ')
        posts = []

        # Игнор Премки
        for item in li:
            if not item.select('.details svg') and item.select('.primary a'):
                posts.append(HOST + item.select('.primary a')[0]['href'])
        return posts

    def get_new_posts(self):
        new_posts = []
        posts_links = self.parse_page()

        # Если записи нет в таблице, то её туда добавим
        is_exist_row = f"SELECT last_post,before_last_post,before_before_last_post FROM posts  WHERE category = '{self.category}' AND city = '{self.city}'"
        lasts_posts = sql.cursor.execute(is_exist_row).fetchone()

        if lasts_posts is None:
            create_new_row = f"INSERT INTO posts(category,city) Values ('{self.category}','{self.city}')"
            sql.cursor.execute(create_new_row)
            sql.conn.commit()
            new_posts = posts_links

            self.update_last_posts(posts_links[:3])
        else:
            for post in posts_links:
                if lasts_posts[0] == post or post == lasts_posts[1] or post == lasts_posts[2]:
                    break
                else:
                    new_posts.append(post)
        return new_posts

    def update_last_posts(self, last_posts):

        query_update_last_posts = f"UPDATE  posts SET last_post = '{last_posts[0]}', before_last_post = '{last_posts[1]}', before_before_last_post = '{last_posts[2]}'  WHERE category = '{self.category}' AND city = '{self.city}'"
        sql.cursor.execute(query_update_last_posts)
        sql.conn.commit()

    def get_posts_info(self, links):
        new_posts_info = []
        for link in links:
            r = requests.get(link)
            html = bs(r.content, 'html.parser')

            price = 'Цена не указана.'
            title = 'Без названия'
            poster = 'https://www.ruprom.ru/templates/images/newdesign/noimage2.png'
            description = 'Без описания'
            city = f"({config.find_item(config.cities, 'eng', self.city, 'ru')})"

            try:
                price = html.select_one('.item-details .price').text
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

            if len(description) > 200: description = description[:196] + ' ...'
            if title == description: description = 'Без описания.'

            info = {
                "title": title,
                "link": link,
                "image": poster,
                "description": description,
                "price": price,
                "city": city
            }
            new_posts_info.append(info)
        return new_posts_info