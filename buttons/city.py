import config
from aiogram import types
from sqlighter import sql

dp = config.dp
bot = config.bot

CHOOSE_CITY = 'Выбор города'

# Города
commands_cities = [str(city['ru']) for city in config.cities]
buttons_cities = [types.KeyboardButton(city) for city in commands_cities]
f_button_city = types.ReplyKeyboardMarkup(resize_keyboard=True)
f_button_city.add(*buttons_cities)


# Выбор города
async def start(message: types.Message):
    if message.text == CHOOSE_CITY:
        await message.answer('Объявления из каких городов будут вам присылаться?', reply_markup=f_button_city)
        return True
    else:
        for city in config.cities:
            if message.text == city['ru']:

                was_exist = sql.update_item_bool('cities', city['eng'], message.from_user.id)

                if was_exist:
                    await message.answer(f"Вы успешно отписались от рассылки для города {city['ru']}")

                else:
                    await message.answer(f"Вы успешно подписались на рассылки для города {city['ru']}")

                return True


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
