import pymysql
from app.services import operation_mysql as om
from app.utils.permission import regulate
from app.utils import easy_query as eq
from app.services import config_mysql as cf

@regulate(0b1101)
def add_attend_cod(conn:pymysql.Connection ,date: str,employee_no:str,absent:int = None,shift_type:str = None,checkin_time:str=None,source:str=None,checkout_time:str=None,work_hours:str=None,location:str=None,approver_user_name:str=None,approver_at:str=None,late_minutes:int = None,early_leave_minute:int=None,remark:str=None,**kwargs):
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
            "approver_at":approver_at,
            "late_minutes":late_minutes,
            "early_leave_minute":early_leave_minute,
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
def update_attend_cod(conn:pymysql.Connection ,date: str,employee_no:str,absent:int = None,shift_type:str = None,checkin_time:str=None,source:str=None,checkout_time:str=None,work_hours:str=None,location:str=None,approver_user_name:str=None,approver_at:str=None,late_minutes:int = None,early_leave_minute:int=None,remark:str=None,status:str=None,**kwargs):
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
            "approver_at":approver_at,
            "late_minutes":late_minutes,
            "early_leave_minute":early_leave_minute,
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