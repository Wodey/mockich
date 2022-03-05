import psycopg2
from dotenv import load_dotenv
from os import getenv

load_dotenv()


class Database:
    def __init__(self):
        self.db = psycopg2.connect(
            f"dbname={getenv('DB_NAME')} user={getenv('DB_USER')} password={getenv('DB_PASSWORD')} host={getenv('DB_HOST')}")
        self.db.autocommit = True

    def create_user(self, data):
        with self.db.cursor() as cursor:
            cursor.execute(
                f"INSERT INTO users (name, email, nickname) VALUES {data['name'], data['email'], data['nickname']};")

    def get_user_id_by_tg_name(self, nickname):
        with self.db.cursor() as cursor:
            cursor.execute(f"SELECT id FROM users WHERE nickname = '{nickname}'")
            return cursor.fetchone()

    def create_request2meet(self, data):
        with self.db.cursor() as cursor:
            cursor.execute(
                f"INSERT into requests2meet(date, user_id, difficulty, type, companies) VALUES {data['date'], data['user_id'], data['difficulty'], data['type'], data['companies']}")

    def get_users(self):
        with self.db.cursor() as cursor:
            cursor.execute("select * from test")
            # result = cursor.execute("insert into test2 values(2, 'heyyyyy');")
            # records = cursor.fetchall()
            return cursor.fetchone()

    def initialization(self):
        with self.db.cursor() as cursor:
            # cursor.execute("DROP TABLE users;")
            # cursor.execute("DROP TABLE requests2meet;")
            # cursor.execute("DROP TABLE meetings;")

            cursor.execute("CREATE TABLE users(id SERIAL PRIMARY KEY, name VARCHAR(50), email VARCHAR(50), \
            nickname VARCHAR(30) UNIQUE NOT NULL)")
            cursor.execute("CREATE TABLE requests2meet(id SERIAL PRIMARY KEY, date VARCHAR(20), user_id INT, \
             difficulty INT, type INT, companies VARCHAR(50), \
            FOREIGN KEY(user_id) REFERENCES  users(id))")
            cursor.execute("CREATE TABLE meetings(id SERIAL PRIMARY KEY, date VARCHAR(20), user1_id INT, \
            user2_id INT, difficulty INT, type INT, link VARCHAR(100), FOREIGN KEY(user1_id) REFERENCES users(id), \
            FOREIGN KEY(user2_id) REFERENCES  users(id)) ")


if __name__ == "__main__":
    db = Database()
    print(db.get_users())
    # db.initialization()
    # db.create_user({'name': 'ivan', 'email': 'ivannewest@gmail.com', 'nickname': 'Ivannewest'})
    # print(db.get_user_id_by_tg_name('Ivannewest')[0])
    db.create_request2meet({
        'date': '11:50',
        'user_id': 1,
        "type": 2,
        'companies': 'amazon;forex',
        'difficulty': 2
    })
