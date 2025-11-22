from app.services import operation_mysql as om
import pymysql

"""查询两个表，那每个表查到的第一条的某个列作比较，返回后者表指定列的单个数据"""
def query_item(conn:pymysql.Connection,table_f:str,table_l:str,compare_arg:list,where_arg_f: dict = None,where_arg_l: dict = None):
    """
    执行参数化查询,防止SQL注入
    
    Args:
        conn: 数据库连接（由外部管理）
        table_f: 第一表名
        table_l: 第二表名
        compare_arg:比较及输出属性名 (f,l,o) ['user_id','user_id','role_id']
        where_arg_f/where_arg_l: 查询条件字典，例如 {'id': 1, 'name': 'test'}
    """
    if table_l == None:
        table_l = table_f
        
    try:
        first_data = om.mysql_select_dict(conn,table_f,where_arg_f)
        last_data = om.mysql_select_dict(conn,table_l,where_arg_l)
    except:
        print('❌ Unknow error from query_item().select')
        raise
        
    try:
        f_index = om.find_index(first_data["column_name"],compare_arg[0])
        l_index = om.find_index(last_data["column_name"],compare_arg[1])
        o_index = om.find_index(last_data["column_name"],compare_arg[2])

        if first_data["data"][0][f_index] == last_data["data"][0][l_index]:
            return last_data["data"][0][o_index]
    except IndexError as e:
        print(f'❌ IndexError from query_item():{e}')
    except:
        print('❌ Unknow error from query_item()')
        raise



                     
        



    

    