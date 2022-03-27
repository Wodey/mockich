import logging
from datetime import datetime, timezone, timedelta
import requests
from state import State
from aiogram import Bot, Dispatcher, executor, types
from dotenv import load_dotenv
from os import getenv

load_dotenv()

logging.basicConfig(level=logging.INFO)


bot = Bot(token=getenv('BOT_TOKEN'))
dp = Dispatcher(bot)


state = State(page=0)

@dp.message_handler(commands=['help'])
async def help(message: types.Message):
    await message.answer("/register - чтобы заполнить базовую информацию о себе(не доступна, еслы вы уже "
                         "зарегистрировались) \n /interview - чтобы создать запрос на пробное собеседование"
                         "(чтобы её использовать вам нужна заполненная анкета с базовой информацией о себе)")

@dp.message_handler(commands=['start'])
async def welcome(message: types.Message):
    state.page = 0
    state.clear_state()

    url = f"http://164.92.148.198:8081/user?chat_id={message.chat.id}"
    r = requests.get(url)
    if r.status_code != 200:
        print(r.text)

    is_user_exists = len(r.json()) > 0

    keyboard = types.ReplyKeyboardMarkup()
    button1 = types.KeyboardButton(text='Зарегистрироваться')
    if not is_user_exists:
        keyboard.add(button1)
    button2 = types.KeyboardButton(text='Назначить собеседование')
    keyboard.add(button2)

    if is_user_exists:
        return await message.answer("Привет! Я бот - помогу получить оффер с помощью пробоного собеседования \n"
                             "Чтобы найти партнера для собеседования жми кнопку 'Назначить собеседование'",
                             reply_markup=keyboard)
    await message.answer("Привет! Я бот - помогу получить оффер с помощью пробоного собеседования \n Для начала "
                         "работы со мной, тебе нужно заполнить небольшую анкету о себе (Жми кнопку Зарегистрироваться)",
                         reply_markup=keyboard)


@dp.message_handler(lambda msg: msg.text in {'Зарегистрироваться', '/Зарегистрироваться', '/register'})
async def register(message: types.Message):

    state.clear_state()

    url = f"http://164.92.148.198:8081/user?chat_id={message.chat.id}"
    r = requests.get(url)
    if r.status_code != 200:
        print(r.text)

    is_user_exists = len(r.json()) > 0

    if is_user_exists:
        return await message.answer('Вы уже зарегистрировались! Хотите что-то поменять?')

    state.page = 1
    await message.answer('Введи пожалуйста, свое имя')


@dp.message_handler(lambda msg: state.page == 1)
async def get_name(message: types.Message):
    state.page = 2
    state.full_name = message.text
    await message.answer('Отлично, теперь введи пожалуйста почту, чтобы мы смогли потом прислать тебе приглашение на '
                         'собеседование')


@dp.message_handler(lambda msg: state.page == 2)
async def get_email(message: types.Message):
    state.page = 3
    state.email = message.text
    keyboard = types.ReplyKeyboardMarkup()
    button1 = types.KeyboardButton(text='Да')
    button2 = types.KeyboardButton(text='Нет')
    keyboard.add(button1)
    keyboard.add(button2)

    await message.answer(f"Всё Верно?\n Имя: {state.full_name} \n Email: {state.email}", reply_markup=keyboard)


@dp.message_handler(lambda msg: state.page == 3 and msg.text == 'Да')
async def save_date(message: types.Message):
    # save date
    state.page = 0
    keyboard = types.ReplyKeyboardMarkup()
    button1 = types.KeyboardButton(text='Зарегистрироваться')
    button2 = types.KeyboardButton(text='Назначить собеседование')
    keyboard.add(button1)
    keyboard.add(button2)


    data = {
        'full_name': state.full_name,
        'email': state.email,
        'chat_id': str(message.chat.id)
    }
    r = requests.get('http://164.92.148.198:8081/user', params={'email': data['email']})
    if r.status_code != 200:
        print(r.text)

    existing_user = r.json()
    if len(existing_user) > 0:
        state.page = 6
        await message.answer(f"Пользователь с такой почтой уже существует!")
        await message.answer(f"Введи другую почту")
        return

    r = requests.post('http://164.92.148.198:8081/user', json=data)
    if r.status_code != 200:
        print(r.text)
        return await message.answer('Ошибка!')
    state.clear_state()

    url = f"http://164.92.148.198:8081/user?chat_id={message.chat.id}"
    r_2 = requests.get(url)
    is_user_exists = len(r_2.json()) > 0

    keyboard = types.ReplyKeyboardMarkup()
    button1 = types.KeyboardButton(text='Зарегистрироваться')
    if not is_user_exists:
        keyboard.add(button1)
    button2 = types.KeyboardButton(text='Назначить собеседование')
    keyboard.add(button2)

    await message.answer(f"Твоя анкета готова, теперь можешь назначить собеседование ", reply_markup=keyboard)


@dp.message_handler(lambda msg: state.page == 3 and msg.text == 'Нет')
async def update(message: types.Message):
    state.page = 4
    keyboard = types.ReplyKeyboardMarkup()
    button1 = types.KeyboardButton(text='Имя')
    button2 = types.KeyboardButton(text='Почту')
    keyboard.add(button1)
    keyboard.add(button2)
    await message.answer('Что ты хочешь поменять?', reply_markup=keyboard)


@dp.message_handler(lambda msg: state.page == 4 and msg.text == 'Имя')
async def update_email(message: types.Message):
    state.page = 5
    await message.answer('Введи желаемое имя')


@dp.message_handler(lambda msg: state.page == 4 and msg.text == 'Почту')
async def update_email(message: types.Message):
    state.page = 6
    await message.answer('Введи желаемую почту')


@dp.message_handler(lambda msg: state.page in {5, 6})
async def update_all(message: types.Message):
    match state.page:
        case 5:
            state.full_name = message.text
        case 6:
            state.email = message.text

    state.page = 3
    keyboard = types.ReplyKeyboardMarkup()
    button1 = types.KeyboardButton(text='Да')
    button2 = types.KeyboardButton(text='Нет')
    keyboard.add(button1)
    keyboard.add(button2)

    await message.answer(f"Всё Верно?\n Имя: {state.full_name} \n Email: {state.email}", reply_markup=keyboard)


@dp.message_handler(lambda msg: msg.text in ['Назначить собеседование', '/interview'])
async def schedule(message: types.Message):
    state.page = 7
    keyboard = types.ReplyKeyboardMarkup()
    for i in ["11:12", "13:14", "15:16", "17:18", "19:20"]:
        keyboard.add(types.KeyboardButton(text=i))

    keyboard.add(types.KeyboardButton(text='Далее'))

    await message.answer('Выбери пожалуйста удобное время на завтра. \n Нажми на кнопку чтобы указать время как удобное \
     \n Нажми еще раз чтобы убрать время из удобных \n Когда закончишь, жми далее', reply_markup=keyboard)


@dp.message_handler(lambda msg: state.page == 7 and msg.text != 'Далее')
async def set_time(message: types.Message):
    h, m = int(message.text.split(':')[0]), int(message.text.split(':')[1])
    dtime = datetime(2022, 3, 25, h, m, tzinfo=timezone(timedelta(hours=-3)))
    if dtime in state.selected_times:
        state.selected_times.remove(dtime)
    else:
        state.selected_times.add(dtime)

    await message.answer(f"Текущее выбранное время: {' ,'.join(e.strftime('%H:%M') for e in state.selected_times)}")


@dp.message_handler(lambda msg: state.page == 7 and msg.text == 'Далее')
async def next_step(message: types.Message):
    state.page = 8
    keyboard = types.ReplyKeyboardMarkup()
    for i in ["Легкий", "Средний", "Тяжелый"]:
        keyboard.add(types.KeyboardButton(text=i))

    await message.answer('Выберите уровень подходящий уровень сложности интервью', reply_markup=keyboard)


@dp.message_handler(lambda msg: state.page == 8 and msg.text in ["Легкий", "Средний", "Тяжелый"])
async def difficulty_level(message: types.Message):
    state.page = 9
    state.difficulty_level = message.text
    keyboard = types.ReplyKeyboardMarkup()
    for i in ["Алгоритмы", "System design", "Python", "C++"]:
        keyboard.add(types.KeyboardButton(text=i))

    await message.answer('Какой тип интервью вас интересует?', reply_markup=keyboard)


@dp.message_handler(lambda msg: state.page == 9 and msg.text in ["Алгоритмы", "System design", "Python", "C++"])
async def intervie_type(message: types.Message):
    state.page = 10
    state.theme = message.text

    keyboard = types.ReplyKeyboardMarkup()
    for i in ["Amazon", "Yandex", "Google", "Mail", "Далее"]:
        keyboard.add(types.KeyboardButton(text=i))

    await message.answer('Выберете интересующую вас компанию', reply_markup=keyboard)


@dp.message_handler(lambda msg: state.page == 10 and msg.text != 'Далее')
async def set_company(message: types.Message):
    if message.text in state.companies:
        state.companies.remove(message.text)
    else:
        state.companies.add(message.text)

    await message.answer(f"Текущие выбранные компании {' ,'.join(e for e in state.companies)}")


@dp.message_handler(lambda msg: state.page == 10 and msg.text == 'Далее')
async def save_request_to_meeting(message: types.Message):
    state.page = 11

    match state.difficulty_level:
        case 'Легкий':
            difficulty = 0
        case 'Средний':
            difficulty = 1
        case _:
            difficulty = 3

    for i in state.selected_times:
        r = requests.post('http://164.92.148.198:8081/interview', json={
            "date": str(i.isoformat()),
            "chat_id": str(message.chat.id),
            "level": int(difficulty),
            "theme": state.theme
        })
    if r.status_code == 200:
        state.clear_state()
        await message.answer('Отлично, мы добавили ващ запрос на встречу')
        return
    print(r.text)
    await message.answer('Ошибка!')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
