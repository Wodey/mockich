from db import Database

db = Database()


def connect2users():
    all_requests = db.get_requests2meet()
    print(all_requests)
    while len(all_requests) > 1:
        last_request = all_requests.pop()
        match = None
        for i in all_requests:
            if i[1] != last_request[1] and i[2] == last_request[2] and i[3] == last_request[3]:
                match = i

        if not match:
            continue

        db.create_meeting({
            'date': match[2],
            'user1_id': match[1],
            'user2_id': last_request[1],
            'difficulty': last_request[3],
            'type': last_request[4],
            'link': "LOREM IPSUM"
        })

        db.delete_requests2meet(match[0])
        db.delete_requests2meet(last_request[0])

    return


if __name__ == "__main__":
    connect2users()
