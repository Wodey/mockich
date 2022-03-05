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
            cursor.execute(f"INSERT INTO users (name, email, nickname) VALUES {data['name'], data['email'], data['nickname']};")

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
            nickname VARCHAR(30))")
            cursor.execute("CREATE TABLE requests2meet(id SERIAL PRIMARY KEY, date TIMESTAMP, user1_id INT, \
            user2_id INT, difficulty INT, type INT, FOREIGN KEY(user1_id) REFERENCES users(id), \
            FOREIGN KEY(user2_id) REFERENCES  users(id))")
            cursor.execute("CREATE TABLE meetings(id SERIAL PRIMARY KEY, date TIMESTAMP, user1_id INT, \
            user2_id INT, difficulty INT, type INT, link VARCHAR(100), FOREIGN KEY(user1_id) REFERENCES users(id), \
            FOREIGN KEY(user2_id) REFERENCES  users(id)) ")


if __name__ == "__main__":
    db = Database()
    print(db.get_users())
    # db.initialization()
    db.create_user({'name': 'ivan', 'email': 'ivannewest@gmail.com', 'nickname': 'Ivannewest'})
