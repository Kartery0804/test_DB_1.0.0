import pymysql
from app.utils import pwd_hash
from app.services import operation_mysql as om

def login_mysql(conn:pymysql.Connection, username:str ,password: str) -> bool:
    try:
        user_data = om.mysql_select_dict(conn, "sys_user",{"username": username})
        idx = om.find_column_index(user_data["column_name"],"password_hash")
        if pwd_hash.verify_password(password,user_data['data'][0][idx],user_data['data'][0][idx+1]):
            print('✅ Login success!')
            return True
        else:
            print('❌ Incorrect password')
            return False
    except:
        print('❌ Unknow error')
        return False



if __name__ == '__main__':

    import connect_mysql as cm

    conn = cm.connect_mysql("localhost","root","Pizza0804","srs_v1.0")

    login_mysql(conn,'kartery','my_password')