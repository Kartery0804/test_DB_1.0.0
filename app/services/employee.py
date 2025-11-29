import pymysql
from app.services import operation_mysql as om
from app.utils.permission import regulate
from app.utils import easy_query as eq

#权限值0b1101，仅供同时拥有查询，审核，创建权限的用户访问

@regulate(0b1101)
def add_employee(conn:pymysql.Connection,employee_no:str,name_cn:str,hire_date:str,employment_type:str,dept_name:str,status:str,position_name:str,manager_employee_no:str = None,**kwargs):
    try:
        dept_id = om.mysql_select_dict(conn,"department",{"dept_name":dept_name})['data'][0][0]
        position_id = om.mysql_select_dict(conn,"position",{"position_name":position_name})['data'][0][0]
        if manager_employee_no!=None:
            manager_employee_id = om.mysql_select_dict(conn,"employee",{"manager_employee_no":manager_employee_no})['data'][0][0]
        else:
            manager_employee_id = None
    except:
        print("❌ select the id error from add_employee()")
        return False
    
    field_mapping = {
            "employee_no":employee_no,
            "name_cn":name_cn,
            "hire_date":hire_date,
            "employment_type":employment_type,
            "dept_id":dept_id,
            "position_id":position_id,
            "manager_employee_id":manager_employee_id,
            "status":status
        }

    add_data = {
            "updated_at": om.datetime.now(),
            **{k: v for k, v in field_mapping.items() if v is not None}
        }
    
    try:
        om.mysql_insert_dict(conn,"employee",add_data)
    except:
        print("❌ insert the employee error from add_employee()")
        return False
    
@regulate(0b1101)
def update_employee(
    conn:pymysql.Connection,
    employee_no:str,
    employee_no_new:str = None,
    name_cn:str = None,
    hire_date:str = None,
    employment_type:str = None,
    dept_name:str = None,
    status:str = None,
    position_name:str = None,
    manager_employee_no:str = None,
    #--
    name_en:str = None,
    gender:str = None,
    date_of_birth:str = None,
    id_number:str = None,
    phone:str = None,
    email:str = None,
    probation_end_date:str = None,
    work_location:str = None,
    salary_base:str = None,
    bank_name:str = None,
    bank_account_no:str = None,
    social_city:str = None,
    address:str = None,
    emergency_name:str = None,
    emergency_phone:str = None,
    photo_url:str = None,
    username:str = None,
    **kwargs
    ):
    try:
        updated_by = dept_id = position_id = manager_employee_id = None
        if username!=None:
            updated_by = om.mysql_select_dict(conn,"sys_user",{"username":username})['data'][0][0]
        else:
            print("❌ select the updated_by_id error from add_employee()")
            return False
        if dept_name!=None:
            dept_id = om.mysql_select_dict(conn,"department",{"dept_name":dept_name})['data'][0][0]
        if dept_name!=None:
            position_id = om.mysql_select_dict(conn,"position",{"position_name":position_name})['data'][0][0]
        if manager_employee_no!=None:
            manager_employee_id = om.mysql_select_dict(conn,"employee",{"manager_employee_no":manager_employee_no})['data'][0][0]
    except:
        print("❌ select the id error from add_employee()")
        #return False
    
    field_mapping = {
            "employee_no":employee_no_new,
            "name_cn":name_cn,
            "hire_date":hire_date,
            "employment_type":employment_type,
            "dept_id":dept_id,
            "position_id":position_id,
            "manager_employee_id":manager_employee_id,
            "status":status,
            "updated_by":updated_by,
            "name_en":name_en,
            "gender":gender,
            "date_of_birth":date_of_birth,
            "id_number":id_number,
            "phone":phone,
            "email":email,
            "probation_end_date":probation_end_date,
            "work_location":work_location,
            "salary_base":salary_base,
            "bank_name":bank_name,
            "bank_account_no":bank_account_no,
            "social_city":social_city,
            "address":address,
            "emergency_name":emergency_name,
            "emergency_phone":emergency_phone,
            "photo_url":photo_url
        }

    update_data = {
            "updated_at": om.datetime.now(),
            **{k: v for k, v in field_mapping.items() if v is not None}
        }
    
    try:
        us = om.mysql_update_dict(conn,"employee",update_data,{"employee_no":employee_no})
        print(f"✅ add success from add_employee():{us}")
        return True
    except:
        print("❌ insert the employee error from add_employee()")
        return False
    

if __name__ == "__main__":
    conn = None
    try:
        from app.services import connect_mysql as cm
        conn = cm.connect_mysql('localhost','root','Pizza0804','srs_v1.0')
        #职员测试
        data = {
            "username":"kartery",
            "employee_no":"12314789",
            "name_cn":"李四",
            #"hire_date":"2025-1-1",
            #"employment_type":"full",
            #"dept_name":"Animation Dept",
            #"position_name":"Concept_Art",
            #"manager_employee_name":None,
            "status":"active"
        }
        #操作 
        #add_employee(conn,**data,r_flag = 0b1111)
        update_employee(conn,**data,r_flag = 0b1111)
        #打印结果
        print(om.mysql_select_dict(conn,"employee",{"name_cn":"李四"}))


    except:
        print("error")
        raise
    finally:
        if conn != None:
            conn.close()