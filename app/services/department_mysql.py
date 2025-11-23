import pymysql
from app.services import operation_mysql as om
from app.utils.permission import regulate
from app.utils import easy_query as eq

#权限值0b1101，仅供同时拥有查询，审核，创建权限的用户访问

#部门
@regulate(0b1101)
def add_dept(conn:pymysql.Connection ,dept_name:str ,dept_code: str ,parent_dept_id:str = None,manager_employee_id:str = None):
    try:
        if not om.mysql_select_dict(conn,"department",{"dept_name":dept_name})["data"]:
            if om.mysql_insert_dict(conn,"department",{"dept_name":dept_name,"dept_code":dept_code,"parent_dept_id":parent_dept_id,"manager_employee_id":manager_employee_id}) != None:
                return True
            else:
                raise Exception("error from mysql_insert_dict() ")
        else:
            print("❌ Department name duplication from create_dept()")
            return False
        
        
    except Exception as e:
        print(f'❌ Unknow error from create_dept() : {e}')
        return False
    
@regulate(0b1101)
def update_dept(conn:pymysql.Connection ,dept_name:str,new_dept_name:str = None ,dept_code: str = None ,parent_dept_id:str = None,manager_employee_id:str = None):
    try:
        field_mapping = {
            "dept_name": new_dept_name,
            "dept_code": dept_code, 
            "parent_dept_id": parent_dept_id,
            "manager_employee_id": manager_employee_id
        }

        update_data = {
            "updated_at": om.datetime.now(),
            **{k: v for k, v in field_mapping.items() if v is not None}
        }

        if om.mysql_update_dict(conn,"department",update_data,{"dept_name":dept_name}) != None:
            return True
        else:
            raise Exception("error from mysql_update_dict()")

    except Exception as e:
        print(f'❌ Unknow error from create_dept() : {e}')
        return False
    
#岗位 
@regulate(0b1101)
def add_position(conn:pymysql.Connection,position_name:str,dept_name:str,position_level:str = None,headcount_budget:int = 0,description:str = None,status:int = 1):
    """新增岗位"""
    try:
        dept_id = om.mysql_select_dict(conn,"department",{"dept_name":dept_name})["data"]
        position = om.mysql_select_dict(conn,"position",{"position_name":position_name})["data"]
        if dept_id and not position:
            om.mysql_insert_dict(conn,"position",{
                "position_name":position_name,
                "dept_id":dept_id[0][0],
                "position_level":position_level,
                "headcount_budget":headcount_budget,
                "description":description,
                "status":status
            })
            return True
        else:
            print("❌ Can select dept_id or Position name duplication from add_position()")
            return False

    except Exception as e:
        print(f'❌ Unknow error from add_position() : {e}')
        return False

@regulate(0b1101)
def update_position(conn:pymysql.Connection,position_name:str,new_position_name:str = None,dept_name:str = None,position_level:str = None,headcount_budget:int  = None,description:str = None,status:int = None):
    try:
        dept_id = om.mysql_select_dict(conn,"department",{"dept_name":dept_name})["data"]
        if dept_id:
            field_mapping = {
                    "position_name":new_position_name,
                    "dept_id":dept_id[0][0],
                    "position_level":position_level,
                    "headcount_budget":headcount_budget,
                    "description":description,
                    "status":status
                }

            update_data = {
                "updated_at": om.datetime.now(),
                **{k: v for k, v in field_mapping.items() if v is not None}
            }

            if om.mysql_update_dict(conn,"position",update_data,{"position_name":position_name}) != None:
                return True
            return False
        else:
            print("❌ Can't select dept_id from update_position()")
            return False

    except Exception as e:
        print(f'❌ Unknow error from create_dept() : {e}')
        return False
    
@regulate(0b1101)
def delete_position(conn:pymysql.Connection,position_name:str):
    try:
        if position_name:
            flag = om.mysql_delete_dict(conn,"position",{"position_name":position_name})
            if flag == None:
                print(f"❌ Can't delete {position_name} from delete_position()")
                return False
            return True
        else:
            print(f"❌ Can't select {position_name} from delete_position()")
            return False

    except Exception as e:
        print(f'❌ Unknow error from create_dept() : {e}')
        return False

@regulate(0b1101)
def read_info(conn:pymysql.Connection,table_name:str,where_arg: dict = None):
    info = om.mysql_select_dict(conn,table_name,where_arg)
    if info != None:
        return info
    else:
        return {"column_name": ["error"],"data": ["unknow error from read_info()"]}


@regulate(0b1101)
def appoint(conn:pymysql.Connection):
    """任命"""
    try:
        
        return True

    except Exception as e:
        print(f'❌ Unknow error from appoint() : {e}')
        return False

@regulate(0b1101)
def dismiss():
    """解职"""
    try:

        return True

    except Exception as e:
        print(f'❌ Unknow error from appoint() : {e}')
        return False




if __name__ == "__main__":
    conn = None
    try:
        from app.services import connect_mysql as cm
        conn = cm.connect_mysql('localhost','root','Pizza0804','srs_v1.0')
        #部门测试
        #add_dept(conn,"Animation Dept",dept_code = "00002",r_flag = 0b1101)
        #update_dept(conn,"Animation Dept" ,dept_code = "00001",r_flag = 0b1101)
        #print(om.mysql_select_dict(conn,"department"))

        #新增岗位
        #add_position(conn,"Concept_Art","Animation Dept","1",0,"原画师",r_flag = 0b1101)
        update_position(conn,"Concept_Art",dept_name="Animation Dept",headcount_budget = 10,r_flag = 0b1101)


    except:
        print("error")
    finally:
        if conn != None:
            conn.close()