import psycopg2
import sys
from psycopg2.extras import DictCursor
from db_process import DbProcessor
from bot_settings import Clients_Db

table = 'clients'
name = 'Masha'
last_name = 'Hutorna'
birth_date = '2000-02-28'
data = ('Maria', 'Hutorna', '2000-02-28')
params = (Clients_Db.get(table)).split()
print(params)

processor = DbProcessor()
processor.update_data(table, 11, params[0], name)
