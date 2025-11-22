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
        raise
    finally:
        # 只关闭游标，不关闭连接
        if cursor:
            cursor.close()

"""可直接序列化"""
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

"""支持比较运算符"""
def mysql_select_dict_enhanced(connection: pymysql.Connection, table_name: str, 
                              where_arg: dict = None, 
                              order_by: str = None,
                              limit: int = None):
    """
    增强版参数化查询，支持比较运算符和其他高级功能
    
    Args:
        connection: 数据库连接（由外部管理）
        table_name: 表名
        where_arg: 查询条件字典，支持以下格式：
                  - 等值比较: {'id': 1, 'name': 'test'}
                  - 比较运算符: {'age': ('>', 18), 'score': ('<=', 100)}
                  - LIKE操作: {'name': ('LIKE', '%张%')}
                  - IN操作: {'id': ('IN', [1, 2, 3])}
                  - BETWEEN操作: {'age': ('BETWEEN', [18, 30])}
        order_by: 排序字段，例如 'id DESC' 或 'name ASC'
        limit: 限制返回记录数
    
    Returns:
        dict: 包含列名和数据的字典
    """
    cursor: Optional[pymysql.cursors.Cursor] = None
    try:
        # 构建基础SQL语句
        sql = f"SELECT * FROM {table_name}"
        params = ()
        
        # 构建WHERE子句（支持比较运算符）
        if where_arg and isinstance(where_arg, dict):
            where_conditions = []
            where_values = []
            
            for key, condition in where_arg.items():
                if isinstance(condition, tuple) and len(condition) == 2:
                    # 处理带运算符的条件
                    operator, value = condition
                    operator = operator.upper()
                    
                    if operator in ['=', '!=', '<', '>', '<=', '>=', 'LIKE', 'NOT LIKE']:
                        where_conditions.append(f"{key} {operator} %s")
                        where_values.append(value)
                    elif operator == 'IN':
                        # IN 操作需要特殊处理
                        if isinstance(value, (list, tuple)):
                            placeholders = ','.join(['%s'] * len(value))
                            where_conditions.append(f"{key} IN ({placeholders})")
                            where_values.extend(value)
                        else:
                            raise ValueError("IN操作符的值必须是列表或元组")
                    elif operator == 'BETWEEN':
                        # BETWEEN 操作需要特殊处理
                        if isinstance(value, (list, tuple)) and len(value) == 2:
                            where_conditions.append(f"{key} BETWEEN %s AND %s")
                            where_values.extend(value)
                        else:
                            raise ValueError("BETWEEN操作符的值必须是包含2个元素的列表或元组")
                    elif operator == 'IS NULL':
                        where_conditions.append(f"{key} IS NULL")
                    elif operator == 'IS NOT NULL':
                        where_conditions.append(f"{key} IS NOT NULL")
                    else:
                        raise ValueError(f"不支持的运算符: {operator}")
                else:
                    # 默认使用等值比较
                    where_conditions.append(f"{key} = %s")
                    where_values.append(condition)
            
            if where_conditions:
                sql += " WHERE " + " AND ".join(where_conditions)
                params = tuple(where_values)
        
        # 添加ORDER BY子句
        if order_by:
            sql += f" ORDER BY {order_by}"
        
        # 添加LIMIT子句
        if limit is not None and limit > 0:
            sql += f" LIMIT {limit}"
        
        print(f"执行的SQL: {sql}")  # 调试用
        print(f"参数: {params}")    # 调试用
        
        # 创建游标并执行参数化查询
        cursor = connection.cursor()
        cursor.execute(sql, params)
        
        print("查询成功")

        data_dict = {"column_name": [], "data": []}

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
        return {"column_name": [], "data": []}
    finally:
        # 只关闭游标，不关闭连接
        if cursor:
            cursor.close()

#INSERT
def mysql_insert_dict(connection: pymysql.Connection, table_name: str, insert_data: dict, ignore_extra_fields: bool = True):
    """
    执行参数化插入操作,防止SQL注入
    
    Args:
        connection: 数据库连接（由外部管理）
        table_name: 表名
        insert_data: 插入数据字典
        ignore_extra_fields: 是否忽略插入数据中不存在的字段（True时忽略，False时抛出错误）
    
    Returns:
        int: 插入的行数,失败返回0
    """
    cursor: Optional[pymysql.cursors.Cursor] = None
    try:
        # 验证插入数据
        if not insert_data or not isinstance(insert_data, dict):
            print("插入数据不能为空且必须为字典格式")
            return 0
        
        # 获取表结构信息
        cursor = connection.cursor()
        cursor.execute(f"DESCRIBE {table_name}")
        table_structure = cursor.fetchall()
        
        # 分析表结构
        table_columns = {}
        auto_increment_column = None
        nullable_columns = []
        columns_with_default = []
        
        for column_info in table_structure:
            column_name = column_info[0]
            column_type = column_info[1]
            is_nullable = column_info[2] == 'YES'
            column_key = column_info[3]
            column_default = column_info[4]
            extra = column_info[5]
            
            table_columns[column_name] = {
                'type': column_type,
                'nullable': is_nullable,
                'key': column_key,
                'default': column_default,
                'extra': extra
            }
            
            if extra and 'auto_increment' in extra.lower():
                auto_increment_column = column_name
            
            if is_nullable:
                nullable_columns.append(column_name)
            
            if column_default is not None:
                columns_with_default.append(column_name)
        
        # 检查插入数据中的字段是否存在于表中
        valid_columns = []
        invalid_columns = []
        
        for column in insert_data.keys():
            if column in table_columns:
                valid_columns.append(column)
            else:
                invalid_columns.append(column)
        
        if invalid_columns and not ignore_extra_fields:
            print(f"错误: 表中不存在的字段: {invalid_columns}")
            return 0
        elif invalid_columns:
            print(f"警告: 忽略表中不存在的字段: {invalid_columns}")
        
        # 检查必填字段
        required_columns = []
        for column_name, column_info in table_columns.items():
            # 如果不是自增字段、不可为空、没有默认值，则是必填字段
            if (column_name != auto_increment_column and 
                not column_info['nullable'] and 
                column_info['default'] is None):
                required_columns.append(column_name)
        
        missing_required_columns = [col for col in required_columns if col not in valid_columns]
        if missing_required_columns:
            print(f"错误: 缺少必填字段: {missing_required_columns}")
            return 0
        
        # 构建SQL语句（只包含提供的字段）
        columns = []
        placeholders = []
        values = []
        
        for column in valid_columns:
            columns.append(column)
            placeholders.append("%s")
            values.append(insert_data[column])
        
        sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
        params = tuple(values)
        
        # 执行插入操作
        cursor.execute(sql, params)
        connection.commit()  # 提交事务
        
        affected_rows = cursor.rowcount
        print(f"插入成功，影响行数: {affected_rows}")
        
        return affected_rows
                        
    except Exception as e:
        # 发生错误时回滚事务
        if connection:
            connection.rollback()
        print(f"执行插入时发生错误: {e}")
        return 0
    finally:
        # 只关闭游标，不关闭连接
        if cursor:
            cursor.close()

#UPDATE
def mysql_update_dict(connection: pymysql.Connection, table_name: str, update_data: dict, where_arg: dict = None):
    """
    执行参数化更新操作，防止SQL注入，支持比较运算符
    
    Args:
        connection: 数据库连接（由外部管理）
        table_name: 表名
        update_data: 要更新的字段和值的字典，例如 {'name': 'new_name', 'age': 25}
        where_arg: 更新条件字典，支持以下格式：
                  - 等值比较: {'id': 1, 'name': 'test'}
                  - 比较运算符: {'age': ('>', 18), 'score': ('<=', 100)}
                  - LIKE操作: {'name': ('LIKE', '%张%')}
                  - IN操作: {'id': ('IN', [1, 2, 3])}
                  - BETWEEN操作: {'age': ('BETWEEN', [18, 30])}
    
    Returns:
        int: 受影响的行数，失败时返回-1
    """
    cursor: Optional[pymysql.cursors.Cursor] = None
    try:
        # 验证更新数据不能为空
        if not update_data or not isinstance(update_data, dict):
            raise ValueError("update_data不能为空且必须为字典类型")
        
        # 构建基础SQL语句
        sql = f"UPDATE {table_name} SET "
        
        # 构建SET子句
        set_conditions = []
        set_values = []
        for key, value in update_data.items():
            set_conditions.append(f"{key} = %s")
            set_values.append(value)
        
        sql += ", ".join(set_conditions)
        
        # 构建WHERE子句（支持比较运算符）
        params = tuple(set_values)
        if where_arg and isinstance(where_arg, dict):
            where_conditions = []
            where_values = []
            
            for key, condition in where_arg.items():
                if isinstance(condition, tuple) and len(condition) == 2:
                    # 处理带运算符的条件
                    operator, value = condition
                    operator = operator.upper()
                    
                    if operator in ['=', '!=', '<', '>', '<=', '>=', 'LIKE', 'NOT LIKE']:
                        where_conditions.append(f"{key} {operator} %s")
                        where_values.append(value)
                    elif operator == 'IN':
                        # IN 操作需要特殊处理
                        if isinstance(value, (list, tuple)):
                            placeholders = ','.join(['%s'] * len(value))
                            where_conditions.append(f"{key} IN ({placeholders})")
                            where_values.extend(value)
                        else:
                            raise ValueError("IN操作符的值必须是列表或元组")
                    elif operator == 'BETWEEN':
                        # BETWEEN 操作需要特殊处理
                        if isinstance(value, (list, tuple)) and len(value) == 2:
                            where_conditions.append(f"{key} BETWEEN %s AND %s")
                            where_values.extend(value)
                        else:
                            raise ValueError("BETWEEN操作符的值必须是包含2个元素的列表或元组")
                    elif operator == 'IS NULL':
                        where_conditions.append(f"{key} IS NULL")
                    elif operator == 'IS NOT NULL':
                        where_conditions.append(f"{key} IS NOT NULL")
                    else:
                        raise ValueError(f"不支持的运算符: {operator}")
                else:
                    # 默认使用等值比较
                    where_conditions.append(f"{key} = %s")
                    where_values.append(condition)
            
            if where_conditions:
                sql += " WHERE " + " AND ".join(where_conditions)
                params = tuple(set_values + where_values)
        
        print(f"执行的SQL: {sql}")  # 调试用
        print(f"参数: {params}")    # 调试用
        
        # 创建游标并执行参数化更新
        cursor = connection.cursor()
        affected_rows = cursor.execute(sql, params)
        
        # 提交事务
        connection.commit()
        
        print(f"更新成功，受影响行数: {affected_rows}")
        return affected_rows
                        
    except Exception as e:
        # 回滚事务
        if connection:
            connection.rollback()
        print(f"执行更新时发生错误: {e}")
        return -1
    finally:
        # 只关闭游标，不关闭连接
        if cursor:
            cursor.close()

#DELETE
def mysql_delete_dict(connection: pymysql.Connection, table_name: str, where_arg: dict = None):
    """
    执行参数化删除操作，防止SQL注入
    
    Args:
        connection: 数据库连接（由外部管理）
        table_name: 表名
        where_arg: 删除条件字典，例如 {'id': 1, 'name': 'test'}
                  如果为None或空字典，将删除整个表的数据（危险操作）
    
    Returns:
        int: 受影响的行数，如果出错返回None
    """
    cursor: Optional[pymysql.cursors.Cursor] = None
    try:
        # 构建基础SQL语句
        sql = f"DELETE FROM {table_name}"
        params = ()
        
        # 安全警告：如果没有where条件会删除整个表
        if not where_arg:
            confirm = input("警告：您正在执行不带条件的删除操作，将删除整个表的数据！输入'y'确认执行：")
            if confirm.lower() != 'y':
                print("删除操作已取消")
                return 0
        elif where_arg and isinstance(where_arg, dict):
            where_conditions = []
            where_values = []
            for key, value in where_arg.items():
                where_conditions.append(f"{key} = %s")
                where_values.append(value)
            
            if where_conditions:
                sql += " WHERE " + " AND ".join(where_conditions)
                params = tuple(where_values)
        
        # 创建游标并执行参数化删除
        cursor = connection.cursor()
        cursor.execute(sql, params)
        
        # 提交事务
        connection.commit()
        
        affected_rows = cursor.rowcount
        print(f"删除成功，受影响行数: {affected_rows}")
        return affected_rows
                        
    except Exception as e:
        # 发生错误时回滚
        if connection:
            connection.rollback()
        print(f"执行删除时发生错误: {e}")
        return None
    finally:
        # 只关闭游标，不关闭连接
        if cursor:
            cursor.close()

# 更安全的版本（推荐）：要求必须提供where条件
def mysql_delete_dict_safe(connection: pymysql.Connection, table_name: str, where_arg: dict):
    """
    执行安全的参数化删除操作（必须提供where条件）
    
    Args:
        connection: 数据库连接（由外部管理）
        table_name: 表名
        where_arg: 删除条件字典，必须提供，例如 {'id': 1, 'name': 'test'}
    
    Returns:
        int: 受影响的行数，如果出错返回None
    """
    if not where_arg or not isinstance(where_arg, dict):
        raise ValueError("删除操作必须提供where条件字典")
    
    return mysql_delete_dict(connection, table_name, where_arg)

"""下标搜索"""
def find_index(lst, target_string):
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


test_flag = '__SELECT__'

if __name__ == '__main__':
    # 使用示例
    from app.services import connect_mysql as cm, operation_mysql as om
    from app.services import with_mysql as wm

    #开启数据库服务
    wm.start_mysql_service()
    conn = cm.connect_mysql("localhost","root","Pizza0804","srs_v1.0")
if __name__ == '__main__' and test_flag == '__SELECT__':
    # 安全查询 - 使用参数化
    print(json.dumps(mysql_select_json(conn, "sys_user", {"username": "kartery"}), ensure_ascii=False, indent=4))
    print("---------------------------------------------------------------------------")
    print(type(mysql_select_dict(conn, "sys_user",{"username": "kartery"})['data']))
if __name__ == '__main__' and test_flag == '__INSERT__':
    # 安全插入
    hashed = "280a72fc933650ff12cd935a43af6bd405988215732711896886e3aa8f8cf1c8"
    salt =   "32000e4736d10afb99fba6db0db6b3750ae4f1b933816a7e9617ad009b3255e2"

    mysql_insert_dict(conn,"sys_user",{"username":"Ailier","password_hash":hashed,"salt":salt})

    # 安全查询 - 使用参数化
    print(json.dumps(mysql_select_json(conn, "sys_user", {"username": "Ailier"}), ensure_ascii=False, indent=4))
    print("---------------------------------------------------------------------------")
    print(type(mysql_select_dict(conn, "sys_user",{"username": "Ailier"})['data']))
if __name__ == '__main__' and test_flag == '__UPDATE__':
    mysql_update_dict(conn,"sys_user",{"last_login_at":datetime.now()},{"username":"kartery"})
    print("---------------------------------------------------------------------------")
    print(json.dumps(mysql_select_json(conn, "sys_user", {"username": "kartery"}), ensure_ascii=False, indent=4))
if __name__ == '__main__' and test_flag == '__DELETE__':
    print(mysql_delete_dict(conn, "sys_user", {"username": "nanser"}))
    print("---------------------------------------------------------------------------")
    print(json.dumps(mysql_select_json(conn, "sys_user"), ensure_ascii=False, indent=4))
if __name__ == '__main__':
    #关闭连接
    conn.close()