from sqlighter import sql
import config
from aiogram import types
from aiogram.dispatcher.filters import Text
import start
from bs4 import BeautifulSoup as bs
import requests

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

# Buttons
# cities
commands_cities = ['/' + str(city['ru']) for city in config.cities]
buttons_cities = [types.KeyboardButton(city) for city in commands_cities]
f_button_city = types.ReplyKeyboardMarkup(resize_keyboard=True)
for city in buttons_cities:
    f_button_city.add(city)

# categories
commands_categories = ['/' + str(category['ru']) for category in config.categories]
buttons_categories = [types.KeyboardButton(category) for category in commands_categories]
f_button_category = types.ReplyKeyboardMarkup(resize_keyboard=True)
for category in buttons_categories:
    f_button_category.add(category)


# Commands
# Команда подписки
@dp.message_handler(commands=['subscribe'])
async def subscribe(message: types.Message):
    if sql.user_exists(message.from_user.id):  # если он уже есть, то просто обновляем ему статус подписки
        sql.update_subscription(message.from_user.id, True)
        is_enabled = sql.cursor.execute(f"SELECT subscription FROM users WHERE user_id={message.chat.id}").fetchone()
        if is_enabled[0]:
            await message.answer(
                "Вы уже подписались на рассылку! \nОсталось лишь выбрать нужный вам город и категорию обьявлений.\n /city  и  /category")
        else:
            await message.answer(
                "Вы успешно подписались на рассылку! \nДальше выберите нужный вам город и категорию обьявлений.\n /city  и  /category")
    else:  # если юзера нет в базе, добавляем его
        sql.add_new_user(message.from_user)
        await message.answer(
            "Вы успешно подписались на рассылку! \nДальше выберите нужный вам город и категорию обьявлений.\n /city  и  /category")


# Команда отписки
@dp.message_handler(commands=['unsubscribe'])
async def unsubscribe(message: types.Message):
    if sql.user_exists(message.from_user.id):
        # если он уже есть, то просто обновляем ему статус подписки
        sql.update_subscription(message.from_user.id, False)
        await message.answer("Вы успешно отписаны от рассылки.")
    else:
        # если юзера нет в базе, добавляем его с неактивной подпиской (запоминаем)
        sql.add_new_user(message.from_user, False)
        await message.answer("Вы итак не подписаны.")

@dp.message_handler(commands=['new_parse'])
async def unsubscribe(message: types.Message):
    if message.chat.id == config.settings['ADMIN_ID']:
        await message.answer('Запущено новое сканирование')
        await start.starting_okidoki()
    else:
        await message.answer('У вас нет прав для этой команды :с')

# Выбор города
@dp.message_handler(commands=['city'])
async def city(message: types.Message):
    await message.answer('Объявления из каких городов будут вам присылаться?', reply_markup=f_button_city)


# Выбор категории
@dp.message_handler(commands=['category'])
async def category(message: types.Message):
    await message.answer('Объявления из каких категорий будут вам присылаться?', reply_markup=f_button_category)


# Посмотреть на все подписанные города
@dp.message_handler(commands=['my_cities'])
async def my_cities(message: types.Message):
    subscribes_cities = []
    cities = sql.cursor.execute(f"SELECT * FROM cities WHERE user_id={message.chat.id}")
    cells_name = list(map(lambda x: x[0], cities.description))
    cities = cities.fetchone()
    for i, cell_name in enumerate(cells_name):
        if cell_name == 'user_id': continue
        if cities[i] == 1: subscribes_cities.append(cell_name)

        # Перевод на русский
    subscribes_categories_translate = []
    for category in subscribes_cities:
        subscribes_categories_translate.append(config.find_item(config.cities, 'eng', category, 'ru'))
    subscribes_cities = subscribes_categories_translate

    if len(subscribes_cities) == 0:
        await message.answer('Вы ещё не выбрали ни одного города')
    else:

        if len(subscribes_cities) > 1:
            answer = ', '.join(subscribes_cities)
            await message.answer(f'Вы подписаны на следующие города: {answer}')
        else:
            answer = subscribes_cities[0]
            await message.answer(f'Вы подписаны на следующий город: {answer}')


# Посмотреть на все подписанные категории
@dp.message_handler(commands=['my_categories'])
async def my_categories(message: types.Message):
    subscribes_categories = []
    categories = sql.cursor.execute(f"SELECT * FROM categories WHERE user_id={message.chat.id}")
    cells_name = list(map(lambda x: x[0], categories.description))
    categories = categories.fetchone()
    for i, cell_name in enumerate(cells_name):
        if cell_name == 'user_id': continue
        if categories[i] == 1: subscribes_categories.append(cell_name)

    # Перевод на русский
    subscribes_categories_translate = []
    for category in subscribes_categories:
        subscribes_categories_translate.append(config.find_item(config.categories, 'eng', category, 'ru'))
    subscribes_categories = subscribes_categories_translate

    if len(subscribes_categories) == 0:
        await message.answer('Вы ещё не подписались ни на одну категорию')
    else:

        if len(subscribes_categories) > 1:
            answer = ', '.join(subscribes_categories)
            await message.answer(f'Вы подписаны на следующие категории: {answer}')
        else:
            answer = subscribes_categories[0]
            await message.answer(f'Вы подписаны на следующую категорию: {answer}')

@dp.message_handler(commands=['add_blacklist'])
async def my_categories(message: types.Message):
    if not check_permission(message.chat.id, 'admin'):
        await message.answer('У вас нет прав на эту команду')
        return
    link = message.text[len('/add_blacklist '):]
    in_bd = sql.cursor.execute(f"SELECT COUNT(link) FROM blacklist WHERE link = '{link}'").fetchone()
    if len(in_bd)>0:
        city, category = parsing_page_city_category(link)
        sql.cursor.execute(f"INSERT INTO blacklist(link, city, category)  VALUES ('{link}', '{city}', '{category}')")
        sql.conn.commit()
        await message.answer("Этот пост удачно добавлен в чёрный список")
    else:
        await message.answer("Этот пост уже в чёрном списке")


















































# Ловим ответ от кнопок с городами
@dp.message_handler(Text(equals=commands_cities))
async def handler_cities(message: types.Message):
    city_input = message.text[1:]
    city_input = config.find_item(config.cities, 'ru', city_input, 'eng')
    was_exist = sql.update_item_bool('cities', city_input, message.from_user.id)

    if was_exist:
        await message.answer(f'Вы успешно отписались от рассылки для "{city_input}"')
    else:
        await message.answer(f'Вы успешно подписались на рассылки для "{city_input}"')


# Ловим ответ от кнопок с категориями
@dp.message_handler(Text(equals=commands_categories))
async def handler_categories(message: types.Message):
    category_input = message.text[1:]
    category_input = config.find_item(config.categories, 'ru', category_input, 'eng')
    was_exist = sql.update_item_bool('categories', category_input, message.from_user.id)

    if was_exist:
        await message.answer(f'Вы успешно отписались от рассылки "{category_input}"')
    else:
        await message.answer(f'Вы успешно подписались на рассылку "{category_input}"')


# Ответ на неузнаную команду
@dp.message_handler()
async def echo(message: types.Message):
    await message.answer('К сожалению, я тебя не понял :с')


def parsing_page_city_category(link):
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

def check_permission(user_id, perm):
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
