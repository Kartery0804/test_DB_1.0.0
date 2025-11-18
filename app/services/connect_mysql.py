import pymysql
from pymysql import OperationalError

def connect_mysql(host,user,passwd,database):
    try:
        connection =  pymysql.connect(
        host=host,
        user=user,
        passwd=passwd,
        database=database
        )   
        return connection
    except:
        print("❌ 数据库连接失败: ")
    finally:
    # 确保关闭连接
        if 'connection' in locals() and connection.open:
            #connection.close()
            pass


if __name__ == "__main__":
    connect_mysql('localhost','root','123456','sys')