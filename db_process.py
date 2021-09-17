import psycopg2

from psycopg2.extras import DictCursor



conn = psycopg2.connect(dbname='telegram_bot', user='bot',
                        password='777WhyMeLucky777', host='db', port="5432")


class DbProcessor(object):
    # saving data into DataBase   
    def save_data(table, fields, values):
        cursor = conn.cursor(cursor_factory=DictCursor)
        try:
            cursor.execute('INSERT INTO {0} ({1}) values({2});'.format(table, fields, values))
            conn.commit()
        except Exception as e:
            print(e)   
    
   
    
    def get_data(table, field, id_type, id_value):
        cursor = conn.cursor(cursor_factory=DictCursor)
        try:
            cursor.execute('SELECT {} FROM {} WHERE {}={};'.format(field, table, id_type, id_value))
            data = cursor.fetchone()
            return data
        except:
            print("nothing to show")

 
    def update_data( table, id_type, id_value, param, value):
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
                WHERE {} = {};
            """.format(table, param, value, id_type, id_value, )
        print(sql)
        cursor.execute(sql)
        conn.commit()
    
    def get_room_in (user_id):
        cursor = conn.cursor(cursor_factory=DictCursor)
        cursor.execute('SELECT day_in, mon_in, room_current, room_home FROM rooms r INNER JOIN accounts a ON r.room_id = a.room_current WHERE a.user_id = {};'.format(user_id))
        data = cursor.fetchone()
        return data

    def get_bal (user_id):
        cursor = conn.cursor(cursor_factory=DictCursor)
        cursor.execute('SELECT day_bal, mon_bal FROM rooms r INNER JOIN accounts a ON r.room_id = a.room_current WHERE a.user_id = {};'.format(user_id))
        data = cursor.fetchone()
        return data
