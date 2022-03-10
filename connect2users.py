from db import Database
from meetings_controller import Google_controller

db = Database()

gc = Google_controller()


def connect2users():
    all_requests = db.get_requests2meet()
    print(all_requests)
    while len(all_requests) > 1:
        # id, user_id, date, difficulty, type, companies
        last_request = all_requests.pop()
        match = None
        for i in all_requests:
            if i[1] != last_request[1] and i[2] == last_request[2] and i[3] == last_request[3]:
                match = i

        if not match:
            continue

        user1 = db.get_user_by_id(last_request[1])[0]
        print(user1)
        user2 = db.get_user_by_id(match[1])[0]
        print(user2)
        event_body = gc.generate_event_body(f"Пробное собеседование",
                                            f"Привет, это бот Mockich. Поздравляю! У тебя получился match и мы смогли найти тебе партнера для пробного собеседования",
                                            match[2], user1[2], user2[2])
        link = gc.new_event(event_body)

        db.create_meeting({
            'date': match[2],
            'user1_id': match[1],
            'user2_id': last_request[1],
            'difficulty': last_request[3],
            'type': last_request[4],
            'link': link
        })

        db.delete_requests2meet(match[0])
        db.delete_requests2meet(last_request[0])

    return


if __name__ == "__main__":
    connect2users()
