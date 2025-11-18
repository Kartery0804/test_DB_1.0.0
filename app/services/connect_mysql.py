import pymysql

connection =  pymysql.connect(
    host='localhost',
    user='root',
    passwd='pizza0804',
    database='demo'
)

def connect_mysql(connection,sql = None):
    try:
        # 2. 创建游标对象
        with connection.cursor() as cursor:
            
            # 4. 执行查询
            cursor.execute(sql)
            
            # 5. 获取所有结果
            results = cursor.fetchall()

            
            # 6. 打印结果
            for row in results:
                print(row)
    finally:
        # 7. 关闭连接
        connection.close()


if __name__ == "__main__":
    connect_mysql(connection)