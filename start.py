
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
Каждые 20 минут, идёт парсинг требуемых категорий, не учитывая город. 
Затем идёт их фильтрация по городу и отправка постов пользователю
"""

API_TOKEN = config.settings['API_TOKEN']
HOST = config.settings['HOST']
HOST_POSTS = config.settings['HOST_POSTS']








# Логика запуска парсинга
async def starting_okidoki():
    categories = config.categories
    cities = config.cities

    for category in categories:

        for city in cities:

            okidoki = ok.Okidoki(category, city)
            data = okidoki.start()

            if data is False:
                continue
            elif len(data['posts']) > 0:
                for user in data['users']:
                    user = user[0]
                    for post in data['posts']:
                        try:
                            await commands.send_post(user, post)
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
