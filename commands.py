from sqlighter import sql
import config
from aiogram import types
import start
from bs4 import BeautifulSoup as bs
import requests

import buttons.button_menu

dp = config.dp
bot = config.bot


async def send_post(user_id, post, notification):
    capture = post['title'] + "\n" +"Цена: " +  post['price'] +'  ' + post['city'] + "\n" + post['description']

    keyboard = types.InlineKeyboardMarkup()
    url_btn = types.InlineKeyboardButton(text='Открыть', url=post['link'])
    keyboard.add(url_btn)
    await bot.send_photo(
        user_id,
        post['image'],
        caption=capture,
        reply_markup=keyboard,
        disable_notification= not notification #Бесшумный режим выключен если True
    )






# Commands
@dp.message_handler(commands=['new_parse'])
async def unsubscribe(message: types.Message):
    if message.chat.id == config.settings['ADMIN_ID']:
        await message.answer('Запущено новое сканирование')
        await start.starting_okidoki()
    else:
        await message.answer('У вас нет прав для этой команды :с')

@dp.message_handler(commands=['add_blacklist'])
async def my_categories(message: types.Message):
    if not check_permission(message.chat.id, 'admin'):
        await message.answer('У вас нет прав на эту команду')
        return
    link = message.text[len('/add_blacklist '):]
    in_bd = sql.cursor.execute(f"SELECT COUNT(link) FROM blacklist WHERE link = '{link}'").fetchone()
    if len(in_bd)>0:
        city, category = get_city_and_category_from_page(link)
        sql.cursor.execute(f"INSERT INTO blacklist(link, city, category)  VALUES ('{link}', '{city}', '{category}')")
        sql.conn.commit()
        await message.answer("Этот пост удачно добавлен в чёрный список")
    else:
        await message.answer("Этот пост уже в чёрном списке")


async def get_city_and_category_from_page(link):
    r = requests.get(link)
    html = bs(r.content, 'html.parser')
    parsed_city, parsed_category = 'empty', 'empty'

    try:
        parsed_city = html.select_one('.location span').text.lower()
    except:
        pass
    try:
        parsed_category = html.select_one('.breadcrumbs li a span').text
    except:
        pass

    if parsed_category != 'empty':
        for category in config.categories:
            if category['ru'] == parsed_category:
                parsed_category = category['eng']

    return [parsed_city, parsed_category]

async def check_permission(user_id, perm):
    user_perm = sql.cursor.execute(f"SELECT permissions FROM users WHERE user_id = '{user_id}'").fetchone()[0]
    perm = perm.lower()
    if user_perm == 'empty':
        if perm == 'empty' : return True
        else: return False
    if perm == user_perm:
        return True
    user_perm = user_perm.split(', ')
    if len(user_perm)>1:
        if perm in user_perm:
            return True
    return False

# Ответ на неузнаную команду
@dp.message_handler()
async def echo(message: types.Message):

    if   await buttons.button_menu.start(message):  return
    elif await buttons.city.start(message):         return
    elif await buttons.category.start(message):     return
    elif await buttons.subscribe.start(message):    return
    elif await buttons.timer.start(message):        return
    else:
        await message.answer('К сожалению, я тебя не понял :с')