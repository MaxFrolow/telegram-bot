import psycopg2

from psycopg2.extras import DictCursor



conn = psycopg2.connect(dbname='telegram_bot', user='bot',
                        password='777WhyMeLucky777', host='db', port="5432")



class DbProcessor(object):
    # saving data into DataBase   
    def save_data(table, fields, values):
        cursor = conn.cursor(cursor_factory=DictCursor)
        try:
            cursor.execute('INSERT INTO {0} ({1}) values({1});'.format(table, fields, values))
            conn.commit()
        except Exception as e:
            print(e)   
    
   
    
    def get_data(table, id_type, id_value):
        cursor = conn.cursor(cursor_factory=DictCursor)
        try:
            cursor.execute('SELECT * FROM {0} WHERE {1}={2};'.format(table, id_type, id_value))
            data = cursor.fetchone()
            return data
        except:
            print("nothing to show")

 
    def update_data( table, id_type, id_value, password, param, value):
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


