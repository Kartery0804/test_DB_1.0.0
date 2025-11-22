import pymysql
from pymysql import OperationalError

default = ("localhost","root","Pizza0804","srs_v1.0")

"""谨记自行关闭连接对象，在异常处理中做好处理"""
def connect_mysql(host, user, passwd, database):
    """建立MySQL数据库连接"""
    connection = None
    try:
        connection = pymysql.connect(
            host=host,
            user=user,
            password=passwd,
            database=database,
        )
        print("✅ 数据库连接成功")
        return connection
    except pymysql.Error as e:
        print(f"❌ 数据库连接失败: {e}")
        return None


if __name__ == "__main__":
    connect_mysql('localhost','root','123456','sys')
