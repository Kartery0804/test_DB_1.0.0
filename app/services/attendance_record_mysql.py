import pymysql
from app.services import operation_mysql as om
from app.utils.permission import regulate
from app.utils import easy_query as eq
from app.services import config_mysql as cf

@regulate(0b1101)
def add_attend_cod(conn:pymysql.Connection ,date: str,employee_no:str,absent:int = None,shift_type:str = None,checkin_time:str=None,source:str=None,checkout_time:str=None,work_hours:str=None,location:str=None,approver_user_name:str=None,approved_at:str=None,late_minutes:int = None,early_leave_minutes:int=None,remark:str=None,**kwargs):
    try:
        approver_user_id = employee_id = None
        if employee_no:
            employee_data = om.mysql_select_dict(conn,"employee",{"employee_no":employee_no})["data"]
            if employee_data:
                employee_id = employee_data[0][0]
            else:
                print("❌ didn't have this employee")
                return False
        if approver_user_name!=None:
            approver_user_id = om.mysql_select_dict(conn,"sys_user",{"username":approver_user_name})['data'][0][0]
            
        field_mapping = {
            "date":date,
            "absent":absent,
            "employee_id":employee_id,
            "shift_type":shift_type,
            "checkin_time":checkin_time,
            "source":source,
            "checkout_time":checkout_time,
            "work_hours":work_hours,
            "location":location,
            "approved_at":approved_at,
            "late_minutes":late_minutes,
            "early_leave_minutes":early_leave_minutes,
            "remark":remark,
            "approver_user_id":approver_user_id
        }

        add_data = {
            "created_at": om.datetime.now(),
            "updated_at":om.datetime.now(),
            **{k: v for k, v in field_mapping.items() if v is not None}
        }
        if not om.mysql_select_dict(conn,"attendance_record",{"date":date,"employee_id":employee_id})["data"]:
            if om.mysql_insert_dict(conn,"attendance_record",add_data) != None:
                return True
            else:
                raise Exception("error from add_attend_cod() 1111")
        else:
            print("❌ attend_cod date duplication from add_attend_cod() 1121")
            return False
        
        
    except Exception as e:
        print(f'❌ Unknow error from add_attend_cod()1131 : {e}')
        return False
    

@regulate(0b1101)
def update_attend_cod(conn:pymysql.Connection ,date: str,employee_no:str,absent:int = None,shift_type:str = None,checkin_time:str=None,source:str=None,checkout_time:str=None,work_hours:str=None,location:str=None,approver_user_name:str=None,approved_at:str=None,late_minutes:int = None,early_leave_minutes:int=None,remark:str=None,status:str=None,**kwargs):
    try:
        approver_user_id = employee_id = None
        if employee_no:
            employee_data = om.mysql_select_dict(conn,"employee",{"employee_no":employee_no})["data"]
            if employee_data:
                employee_id = employee_data[0][0]
            else:
                print("❌ didn't have this employee")
                return False
        if approver_user_name!=None:
            approver_user_id = om.mysql_select_dict(conn,"sys_user",{"username":approver_user_name})['data'][0][0]
            
        field_mapping = {
            "absent":absent,
            "employee_id":employee_id,
            "shift_type":shift_type,
            "checkin_time":checkin_time,
            "source":source,
            "checkout_time":checkout_time,
            "work_hours":work_hours,
            "location":location,
            "approved_at":approved_at,
            "late_minutes":late_minutes,
            "early_leave_minutes":early_leave_minutes,
            "remark":remark,
            "approver_user_id":approver_user_id,
            "status":status
        }

        update_data = {
            "updated_at":om.datetime.now(),
            **{k: v for k, v in field_mapping.items() if v is not None}
        }
        if om.mysql_update_dict(conn,"attendance_record",update_data,{"date":date,"employee_id":employee_id}) != None:
            return True
        else:
            raise Exception("error from update_attend_cod()")

    except Exception as e:
        print(f'❌ Unknow error from update_dept() : {e}')
        return False
    
@regulate(0b1101)
def select_attend_cod(conn:pymysql.Connection ,status:str=None,date: str=None,employee_no:str=None,absent:int = None,shift_type:str = None,checkin_time:str=None,source:str=None,checkout_time:str=None,work_hours:str=None,location:str=None,approver_user_name:str=None,approved_at:str=None,late_minutes:int = None,early_leave_minutes:int=None,remark:str=None,**kwargs):
    try:
        approver_user_id = employee_id = None
        if employee_no:
            employee_data = om.mysql_select_dict(conn,"employee",{"employee_no":employee_no})["data"]
            if employee_data:
                employee_id = employee_data[0][0]
            else:
                print("❌ didn't found this employee")
                return {"column_name":"info","data":[["didn't found this employee"]]}
        if approver_user_name!=None:
            approver_user_id = om.mysql_select_dict(conn,"sys_user",{"username":approver_user_name})['data'][0][0]
        
        field_mapping = {
            "date":date,
            "absent":absent,
            "attendance_record.employee_id":employee_id,
            "shift_type":shift_type,
            "checkin_time":checkin_time,
            "source":source,
            "checkout_time":checkout_time,
            "work_hours":work_hours,
            "location":location,
            "approved_at":approved_at,
            "late_minutes":late_minutes,
            "early_leave_minutes":early_leave_minutes,
            "remark":remark,
            "approver_user_id":approver_user_id,
            "attendance_record.status":status
        }
        select_data = {
            **{k: v for k, v in field_mapping.items() if v is not None}
        }
        empl_contract_data = om.mysql_select_dict(conn,
            tables=['attendance_record'],  # 主表使用别名
            join_conditions=[
                {
                    'type': 'LEFT',
                    'table1': 'attendance_record',
                    'table2': 'employee',
                    'on': 'attendance_record.employee_id = employee.employee_id'
                },
                {
                    'type': 'LEFT',
                    'table1': 'attendance_record',
                    'table2': 'sys_user',
                    'on': 'attendance_record.approver_user_id = sys_user.user_id'
                }
            ],
            where_arg=select_data,
            select_columns=[
                "date",
                "absent",
                "shift_type",
                "checkin_time",
                "source",
                "checkout_time",
                "work_hours",
                "location",
                "approved_at",
                "late_minutes",
                "early_leave_minutes",
                "remark",
                "attendance_record.status",
                'employee.name_cn',
                "username"
            ]
        )
        if empl_contract_data:
            if empl_contract_data['data']:
                return empl_contract_data
            else:
                print("❌ didn't select data form select_empl_doc()")
                return empl_contract_data
        else:
            empl_contract_data = {'column_name':["error"],"data":["❌ mysql_select_dict error form select_empl_doc()"]}
            return empl_contract_data

    except Exception as e:
        print(f'❌ Unknow error from select_select_empl_doccont() : {e}')
        return {"column_name": ["error"],"data": [["Maybe Department name duplication from select_empl_doc()"]]}