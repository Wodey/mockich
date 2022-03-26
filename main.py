import logging
from datetime import datetime, timezone, timedelta
import requests

from aiogram import Bot, Dispatcher, executor, types
from dotenv import load_dotenv
from os import getenv
load_dotenv()

logging.basicConfig(level=logging.INFO)


bot = Bot(token=getenv('BOT_TOKEN'))
dp = Dispatcher(bot)

state = {
    'page': 0,
    'name': None,
    'email': None,
    'chat_id': None,
    'times': set(),
    'companies': set()
}


@dp.message_handler(commands=['start'])
async def welcome(message: types.Message):
    state['page'] = 0
    state['chat_id'] = message.chat.id
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


    data = {
        'full_name': state['name'],
        'email': state['email'],
        'chat_id': str(message.chat.id)
    }
    print(data['email'])
    existing_user = requests.get('http://164.92.148.198:8081/user', params={'email': data['email']}).json()
    print(existing_user)
    print(message.chat.id)
    if len(existing_user) > 0:
        state['page'] = 6
        await message.answer(f"Пользователь с такой почтой уже существует!")
        await message.answer(f"Введи другую почту")
        return

    r = requests.post('http://164.92.148.198:8081/user', json=data)
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
    for i in ["11:12", "13:14", "15:16", "17:18", "19:20"]:
        keyboard.add(types.KeyboardButton(text=i))

    keyboard.add(types.KeyboardButton(text='Далее'))

    await message.answer('Выбери пожалуйста удобное время на завтра. \n Нажми на кнопку чтобы указать время как удобное \
     \n Нажми еще раз чтобы убрать время из удобных \n Когда закончишь, жми далее', reply_markup=keyboard)


@dp.message_handler(lambda msg: state['page'] == 7 and msg.text != 'Далее')
async def set_time(message: types.Message):
    h, m = int(message.text.split(':')[0]), int(message.text.split(':')[1])
    dtime = datetime(2022, 3, 25, h, m, tzinfo=timezone(timedelta(hours=-3)))
    if message.text in state['times']:
        state['times'].remove(dtime)
    else:
        state['times'].add(dtime)

    await message.answer(f"Текущее выбранное время: {' ,'.join(e.strftime('%H:%M') for e in state['times'])}")


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
        print(difficulty),
        print(message.chat.id)
        print(i.isoformat())
        print(state['intervie_type'])
        r = requests.post('http://164.92.148.198:8081/interview', json={
            "date": str(i.isoformat()),
            "chat_id": str(message.chat.id),
            "level": int(difficulty),
            "theme": state['intervie_type']
        })
    if r.status_code == 200:
        await message.answer('Отлично, мы добавили ващ запрос на встречу')
        return
    print(r.status_code)
    await message.answer('Ошибка!')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
