import sqlite3


class User:


    def __init__(self, id=None, code=None, time=None):
        self.id = id
        self.code = code
        self.time = time


    def create_user(self):
        base = sqlite3.connect('base.db')
        cursor = base.cursor()
        try:
            cursor.execute('insert into users (id, code) values (?, ?)',
                            (self.id, self.code,))
            base.commit()
        except Exception:
            base.rollback()


    def set_time(self, time=float):
        base = sqlite3.connect('base.db')
        cursor = base.cursor()
        self.time = time
        time = str(time)
        try:
            cursor.execute('update users set time=? where id=?',
                            (time, self.id,))
            base.commit()
        except Exception:
            base.rollback()


    def set_code(self, code=int):
        base = sqlite3.connect('base.db')
        cursor = base.cursor()
        self.code = code
        try:
            cursor.execute('update users set code=? where id=?',
                            (code, self.id,))
            base.commit()
        except Exception:
            base.rollback()


    @classmethod
    def get_user(self, id: str):
        base = sqlite3.connect('base.db')
        cursor = base.cursor()
        user = cursor.execute('select * from users where id=?', (id,)).fetchall()
        if user:
            user = user[0]
            base.close()
            time = user[2]

            if time:
                time = float(time)

            return User(id, user[1], time)
        else:
            base.close()
            return None

    @classmethod
    def get_all(self):
        base = sqlite3.connect('base.db')
        cursor = base.cursor()
        all_users = cursor.execute('select id from users').fetchall()
        all_opened_users = [i for i in range(len(all_users))]
        for i, subscription in enumerate(all_users):
            temp_user = self.get_user(subscription[0])
            all_opened_users[i] = User(temp_user.id, temp_user.code, temp_user.time)
        base.close()
        return all_opened_users


    @classmethod
    def confirm_payment(self, code: int):
        base = sqlite3.connect('base.db')
        cursor = base.cursor()
        try:
            cursor.execute('update users set code=? where code=?', (1, code,))
            base.commit()
            return True
        except Exception:
            base.rollback()
            return False


    def remove(self):
        base = sqlite3.connect('base.db')
        cursor = base.cursor()
        try:
            cursor.execute('delete from users where id=?', (self.id,))
            base.commit()
        except Exception:
            base.rollback()
