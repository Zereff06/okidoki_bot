import requests
from bs4 import BeautifulSoup as bs
import asyncio
from aiogram import executor

from sqlighter import sql
import commands
import config

#  инициализируем бота
dp = config.dp
bot = config.bot

"""
Каждые 20 минут, идёт парсинг требуемых категорий, не учитывая город. 
Затем идёт их фильтрация по городу и отправка постов пользователю
"""

API_TOKEN = config.settings['API_TOKEN']
HOST = config.settings['HOST']
HOST_POSTS = config.settings['HOST_POSTS']


class OkidokiCity:
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


async def send_message(user_id, post):
    capture = post['title'] + "  =>  " + post['price'] + '\n' + post['city'] + "\n" + post['description'] + "\n\n" + \
              post["link"]
    await bot.send_photo(
        user_id,
        post['image'],
        caption=capture,
        disable_notification=False
    )


# Логика запуска парсинга
async def starting_okidoki():
    categories = config.categories
    cities = config.cities

    for category in categories:

        for city in cities:

            okidoki = OkidokiCity(category, city)
            data = okidoki.start()

            if data is False:
                continue
            elif len(data['posts']) > 0:
                for user in data['users']:
                    user = user[0]
                    for post in data['posts']:
                        try:
                            await send_message(user, post)
                        except:
                            print("Не удалось найти слудуюший чат: " + user)
    print('Updated posts')


async def scheduled(wait_for):
    while True:
        print('start parse')
        await starting_okidoki()
        print('Finish')
        await asyncio.sleep(wait_for)


# запускаем лонг поллинг
if __name__ == '__main__':
    sql.create_table_if_no_exist()
    loop = asyncio.get_event_loop()
    loop.create_task(scheduled(1800))
    executor.start_polling(dp, skip_updates=True, loop=loop)
