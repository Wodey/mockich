import logging
from datetime import datetime, timezone, timedelta
import requests
from state import State
from aiogram import Bot, Dispatcher, executor, types
from dotenv import load_dotenv
from os import getenv
from utilities import get_date

SELECT_DAYS_1 = "SELECT_DAYS"
SELECT_DAYS_2 = "SELECT_DAYS_2"
SELECT_TIME_1 = "SELECT_TIME_1"

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
    if is_user_exists:
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

days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]

@dp.message_handler(lambda msg: msg.text in ['Назначить собеседование', '/interview'] or state.page == SELECT_DAYS_2  \
                                and msg.text == 'Текущая неделя' or state.page == SELECT_TIME_1 and msg.text == 'Назад')
async def schedule(message: types.Message):
    url = f"http://164.92.148.198:8081/user?chat_id={message.chat.id}"
    r = requests.get(url)
    if r.status_code != 200:
        print(r.text)

    is_user_exists = len(r.json()) > 0

    if not is_user_exists:
        return await message.answer('Прежде чем подать заявку на собеседование, зарегестрируйся!')

    if state.page not in {SELECT_DAYS_1, SELECT_DAYS_2, SELECT_TIME_1}:
        state.clear_state()

    state.page = SELECT_DAYS_1
    today = datetime.now().weekday()
    current_hour = datetime.now().hour

    keyboard = types.ReplyKeyboardMarkup()
    if today == 6 and current_hour >= 23:
        for i in days:
            keyboard.add(types.KeyboardButton(text=i))

        keyboard.add(types.KeyboardButton(text='Далее'))
        return await message.answer(f"Выбери пожалуйста удобный день на следущей неделе(на этой неделе всё занято)\nНажми на кнопку чтобы указать день как удобный\
           \nКогда закончишь, жми далее, \nВыбранное время: {', '.join(e.strftime('%A %d %H:%M') for e in state.selected_times)}", reply_markup=keyboard)

    for index, i in enumerate(days[today:]):
        if index == today and current_hour >= 23:
            continue
        keyboard.add(types.KeyboardButton(text=i))

    keyboard.add(types.KeyboardButton(text='Следущая неделя'))
    keyboard.add(types.KeyboardButton(text='Далее'))

    await message.answer(f"Выбери пожалуйста удобный день\nНажми на кнопку чтобы указать день как удобный\
    \nКогда закончишь, жми далее\nВыбранное время: {', '.join(e.strftime('%A %d %H:%M') for e in state.selected_times)}", reply_markup=keyboard)


@dp.message_handler(lambda msg: state.page == SELECT_DAYS_1 and msg.text == 'Следущая неделя')
async def set_time1(message: types.Message):
    state.page = SELECT_DAYS_2
    keyboard = types.ReplyKeyboardMarkup()
    for i in days:
        keyboard.add(types.KeyboardButton(text=i))

    keyboard.add(types.KeyboardButton(text='Текущая неделя'))
    keyboard.add(types.KeyboardButton(text='Далее'))

    await message.answer(f"Выбери пожалуйста удобный день\nНажми на кнопку чтобы указать день как удобный \
     \nКогда закончишь, жми далее\nВыбранное время: {', '.join(e.strftime('%A %d %H:%M') for e in state.selected_times)}", reply_markup=keyboard)


hours = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]

@dp.message_handler(lambda msg: state.page in {SELECT_DAYS_2, SELECT_DAYS_1} and msg.text in days)
async def set_time(message: types.Message):
    state.selected_week = 0 if state.page == SELECT_DAYS_1 else 1 # 0 for current, 1 for next
    state.selected_day = message.text

    today = datetime.now().weekday()
    hour = datetime.now().hour
    keyboard = types.ReplyKeyboardMarkup()
    for i in hours:
        if state.page == SELECT_DAYS_1 and days[today] == message.text and hour >= i:
            continue
        keyboard.add(f"{i}:00")

    keyboard.add('Назад')

    state.page = SELECT_TIME_1
    await message.answer(f"Выбери пожалуйста удобное время\nНажми на кнопку чтобы указать время как удобное \
     \nиз удобных \n Когда закончишь, жми далее\nВыбранное время: {', '.join(e.strftime('%A %d %H:%M') for e in state.selected_times)}", reply_markup=keyboard)

@dp.message_handler(lambda msg: state.page == SELECT_TIME_1 and int(msg.text.split(':')[0]) in hours)
async def set_time(message: types.Message):
    h = int(message.text.split(':')[0])
    date = get_date(state.selected_week, state.selected_day, h)
    if date in state.selected_times:
        state.selected_times.remove(date)
    else:
        state.selected_times.add(date)

    state.page = SELECT_DAYS_1
    today = datetime.now().weekday()
    current_hour = datetime.now().hour

    keyboard = types.ReplyKeyboardMarkup()
    if today == 6 and current_hour >= 23:
        for i in days:
            keyboard.add(types.KeyboardButton(text=i))

        keyboard.add(types.KeyboardButton(text='Далее'))
        return await message.answer(f"Выбери пожалуйста удобный день на следущей неделе(на этой неделе всё занято)\nНажми на кнопку чтобы указать день как удобный\
           \nКогда закончишь, жми далее, \nВыбранное время: {', '.join(e.strftime('%A %d %H:%M') for e in state.selected_times)}", reply_markup=keyboard)

    for index, i in enumerate(days[today:]):
        if index == today and current_hour >= 23:
            continue
        keyboard.add(types.KeyboardButton(text=i))

    keyboard.add(types.KeyboardButton(text='Следущая неделя'))
    keyboard.add(types.KeyboardButton(text='Далее'))
    await message.answer(f"Выбери пожалуйста удобный день\nНажми на кнопку чтобы указать день как удобный\
    \nКогда закончишь, жми далее\nВыбранное время: {', '.join(e.strftime('%A %d %H:%M') for e in state.selected_times)}",
                         reply_markup=keyboard)


@dp.message_handler(lambda msg: state.page in {SELECT_DAYS_1, SELECT_DAYS_2} and msg.text == 'Далее')
async def next_step(message: types.Message):
    if len(state.selected_times) == 0:
        state.page = SELECT_DAYS_1
        today = datetime.now().weekday()
        current_hour = datetime.now().hour

        keyboard = types.ReplyKeyboardMarkup()
        if today == 6 and current_hour >= 23:
            for i in days:
                keyboard.add(types.KeyboardButton(text=i))

            keyboard.add(types.KeyboardButton(text='Далее'))
            return await message.answer("Пожалуйста выбери, хоть какое-нибудь время на следущей неделе!")

        for index, i in enumerate(days[today:]):
            if index == today and current_hour >= 23:
                continue
            keyboard.add(types.KeyboardButton(text=i))

        keyboard.add(types.KeyboardButton(text='Следущая неделя'))
        keyboard.add(types.KeyboardButton(text='Далее'))

        return await message.answer("Пожалуйста выбери, хоть какое-нибудь время!")

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
