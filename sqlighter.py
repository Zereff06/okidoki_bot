import sqlite3
import datetime


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
        						user_id         INT (10)    NOT NULL ,
        						first_name      TEXT        DEFAULT 'empty',
        						last_name       TEXT        DEFAULT 'empty',
        						subscription    BOOLEAN     DEFAULT 1,
        						permissions     TEXT        DEFAULT 'empty',
                                timer           INT         DEFAULT 1750       NOT NULL,
                                last_timer_time DATETIME
        					);
        					""")
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS premium (
        						category        TEXT        NOT NULL ,
        						city            TEXT        NOT NULL,
        						link            TEXT        NOT NULL    UNIQUE 
        					);
        					""")
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS blacklist (
        						link            TEXT        NOT NULL UNIQUE,
        						category        TEXT        NOT NULL,
        						city            TEXT        NOT NULL     
        					);
        					""")

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
                                user_id     INT (10) NOT NULL UNIQUE,
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
                            user_id         INT (10)    NOT NULL UNIQUE,
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

            # city
            in_bd = self.cursor.execute(f"SELECT user_id FROM cities WHERE user_id = {user.id}").fetchone()
            if not in_bd:
                self.cursor.execute(f"INSERT INTO cities(user_id) VALUES({user.id})")

            # category
            in_bd = self.cursor.execute(f"SELECT user_id FROM categories WHERE user_id = {user.id}").fetchone()
            if not in_bd:
                self.cursor.execute(f"INSERT INTO categories(user_id)  VALUES({user.id})")

            self.conn.commit()
            return bool(result)

    def update_subscription(self, user_id, status):
        """Обновляем статус подписки пользователя"""
        result = self.cursor.execute(f"UPDATE users SET subscription = {status} WHERE user_id = {user_id}")
        self.conn.commit()
        return bool(result)

    def update_item_bool(self, table, item, user_id):
        # Проверка, есть ли юзер вообще в таблице
        user_exist_in_table = self.cursor.execute(f"SELECT EXISTS(SELECT user_id FROM {table} WHERE  user_id = {user_id} )").fetchone()[0]
        if not user_exist_in_table:
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
            return self.cursor.execute(f"SELECT {cell} FROM {table} WHERE user_id={user_id}")

    # can delete...
    def get_unique_items(self, cell):
        """Вернёт только уникальные значения из выборки"""
        return self.cursor.execute(f"SELECT {cell} FROM table  GROUP BY {cell}")


    def get_table_params(self, tables, params=''):
        """Достать все данные из таблицы с улсовием"""
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

    def update_last_notification_timer(self, user_id):
        self.cursor.execute(f"UPDATE users SET last_timer_time = '{datetime.datetime.now()}' WHERE user_id = {user_id}")
        self.conn.commit()

    def check_user_notification_timer(self, user_id):
        timer = self.cursor.execute(f"SELECT timer FROM users WHERE user_id = {user_id}").fetchone()[0]
        result = self.cursor.execute(f"""
            SELECT user_id 
            FROM users
            WHERE  last_timer_time < '{datetime.datetime.now() - datetime.timedelta(seconds=timer)}'
        """).fetchone()

        if result is None:
            result = False
        else:
            result = result[0]
            self.update_last_notification_timer(result)
        return result

    def sql_get_name_and_value (self, query):
        sql_result = sql.cursor.execute(query)
        if sql_result:
            sql_values = sql_result.fetchone()
            result = {v[0]:sql_values[i] for i,v in enumerate(sql_result.description)}
            return result
        else :
            print(f'Ошибка с запросом: {query}')
            return False


sql = SQLighter('server.db')
