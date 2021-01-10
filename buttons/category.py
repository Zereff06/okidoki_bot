import config
from aiogram import types
from sqlighter import sql

dp = config.dp
bot = config.bot

NAME = 'Выбор категории'
ru_array_category = [c['ru'] for c in config.categories]

# button_names
commands_categories = [str(category['ru']) for category in config.categories]
buttons_categories = [types.KeyboardButton(category) for category in commands_categories]
f_button_category = types.ReplyKeyboardMarkup(resize_keyboard=True)
f_button_category.add(*buttons_categories).add('Главное меню')




async def start(message: types.Message):
    # Выбор категории
    if message.text == NAME:
        await message.answer('Объявления из каких категорий будут вам присылаться?', reply_markup=f_button_category)
        return True

    # Подписка/Отписка
    elif message.text in ru_array_category:
        category_input = config.find_item(config.categories, 'ru', message.text, 'eng')
        was_exist = sql.update_item_bool('categories', category_input, message.from_user.id)

        if was_exist:
            await message.answer(f'Вы успешно отписались от рассылки {message.text}')
        else:
            await message.answer(f'Вы успешно подписались на рассылку {message.text}')
        return True


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
