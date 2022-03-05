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
    'email': None,
    'times': set(),
    'companies': set()
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
    # save date
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


@dp.message_handler(lambda msg: msg.text in ['Назначить собеседование'])
async def schedule(message: types.Message):
    state['page'] = 7
    keyboard = types.ReplyKeyboardMarkup()
    for i in ["11-12", "13-14", "15-16", "17-18", "19-20"]:
        keyboard.add(types.KeyboardButton(text=i))

    keyboard.add(types.KeyboardButton(text='Далее'))

    await message.answer('Выбери пожалуйста удобное время на завтра. \n Нажми на кнопку чтобы указать время как удобное \
     \n Нажми еще раз чтобы убрать время из удобных \n Когда закончишь, жми далее', reply_markup=keyboard)


@dp.message_handler(lambda msg: state['page'] == 7 and msg.text != 'Далее')
async def set_time(message: types.Message):
    if message.text in state['times']:
        state['times'].remove(message.text)
    else:
        state['times'].add(message.text)

    await message.answer(f"Текущее выбранное время: {' ,'.join(e for e in state['times'])}")


@dp.message_handler(lambda msg: state['page'] == 7 and msg.text == 'Далее')
async def next_step(message: types.Message):
    state['page'] = 8
    keyboard = types.ReplyKeyboardMarkup()
    for i in ["Легкий", "Средний", "Тяжелый"]:
        keyboard.add(types.KeyboardButton(text=i))

    await message.answer('Выберите уровень подходящий уровень сложности интервью', reply_markup=keyboard)


@dp.message_handler(lambda msg: state['page'] == 8 and msg.text in ["Легкий", "Средний", "Тяжелый"])
async def difficulty_level(message: types.Message):
    state['page'] = 9
    state['difficulty_level'] = message.text
    keyboard = types.ReplyKeyboardMarkup()
    for i in ["Алгоритмы", "System design", "Python", "C++"]:
        keyboard.add(types.KeyboardButton(text=i))

    await message.answer('Какой тип интервью вас интересует?', reply_markup=keyboard)


@dp.message_handler(lambda msg: state['page'] == 9 and msg.text in ["Алгоритмы", "System design", "Python", "C++"])
async def intervie_type(message: types.Message):
    state['page'] = 10
    state['intervie_type'] = message.text

    keyboard = types.ReplyKeyboardMarkup()
    for i in ["Amazon", "Yandex", "Google", "Mail", "Далее"]:
        keyboard.add(types.KeyboardButton(text=i))

    await message.answer('Выберете интересующую вас компанию', reply_markup=keyboard)

@dp.message_handler(lambda msg: state['page'] == 10 and msg.text != 'Далее')
async def set_company(message: types.Message):
    if message.text in state['companies']:
        state['companies'].remove(message.text)
    else:
        state['companies'].add(message.text)

    await message.answer(f"Текущие выбранные компании {' ,'.join(e for e in state['companies'])}")


@dp.message_handler(lambda msg: state['page'] == 10 and msg.text == 'Далее')
async def save_request_to_meeting(message: types.Message):
    state['page'] = 11
    nickname = message.from_user.username
    user_id = db.get_user_id_by_tg_name(nickname)[0]

    match state['difficulty_level']:
        case 'Легкий':
            difficulty = 0
        case 'Средний':
            difficulty = 1
        case _:
            difficulty = 3

    # "Алгоритмы", "System design", "Python", "C++"
    match state['intervie_type']:
        case 'Алгоритмы':
            type_i = 0
        case 'System design':
            type_i = 1
        case 'Python':
            type_i = 2
        case 'C++':
            type_i = 3

    for i in state['times']:
        db.create_request2meet({
            'date': i,
            'user_id': user_id,
            'difficulty': difficulty,
            'type': type_i,
            'companies': ';'.join(list(state['companies']))
        })
    await message.answer('Отлично, мы добавили ващ запрос на встречу')

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
