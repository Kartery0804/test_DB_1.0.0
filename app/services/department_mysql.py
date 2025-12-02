import pymysql
from app.services import operation_mysql as om
from app.utils.permission import regulate
from app.utils import easy_query as eq
from app.services import config_mysql as cf
#权限值0b1101，仅供同时拥有查询，审核，创建权限的用户访问

#部门
@regulate(0b1101)
def add_dept(conn:pymysql.Connection ,dept_name:str ,dept_code: str ,parent_dept_name:str = None,manager_employee_no:str = None,status:int=None,**kwargs):
    try:
        parent_dept_id = manager_employee_id = None
        if parent_dept_name:
            parent_data = om.mysql_select_dict(conn,"department",{"dept_name":parent_dept_name})["data"]
            if parent_data:
                parent_dept_id = parent_data[0][0]
        if manager_employee_no:
            manager_employee_data = om.mysql_select_dict(conn,"employee",{"employee_no":manager_employee_no})["data"]
            if manager_employee_data:
                manager_employee_id = manager_employee_data[0][0]

            
        field_mapping = {
            "dept_name":dept_name,
            "dept_code": dept_code, 
            "parent_dept_id": parent_dept_id,
            "manager_employee_id": manager_employee_id,
            "status":status
        }

        add_data = {
            "updated_at": om.datetime.now(),
            **{k: v for k, v in field_mapping.items() if v is not None}
        }
        if not om.mysql_select_dict(conn,"department",{"dept_name":dept_name})["data"] and not om.mysql_select_dict(conn,"department",{"dept_code":dept_code})["data"]:
            if om.mysql_insert_dict(conn,"department",add_data) != None:
                return True
            else:
                raise Exception("error from mysql_insert_dict() ")
        else:
            print("❌ Department name/code duplication from add_dept()")
            return False
        
        
    except Exception as e:
        print(f'❌ Unknow error from add_dept() : {e}')
        return False

@regulate(0b1101)
def update_dept(conn:pymysql.Connection ,dept_name:str,new_dept_name:str = None ,dept_code: str = None ,parent_dept_name:str = None,manager_employee_no:str = None,status:int = None,**kwargs):
    try:
        parent_dept_id = manager_employee_id = None
        if parent_dept_name:
            parent_data = om.mysql_select_dict(conn,"department",{"dept_name":parent_dept_name})["data"]
            if parent_data:
                parent_dept_id = parent_data[0][0]
        if manager_employee_no:
            manager_employee_data = om.mysql_select_dict(conn,"employee",{"employee_no":manager_employee_no})["data"]
            if manager_employee_data:
                manager_employee_id = manager_employee_data[0][0]

        field_mapping = {
            "dept_name": new_dept_name,
            "dept_code": dept_code, 
            "parent_dept_id": parent_dept_id,
            "manager_employee_id": manager_employee_id,
            "status":status
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
        print(f'❌ Unknow error from update_dept() : {e}')
        return False
@regulate(0b1101)
def delete_dept(conn:pymysql.Connection ,dept_name:str):
    try:
        if om.mysql_select_dict(conn,"department",{"dept_name":dept_name})["data"]:
            if om.mysql_delete_dict_safe(conn,"department",{"dept_name":dept_name}):
                return True
        else:
            print("❌ Department name/code duplication from delete_dept()")
            return False
    except Exception as e:
        print(f'❌ Unknow error from delete_dept() : {e}')
        return False

@regulate(0b1101)
def select_dept(conn:pymysql.Connection ,dept_name:str = None,dept_code: str = None ,parent_dept_name:str = None,manager_employee_no:str = None,status:int = None,**kwargs):
    try:
        parent_dept_id = manager_employee_id = None
        if parent_dept_name:
            parent_data = om.mysql_select_dict(conn,"department",{"dept_name":parent_dept_name})["data"]
            if parent_data:
                parent_dept_id = parent_data[0][0]
        if manager_employee_no:
            manager_employee_data = om.mysql_select_dict(conn,"employee",{"employee_no":manager_employee_no})["data"]
            if manager_employee_data:
                manager_employee_id = manager_employee_data[0][0]
        
        field_mapping = {
            "dept_name": dept_name,
            "dept_code": dept_code, 
            "parent_dept_id": parent_dept_id,
            "manager_employee_id": manager_employee_id,
            "status":status
        }
        select_data = {
            **{k: v for k, v in field_mapping.items() if v is not None}
        }
        dept_data = om.mysql_select_dict(conn,"department",select_data)
        if dept_data:
            if dept_data['data']:
                return dept_data
            else:
                print("❌ didn't select data form select_dept()")
                return dept_data
        else:
            dept_data = {'column_name':["error"],"data":["❌ mysql_select_dict error form select_dept()"]}
            return dept_data

    except Exception as e:
        print(f'❌ Unknow error from select_dept() : {e}')
        return {"column_name": ["error"],"data": [["Maybe Department name duplication from select_dept()"]]}
    

#岗位 
@regulate(0b1101)
def add_position(conn:pymysql.Connection,position_name:str,dept_name:str,job_family:str = None,position_level:str = None,headcount_budget:int = 0,description:str = None,status:int = 1,**kwargs):
    """新增岗位"""
    try:
        dept_id_data = om.mysql_select_dict(conn,"department",{"dept_name":dept_name})["data"]
        if dept_id_data:
            dept_id = dept_id_data[0][0]
        else:
            print("❌ didn't have this department")
            return False
        field_mapping = {
            "dept_id":dept_id,
            "position_name":position_name,
            "position_level": position_level,
            "headcount_budget": headcount_budget,
            "description":description,
            "status":status,
            "job_family":job_family
        }

        add_data = {
            "updated_at": om.datetime.now(),
            "created_at": om.datetime.now(),
            **{k: v for k, v in field_mapping.items() if v is not None}
        }

        if not om.mysql_select_dict(conn,"position",{"position_name":position_name,"dept_id":dept_id})["data"]:
            if om.mysql_insert_dict(conn,"position",add_data) != None:
                return True
            else:
                raise Exception("error from add_position() ")
        else:
            print("❌ position name duplication from add_position()")
            return False
        
        
    except Exception as e:
        print(f'❌ Unknow error from add_dept() : {e}')
        return False

@regulate(0b1101)
def update_position(conn:pymysql.Connection,position_name:str,dept_name:str,job_family:str = None,new_position_name:str = None,new_dept_name:str =None,position_level:str = None,headcount_budget:int  = None,description:str = None,status:int = None,**kwargs):
    try:
        new_dept_id = dept_id = position_id = None
        if dept_name:
            dept_id = om.mysql_select_dict(conn,"department",{"dept_name":dept_name})["data"][0][0]
        if new_dept_name:
            new_dept_id = om.mysql_select_dict(conn,"department",{"dept_name":new_dept_name})["data"][0][0]
        if dept_id and position_name:
            position_id = om.mysql_select_dict(conn,"position",{"position_name":position_name,"dept_id":dept_id})["data"][0][0]
        else:
            print("❌ Can't select dept_id/position from update_position()")
            return False
        if position_id:
            field_mapping = {
                    "position_name":new_position_name,
                    "dept_id":new_dept_id,
                    "position_level":position_level,
                    "headcount_budget":headcount_budget,
                    "description":description,
                    "status":status,
                    "position_level":position_level,
                    "job_family":job_family
                }

            update_data = {
                "updated_at": om.datetime.now(),
                **{k: v for k, v in field_mapping.items() if v is not None}
            }

            if om.mysql_update_dict(conn,"position",update_data,{"position_name":position_name,"dept_id":dept_id}) != None:
                return True
            return False
        else:
            print("❌ Can't select position_id from update_position()")
            return False

    except Exception as e:
        print(f'❌ Unknow error from update_position() : {e}')
        return False
    
@regulate(0b1101)
def delete_position(conn:pymysql.Connection,position_name:str,dept_name:str):
    try:
        dept_id = position_id = None
        if dept_name:
            dept_id = om.mysql_select_dict(conn,"department",{"dept_name":dept_name})["data"][0][0]
        if dept_id and position_name:
            position_id = om.mysql_select_dict(conn,"position",{"position_name":position_name,"dept_id":dept_id})["data"][0][0]
            if position_id == None:
                print(f"❌ Can't delete {position_name} from delete_position()")
                return False
            else:
                om.mysql_delete_dict(conn,"position",{"position_id":position_id})
                return True
        else:
            print(f"❌ Can't select {position_name} and {dept_name} from delete_position()")
            return False

    except Exception as e:
        print(f'❌ Unknow error from delete_position() : {e}')
        return False

@regulate(0b1101)
def select_position(conn:pymysql.Connection,position_name:str=None,dept_name:str=None,job_family:str = None,position_level:str = None,headcount_budget:int  = None,description:str = None,status:int = None,**kwargs):
    try:
        dept_id = position_id = None
        if dept_name:
            dept_id = om.mysql_select_dict(conn,"department",{"dept_name":dept_name})["data"][0][0]
        if dept_id and position_name:
            position_id = om.mysql_select_dict(conn,"position",{"position_name":position_name,"dept_id":dept_id})["data"][0][0]
        else:
            print("❌ Can't select dept_id/position from select_position()")
        field_mapping = {
            "position.position_id":position_id,
            "position.dept_id":dept_id,
            "position_name":position_name,
            "position_level": position_level,
            "headcount_budget": headcount_budget,
            "description":description,
            "status":status,
            "job_family":job_family
        }

        select_data = {
            **{k: v for k, v in field_mapping.items() if v is not None}
        }
        pos_data = om.mysql_select_dict(
            conn,
            tables=['position'],
            join_conditions = [
                {
                    'type':'INNER',
                    'table1':'position',
                    'table2':'department',
                    'on':'position.dept_id = department.dept_id'
                }
            ],
            columns=['position.position_name','department.dept_name'],
            where_arg=select_data
        )
        if  pos_data["data"]:
            return pos_data
        else:
            print("❌ didn't select data form select_position()")
            return pos_data

    except Exception as e:
        print(f'❌ Unknow error from select_pos() : {e}')
        return {"column_name": ["error"],"data": [["Maybe Department name duplication from select_position()"]]}


@regulate(0b1101)
def read_info(conn:pymysql.Connection,table_name:str,where_arg: dict = None):
    try:
        info = om.mysql_select_dict(conn,table_name,where_arg)
        if info != None:
            return info
        else:
            return {"column_name": ["error"],"data": ["unknow error from read_info()"]}
    except Exception as e:
        print(f'❌ Unknow error from read_info() : {e}')
        return False

if __name__ == "__main__":
    conn = None
    try:
        from app.services import connect_mysql as cm
        conn = cm.connect_mysql(*cf.default)
        #部门测试
        #add_dept(conn,"Animation Dept",dept_code = "00002",r_flag = 0b1101)
        #update_dept(conn,"Animation Dept" ,dept_code = "00001",r_flag = 0b1101)
        #print(om.mysql_select_dict(conn,"department"))

        
        #add_position(conn,"Concept_Art1","Animation Dept","1",0,"原画师1",r_flag = 0b1101)
        #update_position(conn,"Concept_Art",dept_name="Animation Dept",headcount_budget = 10,r_flag = 0b1101)
        #add_position(conn,"Mover","Logistics Dept","1",10,"搬货工",r_flag = 0b1101)
        #print(delete_position(conn,"Mover",r_flag = 0b1111))
        print(select_dept(conn,r_flag=0b1111))


    except:
        print("error")
    finally:
        if conn != None:
            conn.close()