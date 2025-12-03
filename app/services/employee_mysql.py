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
            **{k: v for k, v in field_mapping.items() if v is not None and v != ""}
        }
    
    try:
        om.mysql_insert_dict(conn,"employee",add_data)
        return True
    except:
        print("❌ insert the employee error from add_employee()")
        return False
    
@regulate(0b1101)
def update_employee(
    conn:pymysql.Connection,
    employee_no:str,
    username:str = None,
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
        if position_name!=None:
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
            **{k: v for k, v in field_mapping.items() if v is not None and v != ""}
        }
    
    try:
        us = om.mysql_update_dict(conn,"employee",update_data,{"employee_no":employee_no})
        print(f"✅ update success from add_employee():{us}")
        return True
    except:
        print("❌ insert the employee error from add_employee()")
        return False
    
@regulate(0b1000)
def select_employee(
    conn:pymysql.Connection,
    employee_no:str = None,
    updated_by_name:str = None,
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
    **kwargs
    ):
    try:
        updated_by = dept_id = position_id = manager_employee_id = None
        if updated_by_name!=None:
            updated_by = om.mysql_select_dict(conn,"sys_user",{"username":updated_by_name})['data'][0][0]
        if dept_name!=None:
            dept_id = om.mysql_select_dict(conn,"department",{"dept_name":dept_name})['data'][0][0]
        if position_name!=None:
            position_id = om.mysql_select_dict(conn,"position",{"position_name":position_name})['data'][0][0]
        if manager_employee_no!=None:
            manager_employee_id = om.mysql_select_dict(conn,"employee",{"manager_employee_no":manager_employee_no})['data'][0][0]
    except:
        print("❌ select the id error from select_employee()")
        return {"column_name": ["error"],"data": [["select the id error from select_employee()"]]} 
    field_mapping = {
            "employee_no":employee_no,
            "name_cn":name_cn,
            "hire_date":hire_date,
            "employment_type":employment_type,
            "dept_id":dept_id,
            "position_id":position_id,
            "manager_employee_id":manager_employee_id,
            "employee.status":status,
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

    select_data = {
            **{k: v for k, v in field_mapping.items() if v is not None and v != ""}
        }
    try:
        #data = om.mysql_select_dict(conn,"employee",select_data)
        data = om.mysql_select_dict(conn,
            tables=['employee'],
            join_conditions=[
                {
                    'type': 'INNER',
                    'table1': 'employee', 
                    'table2': 'department',
                    'on': 'employee.dept_id = department.dept_id'
                },
                {
                    'type': 'INNER',
                    'table1': 'employee', 
                    'table2': 'position',
                    'on': 'employee.position_id = position.position_id'
                }
            ],
            where_arg=select_data,
            select_columns=['employee.name_cn','employee.employee_no', 'department.dept_name', 'position.position_name','employee.employment_type','employee.status', 'employee.name_en','employee.gender','employee.date_of_birth','employee.id_number','employee.phone','employee.email','employee.hire_date','employee.probation_end_date','employee.work_location','employee.salary_base','employee.bank_name','employee.bank_account_no','employee.social_city','employee.address','employee.emergency_name','employee.emergency_phone']
        )
        print(f"✅ select success from select_employee()")
        return data
    except:
        print("❌ insert the employee error from select_employee()")
        return {"column_name": ["error"],"data": [["insert the employee error from select_employee()"]]}

@regulate(0b1101)
def rework_employee_pos(
    conn:pymysql.Connection,
    employee_no:str,
    new_position_name:str,
    new_dept_name:str,
    username:str = None,
    employment_type:str = None,
    manager_employee_no:str = None,
    work_location:str = None,
    salary_base:str = None,
    **kwargs
    ):
    try:
        updated_by = new_dept_id = new_position_id = manager_employee_id = None
        if username!=None:
            updated_by = om.mysql_select_dict(conn,"sys_user",{"username":username})['data'][0][0]
        else:
            print("❌ select the updated_by_id error from rework_employee_pos()")
            return False
        if new_dept_name!=None:
            new_dept_id = om.mysql_select_dict(conn,"department",{"dept_name":new_dept_name})['data'][0][0]
        if new_position_name!=None:
            new_position_id = om.mysql_select_dict(conn,"position",{"position_name":new_position_name})['data'][0][0]
        if manager_employee_no!=None:
            manager_employee_id = om.mysql_select_dict(conn,"employee",{"manager_employee_no":manager_employee_no})['data'][0][0]
    except:
        print("❌ select the id error from rework_employee_pos()")
        #return False
    
    field_mapping = {
            "employment_type":employment_type,
            "dept_id":new_dept_id,
            "position_id":new_position_id,
            "manager_employee_id":manager_employee_id,
            "updated_by":updated_by,
            "work_location":work_location,
            "salary_base":salary_base
        }

    update_data = {
            "updated_at": om.datetime.now(),
            **{k: v for k, v in field_mapping.items() if v is not None and v != ""}
        }
    
    try:
        if om.mysql_select_dict(conn,"employee",{"employee_no":employee_no})["data"] and om.mysql_select_dict(conn,"department",{"dept_id":new_dept_id})["data"] and om.mysql_select_dict(conn,"position",{"position_id":new_position_id})["data"]:
            us = om.mysql_update_dict(conn,"employee",update_data,{"employee_no":employee_no})
            print(f"✅ update success from rework_employee_pos():{us}")
            return True
        else:
            print("❌ did have new position/department or this employee")
            return False
    except:
        print("❌ insert the employee error from rework_employee_pos()")
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
            #"name_cn":"李四",
            #"hire_date":"2025-1-1",
            #"employment_type":"full",
            #"dept_name":"Animation Dept",
            #"position_name":"Concept_Art",
            #"manager_employee_name":None,
            "status":"on_leave"
            #"salary_base":1000
        }
        #操作 
        #add_employee(conn,**data,r_flag = 0b1111)
        update_employee(conn,**data,r_flag = 0b1111)
        #打印结果
        print(select_employee(conn,**data,r_flag = 0b1111))


    except:
        print("error")
        raise
    finally:
        if conn != None:
            conn.close()