import json
import pymysql
from typing import Optional
from datetime import datetime, date
from decimal import Decimal
#静态检查
import pymysql.cursors





#SELECT
"""不可直接序列号化,但可以用于通过pymysql添加数据条目"""
def mysql_select_dict(connection: pymysql.Connection, table_name: str, where_arg: dict = None):
    """
    执行参数化查询,防止SQL注入
    
    Args:
        connection: 数据库连接（由外部管理）
        table_name: 表名
        where_arg: 查询条件字典，例如 {'id': 1, 'name': 'test'}
    """
    cursor:Optional[pymysql.cursors.Cursor] = None
    try:
        # 构建基础SQL语句
        sql = f"SELECT * FROM {table_name}"
        params = ()
        
        # 如果有查询条件，添加WHERE子句
        if where_arg and isinstance(where_arg, dict):
            where_conditions = []
            where_values = []
            for key, value in where_arg.items():
                where_conditions.append(f"{key} = %s")
                where_values.append(value)
            
            if where_conditions:
                sql += " WHERE " + " AND ".join(where_conditions)
                params = tuple(where_values)
        
        # 创建游标并执行参数化查询
        cursor = connection.cursor()
        cursor.execute(sql, params)
        
        print("查询成功")

        data_dict = {"column_name": [],"data": []}

        # 获取列名
        if cursor.description:
            data_dict["column_name"] = [desc[0] for desc in cursor.description]
        
        # 分批读取数据
        while True:
            rows = cursor.fetchmany(size=100)
            if not rows:
                break
            for row in rows:
                data_dict["data"].append(row)
        return data_dict
                        
    except Exception as e:
        print(f"执行查询时发生错误: {e}")
    finally:
        # 只关闭游标，不关闭连接
        if cursor:
            cursor.close()


"""可直接序列号化"""
def mysql_select_json(connection: pymysql.Connection, table_name: str, where_arg: dict = None):
    """
    执行参数化查询,返回可JSON序列化的数据
    """
    def convert_value(value):
        """转换单个值为JSON可序列化的类型"""
        if isinstance(value, (datetime, date)):
            return value.isoformat()
        elif isinstance(value, Decimal):
            return float(value)
        else:
            return value
    
    cursor:Optional[pymysql.cursors.Cursor] = None
    try:
        # 构建SQL（同原代码）
        sql = f"SELECT * FROM {table_name}"
        params = ()
        
        if where_arg and isinstance(where_arg, dict):
            where_conditions = []
            where_values = []
            for key, value in where_arg.items():
                where_conditions.append(f"{key} = %s")
                where_values.append(value)
            
            if where_conditions:
                sql += " WHERE " + " AND ".join(where_conditions)
                params = tuple(where_values)
        
        # 执行查询
        cursor = connection.cursor()
        cursor.execute(sql, params)
        
        # 构建返回数据
        data_dict = {"column_name": [], "data": []}
        
        # 获取列名
        if cursor.description:
            data_dict["column_name"] = [desc[0] for desc in cursor.description]
        # 分批读取并转换数据
        while True:
            rows = cursor.fetchmany(size=100)
            if not rows:
                break
            
            for row in rows:
                # 转换每行中的特殊类型
                converted_row = [convert_value(value) for value in row]
                data_dict["data"].append(converted_row)
        
        print("查询成功")
        return data_dict
        
    except Exception as e:
        print(f"执行查询时发生错误: {e}")
        return {"column_name": [], "data": []}
    finally:
        if cursor:
            cursor.close()

"""下标搜索"""
def find_column_index(lst, target_string):
    """
    在列表中搜索字符串并返回下标
    
    参数:
    lst -- 要搜索的列表
    target_string -- 要查找的字符串
    
    返回:
    如果找到，返回字符串的下标；如果找不到，返回-1
    """
    try:
        return lst.index(target_string)
    except ValueError:
        return -1

if __name__ == '__main__':
    
    # 使用示例
    from app.services import connect_mysql as cm, operation_mysql as om
    from app.services import with_mysql as wm

    #开启数据库服务
    wm.start_mysql_service()
    #创建连接
    
    conn = cm.connect_mysql("localhost","root","Pizza0804","srs_v1.0")

    # 安全查询 - 使用参数化
    print(json.dumps(mysql_select_json(conn, "sys_user", {"username": "kartery"}), ensure_ascii=False, indent=4))
    print("---------------------------------------------------------------------------")
    print(type(mysql_select_dict(conn, "sys_user",{"username": "kartery"})['data']))

    #关闭连接
    conn.close()
