import secret
settings = {
    "API_TOKEN" : secret.API_TOKEN,
    "ADMIN_ID": secret.ADMIN_ID,
    "HOST": 'https://www.okidoki.ee',
    'HOST_POSTS': 'https://www.okidoki.ee/ru/buy/',
}

sort = {
    "best_is_top" :     "fsort=1",
    "new_is_first" :    "fsort=2",
    "old_is_top" :      "fsort=3",
    "cheaper_is_top" :  "fsort=4",
    "expensive_is_top": "fsort=5"
}

cities = [
    { 'ru' : 'Таллинн',     'eng' : "tallinn",      'cid': "cid=1",},
    { 'ru' : 'Тарту',       'eng' : "tartu",        'cid': "cid=684"},
    { 'ru' : 'Нарва',       'eng' : "narva",        'cid': "cid=252"},
    { 'ru' : 'Кохтла-Ярве', 'eng' : "kohtla_jarve", 'cid': "cid=256"},
    { 'ru' : 'Пярну',       'eng' : "parnu",        'cid': "cid=532"},
    { 'ru' : 'Йыхви',       'eng' : "johvi",        'cid': "cid=261"},
    { 'ru' : 'Маарду',      'eng' : "maardu",       'cid': "cid=11"},
    { 'ru' : 'Хапсалу',     'eng' : "haapsalu",     'cid': "cid=386"},
    { 'ru' : 'Раквере',     'eng' : "rakvere",      'cid': "cid=423"},
    { 'ru' : 'Вильянди',    'eng' : "viljandi",     'cid': "cid=815"}
]

categories  = [
    {"ru" : "Мода, стиль и красота", "eng" : "clothes" ,    "link" : "ru/buy/30/"},
    {"ru" : "Детские товары",        "eng" : "children",    "link" : "ru/buy/19/"},
    {"ru" : "Транспорт",             "eng" : "cars",        "link" : "ru/buy/16/"},
    {"ru" : "Дом и сад",             "eng" : "home",        "link" : "ru/buy/20/"},
    {"ru" : "Электроника",           "eng" : "electronics", "link" : "ru/buy/26/"},
    {"ru" : "Развлечения и хобби",   "eng" : "hobbies",     "link" : "ru/buy/23/"},
    {"ru" : "Спортивный инвентарь",  "eng" : "sport",       "link" : "ru/buy/31/"},
    {"ru" : "Животные",              "eng" : "pets",        "link" : "ru/buy/3611/"},
    {"ru" : "Всё для бизнеса",       "eng" : "business",    "link" : "ru/buy/17/"},
    {"ru" : "Услуги",                "eng" : "services",    "link" : "ru/buy/35/"},
    {"ru" : "Недвижимость",          "eng" : "realty",      "link" : "ru/buy/15/"},
    {"ru" : "Работа",                "eng" : "job",         "link" : "ru/buy/3612/"}
]

def find_item(array , key, value, query):
    for item in array:
        if item[key] == value:
            return item[query]

from aiogram import Bot, Dispatcher
bot = Bot(token=settings['API_TOKEN'])
dp = Dispatcher(bot)
