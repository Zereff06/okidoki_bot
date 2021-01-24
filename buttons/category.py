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

#sub_categories
array_sub_categories = {
    'Транспорт' :['Весь транспорт','Автомобили','Водный транспорт','Коммерческий транспорт','Мототранспорт','Прицепы, автодома','Снегоходы','Товары и запчасти','Другой транспорт'],
    'Недвижимость':['Вся недвижимость','Гаражи, парковки','Дома','Квартиры','Коммерческая недвижимость','Комнаты','Участки земли','Часть дома'],
    'Работа' :['Вся работа','Вакансии','Ищу работу, CV'],
    'Мода, стиль и красота': ['Вся мода','Женская обувь','Женская одежда','Женские аксессуары, сумочки','Здоровье и красота','Карнавальные костюмы','Мужская обувь','Мужская одежда','Мужские аксессуары','Одежда для беременных и кормящих','Свадебная одежда','Униформа','Ювелирные изделия и часы','Другая одежда'],
    'Детские товары':['Все детские товары','Автокресла','Аксессуары для колясок','Безопасность и здоровье','Детская мебель','Детская обувь','Детская одежда','Детские аксессуары','Игрушки','Книги для детей','Коляски','Купание','Оборудование','Питание','Подгузники и горшки','Другие детские товары'],
    'Дом и сад':['Всё для дома и сада','Бытовая техника','Грили','Дрова, брикеты, гранулы','Кухонные принадлежности','Мебель и интерьер','Постельные принадлежности','Продукты и напитки','Ремонт и строительство','Сад и огород','Другое для дома и сада'],
    'Электроника':['Вся электроника','iPod, MP3 плееры','Аксессуары','Гаджеты','Домашнее аудио','Домашний кинотеатр','Дроны, квадрокоптеры','Кабельное и спутниковое ТВ','Камеры и фото','Компьютеры и планшеты','Мобильное аудио и видео','Мобильные телефоны','Настольные телефоны','Наушники','Радио','Смарт-часы','Телевизоры','Устаревшая электроника','Устройства GPS','Другяа электроника'],
    'Развлечения и хобби':['Все для хобби','Билеты','Видеоигры','Кино и DVD','Книги и журналы','Коллекционирование','Музыка','Музыкальные инструменты','Настольные игры','Подарочные карты','Путешествия и отдых','Ремесла','Табакокурение'],
    'Спортивный инвентарь':['Всё для спорта','Велосипеды','Гольф','Дайвинг','Игры с мячом','Конный спорт','Лыжи и сноуборд','Охота','Пейнтбол и страйкбол','Роликовые коньки','Рыбалка','Самокаты и гироскутеры','Спортивная обувь','Спортивная одежда','Спортивное питание','Сёрфинг','Теннис','Фигурное катание','Фитнес','Хоккей','Другое для спрорта'],
    'Услуги':['Все услуги','Бухгалтерские услуги','Графика и логотипы','Услуга здоровье и красота ','Интернет, компьютеры','Ломбарды и скупка','Медицина','Медия, обработка, копии','Недвижимость','Няни, сиделки','Обслуживание, ремонт техники','Обучение, курсы','Одежда и ювелирные изделия на заказ','Печать','Питание, кейтеринг','Подарки, мероприятия','Развлечение','Ремонт одежды и обуви','Ритуальные услуги', "Сад и благоустройство", "Строительство и ремонт", "Транспорт, перевозки", "Уборка и утилизация", "Уход за животными", "Финансовые услуги", "Фотография, видео", "Юридические услуги", "Другие услуги",],
    'Животные':['Все животные','Аквариумистика','Вязка','Грызуны','Кошки','Птицы','Сельскохозяйственные животные','Собаки','Товары для животных','Экзотические животные'],
    'Всё для бизнеса':['Весь бизнес','Готовый бизнес','Оборудование для бизнеса']
}
emoji_on = "✅"
emoji_off = "❌"


async def start(message: types.Message):
    # Выбор категории
    if message.text == NAME:
        await message.answer('Объявления из каких категорий будут вам присылаться?', reply_markup=f_button_category)
        return True
    elif message.text in array_sub_categories:
        await message.answer(message.text, reply_markup=await show_sub_buttons(message))
        return True
    elif emoji_on == message.text[0] or message.text[0] == emoji_off:
        message.text = message.text[2:]

        if await update_status_all_sub_category(message):
            return True
        elif await update_status_sub_category(message):
            return True

async def update_status_all_sub_category(message: types.Message):
    array_types, array_all = [], []

    for key, value in array_sub_categories.items():
        array_types.append(key)
        array_all.append(value[0])

    if message.text not in array_all:
        return False

    status = sql.cursor.execute(f"SELECT `{message.text}` FROM sub_categories WHERE user_id = {message.from_user.id}").fetchone()[0]
    if status == 1: new_status=0
    elif status == 0 : new_status = 1
    else:
        print(f'Ошибка со статусом у {message.from_user.id} - {message.text} = {status}')
        return

    current_array_types = array_types[array_all.index(message.text)]

    query = ""
    for sub_cat in array_sub_categories[current_array_types]:
        query += f"`{sub_cat}` = {new_status}, "

    sql.cursor.execute(f"UPDATE sub_categories SET "+ query[:-2] + f" WHERE user_id = {message.from_user.id}")
    sql.conn.commit()

    if new_status == 1:
        await message.answer('Вы подписались на рассылку ' + message.text, reply_markup=await show_sub_buttons(message, await is_sub_category(message)))
        return True
    else :
        await message.answer('Вы отписались от рассылки на ' + message.text, reply_markup=await show_sub_buttons(message, await is_sub_category(message)))
        return True


async def update_status_sub_category(message: types.Message):
    sub_status = sql.cursor.execute(f"SELECT `{message.text}` FROM sub_categories WHERE user_id= {message.from_user.id}").fetchone()[0]

    if sub_status:
        sql.cursor.execute(f"UPDATE sub_categories SET `{message.text}` = 0 WHERE user_id = {message.from_user.id}")
        sql.conn.commit()
        await message.answer('Вы отписались от рассылки ' + message.text, reply_markup=await show_sub_buttons(message, await is_sub_category(message)))
        return True

    else:
        sql.cursor.execute(f"UPDATE sub_categories SET `{message.text}` = 1 WHERE user_id = {message.from_user.id}")
        sql.conn.commit()
        await message.answer('Вы подписались на рассылку ' + message.text, reply_markup=await show_sub_buttons(message, await is_sub_category(message)))
        return True


async def is_sub_category(message: types.Message):
    for name, category in array_sub_categories.items():
        if message.text in category:
            return name
    return False

async def show_sub_buttons(message: types.Message, category = False):

    if not category:
        category = message.text

    sub_subscribe = sql.cursor.execute(f"SELECT * FROM `{category}` WHERE user_id = {message.from_user.id}").fetchone()

    if sub_subscribe is None:
        sql.cursor.execute(f"INSERT INTO sub_categories(user_id) VALUES ({message.from_user.id})")
        sql.conn.commit()
        sql.cursor.execute(f"SELECT * FROM {message.text} WHERE user_id = {message.from_user.id}").fetchone()

    sub_cat_buttons = []
    for i, subscribe in enumerate(sub_subscribe[1:]):
        if subscribe == 0:
            sub_cat_buttons.append(types.KeyboardButton(emoji_off + ' ' + array_sub_categories[category][i]))
        else:
            sub_cat_buttons.append(types.KeyboardButton(emoji_on + ' ' + array_sub_categories[category][i]))
    f_sub_cat_buttons = types.ReplyKeyboardMarkup(resize_keyboard=True)
    f_sub_cat_buttons.add(*sub_cat_buttons).add('Главное меню')
    return f_sub_cat_buttons


async def sql_subscribe(message: types.Message):
    was_exist = sql.update_item_bool('categories', message.text, message.from_user.id)

    if was_exist:
        await message.answer(f'Вы успешно отписались от рассылки {message.text}')
    else:
        await message.answer(f'Вы успешно подписались на рассылку {message.text}')



# async def create_if_not_exist():
    # def get_sql_query_text():
    #     text = ''
    #     for category in array_sub_categories.values():
    #         for sub in category:
    #             text += f"`{sub}` BOOLEAN DEFAULT 0,\n"
    #     return text[:-2]
    #
    #
    # sql.cursor.execute(f"""
    #     CREATE TABLE IF NOT EXISTS sub_categories(
    #         user_id INT (10) UNIQUE NOT NULL,
    #         category TEXT NOT NULL,
    #          {get_sql_query_text()}
    #     );
    # """)
    # sql.conn.commit()
