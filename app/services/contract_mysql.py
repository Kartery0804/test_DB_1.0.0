import pymysql
from app.services import operation_mysql as om
from app.utils.permission import regulate
from app.utils import easy_query as eq
from app.services import config_mysql as cf


@regulate(0b1101)
def add_contract(conn:pymysql.Connection ,contract_no: str ,contract_type :str,employee_no:str,start_date:str,contract_status:str,sign_date:str=None,end_date:str=None,probation_months:int=None,termination_date:str=None,termination_reason:str=None,file_url:str=None,**kwargs):
    try:
        employee_id = None
        if employee_no:
            employee_data = om.mysql_select_dict(conn,"employee",{"employee_no":employee_no})["data"]
            if employee_data:
                employee_id = employee_data[0][0]
            else:
                print("didn't have this employee")
                return False

            
        field_mapping = {
            "contract_no":contract_no,
            "contract_type":contract_type,
            "employee_id":employee_id,
            "start_date":start_date,
            "contract_status":contract_status,
            "sign_date":sign_date,
            "end_date":end_date,
            "probation_months":probation_months,
            "termination_date":termination_date,
            "termination_reason":termination_reason,
            "file_url":file_url,
        }

        add_data = {
            "created_at": om.datetime.now(),
            "updated_at":om.datetime.now(),
            **{k: v for k, v in field_mapping.items() if v is not None}
        }
        if not om.mysql_select_dict(conn,"contract",{"contract_no":contract_no})["data"]:
            if om.mysql_insert_dict(conn,"contract",add_data) != None:
                return True
            else:
                raise Exception("error from mysql_insert_dict() 1111")
        else:
            print("❌ contract node duplication from add_contract() 1121")
            return False
        
        
    except Exception as e:
        print(f'❌ Unknow error from add_contract() : {e}')
        return False

@regulate(0b1101)
def renew_contract(conn:pymysql.Connection ,contract_no: str ,start_date:str,end_date:str,contract_type :str = None,probation_months:int=None,termination_date:str=None,termination_reason:str=None,file_url:str=None,**kwargs):
    try:
            
        field_mapping = {
            "contract_no":contract_no,
            "contract_type":contract_type,
            "start_date":start_date,
            "end_date":end_date,
            "probation_months":probation_months,
            "termination_date":termination_date,
            "termination_reason":termination_reason,
            "file_url":file_url,
            'contract_status':'active'
        }

        add_data = {
            "updated_at":om.datetime.now(),
            "sign_date":om.datetime.now(),
            **{k: v for k, v in field_mapping.items() if v is not None and v != ""}
        }
        if om.mysql_select_dict(conn,"contract",{"contract_no":contract_no})["data"]:
            if om.mysql_update_dict(conn,"contract",add_data,{"contract_no":contract_no}) != None:
                return True
            else:
                raise Exception("error from mysql_update_dict() 1112")
        else:
            print("❌ Department name/code duplication from add_contract() 1122")
            return False
        
        
    except Exception as e:
        print(f'❌ Unknow error from add_contract() : {e} 1132')
        return False