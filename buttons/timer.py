from aiogram import types
from sqlighter import sql
from datetime import timedelta


NAME = 'Таймер уведомления'


async def start(message: types.Message):
    if message.text == NAME:
        await message.answer("Напишите что-то вроде 20 минут или 1 день 2 часа 10 минуты и минимум через это время вам будет прислано звуковое увидомление при следующем сканировании")
        return True
    elif await update_timer(message):
        await message.answer("Вы успешно обновлили таймер увидомлений")
        return True

async def update_timer(message):
    text = message.text.lower().split(' ')
    text_count = len(text)

    if text_count > 1:
        cursor = 0
        days = 0
        hours = 0
        minutes = 0

        while cursor < text_count :
            if text[cursor].isdigit():
                cursor+= 1
                type_counter = await get_type(cursor, text)
                if   type_counter == 'days': days= int(text[cursor-1])
                elif type_counter == 'hours': hours= int(text[cursor-1])
                elif type_counter == 'minutes': minutes= int(text[cursor-1])
                elif type_counter == 'not_founded': return False
                cursor += 1
            else:
                type_counter = await get_type(cursor, text)
                if   type_counter == 'days': days = 1
                elif type_counter == 'hours': hours = 1
                elif type_counter == 'minutes': minutes = 1
                elif type_counter == 'not_founded': return False
                cursor += 1

        in_seconds=  int(timedelta(days= days, hours= hours, minutes= minutes).seconds)

        if await sql_update_timer(message.from_user.id, in_seconds):
            return True
        else:
            print("С установкой таймера какая-то ошибка", message.from_user.id, message.text, sep='\n' )
            await message.answer('Произолшла ошибка, сообщите администрации')
            return True

async def get_type(cursor, text):
    if text[cursor] == 'день' or text[cursor] == 'дней' or text[cursor] == 'дня':
        return 'days'

    if text[cursor] == 'часов' or text[cursor] == 'часа' or text[cursor] == 'час':
        return 'hours'

    if text[cursor] == 'минут' or text[cursor] == 'минута' or text[cursor] == 'мин':
        return 'minutes'

    if text[cursor] == 'и' or text[cursor]=='каждый'or text[cursor]=='каждую' : return 'and'

    return 'not_founded'

async def sql_update_timer(user_id, in_seconds):
    result = sql.cursor.execute(f"UPDATE users SET timer = {in_seconds} WHERE user_id = {user_id}")
    sql.conn.commit()
    return result