import pymysql
from flask import jsonify

def safe_mysql_query(connection: pymysql.connections.Connection ,user_input):
    if connection.open == True:
        conn = pymysql.connect(host='localhost', user='user', password='pass', database='test')
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE name = %s", (user_input,))
        return cursor.fetchall()
    else:
        return ('error','unconnection')