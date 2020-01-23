import psycopg2

from psycopg2.extras import DictCursor



conn = psycopg2.connect(dbname='telegram_bot', user='bot',
                        password='777WhyMeLucky777', host='localhost')



class DbProcessor(object):
    # saving data into DataBase
    conn = psycopg2.connect(dbname='telegram_bot', user='bot',
                            password='777WhyMeLucky777', host='localhost')
    def save_data(self, db, table, *args):
        cursor = conn.cursor(cursor_factory=DictCursor)
        save_command = "INSERT INTO {} {}\n VALUES {};".format (table, db.get(table), args)
        print(save_command)
        cursor.execute(save_command)
        conn.commit()
        print('Saved.')

    def get_data(self):
        cursor = conn.cursor(cursor_factory=DictCursor)
        cursor.execute('SELECT * FROM clients;')
        data = ''
        for row in cursor.fetchall():
            data += 'User ID: ' + str(row.get('user_id')) + '\n'
            data += 'Name: ' + str(row.get('user_name')) + '\n'
            data += 'Last Name: ' + str(row.get('user_lastname')) + '\n'
            data += 'Birth date: ' + str(row.get('user_birth_date')) + '\n\n'
        conn.close()
        return data

    def delete_data(self, user_id):
        cursor = conn.cursor(cursor_factory=DictCursor)
        cursor.execute(
            """
            DELETE FROM clients
                WHERE user_id = {};
            """.format(user_id))
        conn.commit()

    def update_data(self,table, user_id, param, value):
        cursor = conn.cursor(cursor_factory=DictCursor)
        if param.endswith(',') or param.endswith(')'):
            param = param[:-1]
        if param[0] == '(':
            param = param[1:]
            print (param)
            sql =\
                """
                UPDATE {}
                    SET {} = '{}'
                    WHERE user_id = {}
                """.format(table, param, value, user_id)
        print(sql)
        cursor.execute(sql)
        conn.commit()



