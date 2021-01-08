from aiogram import types
from sqlighter import sql
import buttons.button_menu as button_menu

SUBSCRIBE = 'Подписаться'
UNSUBSCRIBE = 'Отписаться'
SUBSCRIBE_UNSUBSCRIBE = 'Подписка/Отписка'


subscribe_button = types.ReplyKeyboardMarkup(resize_keyboard=False).add(SUBSCRIBE)
unsubscribe_button = types.ReplyKeyboardMarkup(resize_keyboard=False).add(UNSUBSCRIBE)


async def start(message: types.Message):
    if message.text == SUBSCRIBE_UNSUBSCRIBE:
        subscribe_status = await get_user_subscribe_status(message)
        if subscribe_status:
            await message.answer("Сейчас вы подписаны на расслыку", reply_markup=unsubscribe_button)
        else:
            await message.answer("Сейчас вы не подписаны на расслыку", reply_markup= subscribe_button)
        return True
    elif message.text == SUBSCRIBE:
        await subscribe(message)
        return True
    elif message.text == UNSUBSCRIBE:
        await unsubscribe(message)
        return True

async def get_user_subscribe_status(message):
    try:
        return sql.cursor.execute(f"SELECT subscription FROM users WHERE user_id = {message.from_user.id}").fetchone()[0]
    except:
        sql.add_new_user(message.from_user)
        return False

# Команда подписки
async def subscribe(message: types.Message):

    is_enabled = sql.cursor.execute(f"SELECT subscription FROM users WHERE user_id={message.chat.id}").fetchone()[0]
    if is_enabled:
        await message.answer("Вы уже подписались на рассылку!", reply_markup=button_menu.BUTTON_MENU)
    else:
        sql.update_subscription(message.from_user.id, True)
        await message.answer("Вы успешно подписались на рассылку!", reply_markup=button_menu.BUTTON_MENU)



# Команда отписки
async def unsubscribe(message: types.Message):
    if sql.user_exists(message.from_user.id):
        # если он уже есть, то просто обновляем ему статус подписки
        sql.update_subscription(message.from_user.id, False)
        await message.answer("Вы успешно отписаны от рассылки.", reply_markup=button_menu.BUTTON_MENU)
    else:
        # если юзера нет в базе, добавляем его с неактивной подпиской (запоминаем)
        sql.add_new_user(message.from_user, False)
        await message.answer("Вы итак не подписаны.", reply_markup=button_menu.BUTTON_MENU)