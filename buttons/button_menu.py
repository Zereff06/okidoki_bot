import config
from aiogram import types

import buttons.city
import buttons.category
import buttons.subscribe
import buttons.timer

dp = config.dp
bot = config.bot

BUTTON_MENU = types.ReplyKeyboardMarkup(resize_keyboard=False)
BUTTON_MENU.add(types.InlineKeyboardButton(buttons.city.NAME))
BUTTON_MENU.add(types.InlineKeyboardButton(buttons.category.NAME))
BUTTON_MENU.add(types.InlineKeyboardButton(buttons.timer.NAME))
BUTTON_MENU.add(types.InlineKeyboardButton(buttons.subscribe.NAME))

async def start(message: types.Message):
    if message.text == 'Главное меню':
        await menu(message)
        return True


@dp.message_handler(commands=['menu'])
async def menu(message: types.Message):
    await message.answer('Главное меню:', reply_markup=BUTTON_MENU)