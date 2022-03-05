import logging

from aiogram import Bot, Dispatcher, executor, types
from dotenv import load_dotenv
from os import getenv
from db import Database

load_dotenv()

logging.basicConfig(level=logging.INFO)

db = Database()

bot = Bot(token=getenv('BOT_TOKEN'))
dp = Dispatcher(bot)

state = {
    'page': 0,
    'name': None,
    'email': None
}


@dp.message_handler(commands=['start'])
async def welcome(message: types.Message):
    state['page'] = 0
    keyboard = types.ReplyKeyboardMarkup()
    button1 = types.KeyboardButton(text='Зарегистрироваться')
    button2 = types.KeyboardButton(text='Назначить собеседование')
    keyboard.add(button1)
    keyboard.add(button2)
    await message.answer("Привет! Я бот - помогу получить оффер с помощью пробоного собеседования \n Для начала "
                         "работы со мной, тебе нужно заполнить небольшую анкету о себе (Жми кнопку Зарегистрироваться)",
                         reply_markup=keyboard)


@dp.message_handler(lambda msg: msg.text in {'Зарегистрироваться', '/Зарегистрироваться'})
async def register(message: types.Message):
    state['page'] = 1
    await message.answer('Введи пожалуйста, свое имя')

@dp.message_handler(lambda msg: state['page'] == 1)
async def get_name(message: types.Message):
    state['page'] = 2
    state['name'] = message.text
    await message.answer('Отлично, теперь введи пожалуйста почту, чтобы мы смогли потом прислать тебе приглашение на '
                         'собеседование')

@dp.message_handler(lambda msg: state['page'] == 2)
async def get_email(message: types.Message):
    state['page'] = 3
    state['email'] = message.text
    state['tg_username'] = message.from_user.username
    keyboard = types.ReplyKeyboardMarkup()
    button1 = types.KeyboardButton(text='Да')
    button2 = types.KeyboardButton(text='Нет')
    keyboard.add(button1)
    keyboard.add(button2)

    await message.answer(f"Всё Верно?\n Имя: {state['name']} \n Email: {state['email']}", reply_markup=keyboard)

@dp.message_handler(lambda msg: state['page'] == 3 and msg.text == 'Да')
async def save_date(message: types.Message):
    #save date
    state['page'] = 0
    keyboard = types.ReplyKeyboardMarkup()
    button1 = types.KeyboardButton(text='Зарегистрироваться')
    button2 = types.KeyboardButton(text='Назначить собеседование')
    keyboard.add(button1)
    keyboard.add(button2)
    db.create_user({
        'name': state['name'],
        'email': state['email'],
        'nickname': state['tg_username']
    })
    await message.answer(f"Твоя анкета готова, теперь можешь назначить собеседование ", reply_markup=keyboard)

@dp.message_handler(lambda msg: state['page'] == 3 and msg.text == 'Нет')
async def update(message: types.Message):
    state['page'] = 4
    keyboard = types.ReplyKeyboardMarkup()
    button1 = types.KeyboardButton(text='Имя')
    button2 = types.KeyboardButton(text='Почту')
    keyboard.add(button1)
    keyboard.add(button2)
    await message.answer('Что ты хочешь поменять?', reply_markup=keyboard)

@dp.message_handler(lambda msg: state['page'] == 4 and msg.text == 'Имя')
async def update_email(message: types.Message):
    state['page'] = 5
    await message.answer('Введи желаемое имя')

@dp.message_handler(lambda msg: state['page'] == 4 and msg.text == 'Почту')
async def update_email(message: types.Message):
    state['page'] = 6
    await message.answer('Введи желаемую почту')

@dp.message_handler(lambda msg: state['page'] in {5, 6})
async def update_all(message: types.Message):
    match state['page']:
        case 5:
            state['name'] = message.text
        case 6:
            state['email'] = message.text

    state['page'] = 3
    keyboard = types.ReplyKeyboardMarkup()
    button1 = types.KeyboardButton(text='Да')
    button2 = types.KeyboardButton(text='Нет')
    keyboard.add(button1)
    keyboard.add(button2)

    await message.answer(f"Всё Верно?\n Имя: {state['name']} \n Email: {state['email']}", reply_markup=keyboard)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
