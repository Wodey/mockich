from datetime import datetime, timedelta, timezone


days_of_week = {
    "Понедельник": 0,
    "Вторник": 1,
    "Среда": 2,
    "Четверг": 3,
    "Пятница": 4,
    "Суббота": 5,
    "Воскресенье": 6
}

months = ["Января", "Февраля", "Марта", "Апреля", "Мая", "Июня", "Июля", "Августа", "Сентября", "Октября", "Декабря"]

def get_date(week, day_words, hour):

    today = datetime.now().weekday()
    month = datetime.now().month
    day = datetime.now().day

    days_in_month = _get_amount_of_days_in_month()
    days_between = 7 * week + days_of_week[day_words] - today
    for i in range(days_between):
        day += 1

        if day > days_in_month:
            month += 1
            if month >= 12:
                month = 1
            day = 1
    return datetime(2022, month, day, hour, 0, tzinfo=timezone(timedelta(hours=-3)))


def _get_amount_of_days_in_month():
    date = datetime.now()
    return (date.replace(month=date.month % 12 + 1, day=1) - timedelta(days=1)).day

def get_rich_date(data):
    hour = str(data.hour)
    if len(hour) < 2:
        hour = "0" + hour

    return f"{data.day} {months[data.month - 1]} {hour}:00"

if __name__ == "__main__":
    # print(get_date(0, "Воскресенье", 12))
    # get_date(1, "Понедельник", 12)
    # get_date(1, "Вторник", 12)
    # get_date(1, "Четверг", 12)
    # get_date(1, "Пятница", 12)
    # get_date(1, "Суббота", 12)
    # get_date(1, "Воскресенье", 12)
    print(get_rich_data(datetime.now()))
