import config
from aiogram import types

import buttons.city
import buttons.category
import buttons.subscribe

dp = config.dp
bot = config.bot

BUTTON_MENU = types.ReplyKeyboardMarkup(resize_keyboard=False)
BUTTON_MENU.add(types.InlineKeyboardButton('Выбор города'))
BUTTON_MENU.add(types.InlineKeyboardButton('Выбор категории'))
BUTTON_MENU.add(types.InlineKeyboardButton('Таймер уведомления'))
BUTTON_MENU.add(types.InlineKeyboardButton('Подписка/Отписка'))

async def start(message: types.Message):
    if message.text == 'Главное меню':
        await menu(message)
        return True


@dp.message_handler(commands=['menu'])
async def menu(message: types.Message):
    await message.answer('Настройки бота:', reply_markup=BUTTON_MENU)