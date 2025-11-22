import pymysql
from app.utils import pwd_hash
from app.services import operation_mysql as om
from app.utils.permission import regulate
from app.utils import easy_query as eq

@regulate(0)
def login_mysql(conn:pymysql.Connection,username:str ,password: str) -> bool:
    try:
        user_data = om.mysql_select_dict(conn, "sys_user",{"username": username})
        idx = om.find_index(user_data["column_name"],"password_hash")
        if pwd_hash.verify_password(password,user_data['data'][0][idx],user_data['data'][0][idx+1]):
            print('✅ Login success!')
            om.mysql_update_dict(conn,"sys_user",{"last_login_at":om.datetime.now()},{"username":username})
            return True
        else:
            print('❌ Incorrect password')
            return False
    except:
        print('❌ Unknow error from login_mysql()')
        return False

@regulate(1110)
def logon_mysql(conn:pymysql.Connection, username:str ,password: str,who_done_this:str = None):
    """
    执行创建用户
    
    Args:
        connection: 数据库连接（由外部管理）
        username: 用户名
        password: 密码
        who_done_this: 执行人
    
    Returns:
        int: 插入的行数,失败返回0
    """
    try:
        hashed,salt = pwd_hash.hash_password(password)
        inser_data = {"username": username,"password_hash":hashed,"salt":salt}
        if who_done_this != None:
            inser_data["created_by"] = who_done_this
            om.mysql_insert_dict(conn, "sys_user",inser_data)
            print(f'✅ {username}:Logon success!')
            return True
        else:
            print('❌ Logon failed...')
            return False
    except:
        print('❌ Unknow error')
        return False

@regulate(0)
def get_regulate_code(conn:pymysql.Connection,username:str,defalut_code:int = -1):
    try:
        role_id = eq.query_item(conn,"sys_user","sys_user_role",['user_id','user_id','role_id'],{"username":username})
        role_code = om.mysql_select_dict(conn,"sys_role",{"role_id":role_id})
        return role_code["data"][0][om.find_index(role_code["column_name"],"role_code")]

    except:
        print('❌ Unknow error from get_regulate_code()')
        return defalut_code


if __name__ == '__main__':

    import connect_mysql as cm

    conn = cm.connect_mysql("localhost","root","Pizza0804","srs_v1.0")

    login_mysql(conn,'kartery','my_password')
    print(logon_mysql(conn,'Whoarou','dontloseyournobility','f9567e2f-c3a8-11f0-9a9a-b025aa56a838'))
    login_mysql(conn,'Whoarou','dontloseyournobility')


    conn.close()