import asyncio
from aiogram import executor
from sqlighter import sql
import commands
import config
import okidoki as ok

#  инициализируем бота
dp = config.dp
bot = config.bot

"""
Каждые 30 минут, идёт парсинг требуемых категорий, не учитывая город. 
Затем идёт их фильтрация по городу и отправка постов подписчикам
"""

API_TOKEN = config.settings['API_TOKEN']
HOST = config.settings['HOST']
HOST_POSTS = config.settings['HOST_POSTS']








# Логика запуска парсинга и отправка
async def city_loop(category):
    cities = config.cities
    for city in cities:
        okidoki = ok.Okidoki(category, city)
        data = okidoki.get_data()

        if data is False:
            continue

        for user in data['users']:  # Для каждого подписсичка
            user = user[0]
            for post in data['posts']:  # Отправляются все посты на которые он подписан
                try:
                    await commands.send_post(user, post)
                except:
                    print("Не удалось найти слудуюший чат: " + user)

        print(category['ru'], city['ru'] , 'finished')
        print('{ ',data['posts'], ' }')
        okidoki.update_bd()


async def scheduled(wait_for):
    while True:
        print('start parse')

        categories = config.categories
        for category in categories:
            loop.create_task(city_loop(category))

        print('Finish')
        await asyncio.sleep(wait_for)


# запускаем лонг поллинг
if __name__ == '__main__':
    sql.create_table_if_no_exist()
    loop = asyncio.get_event_loop()
    loop.create_task(scheduled(1800))
    executor.start_polling(dp, skip_updates=True, loop=loop)
