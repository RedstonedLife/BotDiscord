#coding: utf-8
#!/usr/bin/python3
import psycopg2, os

def createTables():
    sql =""" CREATE TABLE IF NOT EXISTS users (
            id BIGSERIAL,
            username VARCHAR,
            platform VARCHAR
        )
        """
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()

try:
    conn = psycopg2.connect(host=os.environ['host'],
                        database=os.environ['database'],
                        user=os.environ['user'],
                        password=os.environ['password'])
    createTables()
except Exception as e:
    print(e)

def add_user(id_number,user,platform='pc'):
    cursor = conn.cursor()
    sql = 'INSERT INTO users(id,username, platform) VALUES(%s, %s, %s);'
    cursor.execute(sql, (id_number, user, platform,))
    conn.commit()

    print("Added " + str(id_number) + " To database!")


def select(user_id):
    cursor = conn.cursor()
    cursor.execute("""SELECT * FROM users WHERE id=%s""",(user_id,))
    rows = cursor.fetchall()
    return rows

def change(table,user,value,newValue):
    cursor = conn.cursor()
    sql_command = '''UPDATE ''' + table + ''' SET ''' + value + '''='''+"'"+ newValue +"'"+''' WHERE id=''' + "'" + user + "'" + ''';'''
    cursor.execute(sql_command, (table, value, newValue, user))
    conn.commit()

    print("Changed " + user + "'s " + value + " value to " + newValue)
