import sqlite3


class SQLighter:

    def __init__(self, database):
        """Подключаемся к БД и сохраняем курсор соединения"""
        with  sqlite3.connect(database) as self.conn:
            self.cursor = self.conn.cursor()

    def close(self):
        """Закрываем соединение с БД до пересоздания объекта..."""
        self.conn.close()

    def create_table_if_no_exist(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
        						user_id         INT         NOT NULL ,
        						first_name      TEXT        DEFAULT 'empty',
        						last_name       TEXT        DEFAULT 'empty',
        						subscription    BOOLEAN     DEFAULT 1,
        						permissions     TEXT        DEFAULT 'empty'
        						
        					);
        					""")
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS premium (
        						category        TEXT        NOT NULL ,
        						city            TEXT        NOT NULL,
        						link            TEXT        NOT NULL
        					);
        					""")

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
                                user_id     INT         NOT NULL UNIQUE,
                                clothes     BOOLEAN  DEFAULT 0,
                                children    BOOLEAN  DEFAULT 0,
                                cars        BOOLEAN  DEFAULT 0,
                                home        BOOLEAN  DEFAULT 0,
                                electronics BOOLEAN  DEFAULT 0,
                                hobbies     BOOLEAN  DEFAULT 0,
                                sport       BOOLEAN  DEFAULT 0,
                                pets        BOOLEAN  DEFAULT 0,
                                business    BOOLEAN  DEFAULT 0,
                                services    BOOLEAN  DEFAULT 0,
                                realty      BOOLEAN  DEFAULT 0,
                                job         BOOLEAN  DEFAULT 0
                            );
        					""")

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS cities (
                            user_id         INT         NOT NULL UNIQUE,
                            tallinn         BOOLEAN     DEFAULT 0,
                            tartu           BOOLEAN     DEFAULT 0,
                            narva           BOOLEAN     DEFAULT 0,
                            kohtla_jarve    BOOLEAN     DEFAULT 0,
                            parnu           BOOLEAN     DEFAULT 0,
                            johvi           BOOLEAN     DEFAULT 0,
                            maardu          BOOLEAN     DEFAULT 0,
                            haapsalu        BOOLEAN     DEFAULT 0,
                            rakvere         BOOLEAN     DEFAULT 0,
                            viljandi        BOOLEAN     DEFAULT 0
            );
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                                id                      INTEGER PRIMARY KEY ,
                                category                TEXT    NOT NULL ,
                                city                    TEXT    NOT NULL , 
                                last_post               TEXT    DEFAULT 'empty',
                                before_last_post        TEXT    DEFAULT 'empty',
                                before_before_last_post TEXT    DEFAULT 'empty'
            );
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS inore_posts(
                link TEXT(200) UNIQUE NOT NULL,
                data DATE,
                forever BOOLEAN DEFAULT(0)
            );
        """)
        self.conn.commit()

    def get_users(self, status="True"):
        """Получаем всех активных подписчиков бота"""
        with self.conn:
            return self.cursor.execute(f"SELECT * FROM users WHERE subscribe = {status}").fetchall()

    def user_exists(self, user_id):
        """Проверяем, есть ли уже юзер в базе"""
        with self.conn:
            result = self.cursor.execute(f"SELECT * FROM users WHERE user_id = {user_id}").fetchall()
            return bool(len(result))

    def add_new_user(self, user, status=True):
        """Добавляем нового подписчика"""
        with self.conn:
            result = self.cursor.execute(
                f"INSERT INTO users(user_id,first_name,last_name )  VALUES({user.id}, '{user.first_name}', '{user.last_name}')")
            self.cursor.execute(f"INSERT INTO cities(user_id) VALUES({user.id})")
            self.cursor.execute(f"INSERT INTO categories(user_id)  VALUES({user.id})")
            self.conn.commit()
            return bool(result)

    def update_subscription(self, user_id, status):
        """Обновляем статус подписки пользователя"""
        with self.conn:
            result = self.cursor.execute(f"UPDATE users SET subscription = {status} WHERE user_id = {user_id}")
            self.conn.commit()
            return bool(result)

    def update_item_bool(self, table, item, user_id):
        with self.conn:
            # Проверка, есть ли юзер вообще в таблице
            user_exist_in_table = self.cursor.execute(
                f"SELECT EXISTS(SELECT user_id FROM {table} WHERE  user_id = {user_id} )").fetchone()
            if not user_exist_in_table[0]:
                print(f"INSERT INTO {table}(user_id) VALUES ({user_id})")
                self.cursor.execute(f"INSERT INTO {table}(user_id) VALUES ({user_id})")
                self.conn.commit()

            # Если есть значение в таблице,то вернёт True
            is_exist_item = self.cursor.execute(f"SELECT {item} FROM {table} WHERE  user_id = {user_id}").fetchone()
            is_exist_item = is_exist_item[0]
            if is_exist_item:
                self.cursor.execute(f"UPDATE {table} SET {item} = 0 WHERE user_id = {user_id}")
                self.conn.commit()
                return True
            else:
                self.cursor.execute(f"UPDATE {table} SET {item} = 1 WHERE user_id = {user_id}")
                self.conn.commit()
                return False

    def get_users_data(self, table, cell, user_id):
        with self.conn:
            return self.cursor.execute(f"SELECT {cell} FROM {table} WHERE user_id={user_id}")

    # can delete...
    def get_unique_items(self, cell):
        """Вернёт только уникальные значения из выборки"""
        with self.conn:
            return self.cursor.execute(f"SELECT {cell} FROM table  GROUP BY {cell}")

    def get_table(self, table):
        """Достать все данные из таблицы"""
        with self.conn:
            data_table = self.cursor.execute(f"SELECT * FROM {table}")
            names = list(map(lambda x: x[0], data_table.description))
            category_dict = {}

            values = data_table.fetchall()
            for i, category in enumerate(names):
                if i == 0: continue
                users_array = []
                for user in values:
                    if user[i] == 1: users_array.append(user[0])
                category_dict[names[i]] = users_array
            return category_dict

    def get_table_params(self, tables, params=''):
        """Достать все данные из таблицы с улсовием"""
        with self.conn:
            data_table = self.cursor.execute(f"SELECT * FROM {tables}  WHERE {params}")
            names = list(map(lambda x: x[0], data_table.description))
            category_dict = {}

            values = data_table.fetchall()
            for i, category in enumerate(names):
                if i == 0: continue
                users_array = []
                for user in values:
                    if user[i] == 1: users_array.append(user[0])
                category_dict[names[i]] = users_array
            return category_dict


sql = SQLighter('server.db')
