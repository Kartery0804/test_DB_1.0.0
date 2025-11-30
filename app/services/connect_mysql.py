import pymysql
from pymysql import OperationalError

from pymysql.constants import FIELD_TYPE

# 创建自定义转换字典，将 DATETIME 保持为字符串
conv = pymysql.converters.conversions.copy()

# 将 DATETIME 和 TIMESTAMP 类型的转换函数设为直接返回字符串
conv[FIELD_TYPE.DATETIME] = str  # 保持 DATETIME 为字符串
conv[FIELD_TYPE.TIMESTAMP] = str  # 保持 TIMESTAMP 为字符串
conv[FIELD_TYPE.DATE] = str       # 保持 DATE 为字符串
conv[FIELD_TYPE.TIME] = str       # 保持 TIME 为字符串

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
            conv=conv
        )
        print("✅ 数据库连接成功")
        return connection
    except pymysql.Error as e:
        print(f"❌ 数据库连接失败: {e}")
        return None


if __name__ == "__main__":
    connect_mysql('localhost','root','123456','sys')
