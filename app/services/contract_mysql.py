import pymysql
from app.services import operation_mysql as om
from app.utils.permission import regulate
from app.utils import easy_query as eq
from app.services import config_mysql as cf


@regulate(0b1101)
def add_contract(conn:pymysql.Connection ,contract_no: str ,contract_type :str,employee_no:str,start_date:str,contract_status:str = None,sign_date:str=None,end_date:str=None,probation_months:int=None,termination_date:str=None,termination_reason:str=None,file_url:str=None,**kwargs):
    try:
        employee_id = None
        if employee_no:
            employee_data = om.mysql_select_dict(conn,"employee",{"employee_no":employee_no})["data"]
            if employee_data:
                employee_id = employee_data[0][0]
            else:
                print("❌ didn't have this employee")
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
            "file_url":file_url
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
            print("❌ Department name/code duplication from renew_contract() 1122")
            return False
        
        
    except Exception as e:
        print(f'❌ Unknow error from renew_contract() : {e} 1132')
        return False

@regulate(0b1101)
def termination_contract(conn:pymysql.Connection ,contract_no: str ,termination_reason:str=None,**kwargs):
    try:
        employee_id = None
        contract_data = om.mysql_select_dict(conn,"contract",{"contract_no":contract_no})["data"]
        if contract_data:
            employee_id = contract_data[0][1]
        else:
            print("❌ didn't have this contract")
            return False
        employee_data = om.mysql_select_dict(conn,"employee",{"employee_id":employee_id})["data"]
        if not employee_data:
            print("❌ didn't have this employee")
            return False
        field_mapping = {
            "termination_reason":termination_reason,
            'contract_status':'terminated'
        }

        cont_update_data = {
            "updated_at":om.datetime.now(),
            "termination_date":om.datetime.now(),
            **{k: v for k, v in field_mapping.items() if v is not None and v != ""}
        }
        empl_update_data = {
            "updated_at":om.datetime.now(),
            "status":"resigned"
        }
        if om.mysql_select_dict(conn,"contract",{"contract_no":contract_no})["data"]:
            if om.mysql_update_dict(conn,"contract",cont_update_data,{"contract_no":contract_no}) != None:
                return True
            else:
                raise Exception("error from termination_contract() 1113")
        else:
            print("❌ contract node duplication from termination_contract() 1123")
            return False
        
        
    except Exception as e:
        print(f'❌ Unknow error from termination_contract() : {e} 1133')
        return False
    
@regulate(0b1101)
def select_cont(conn:pymysql.Connection ,contract_no: str =None,contract_type :str=None,employee_no:str=None,start_date:str=None,contract_status:str = None,sign_date:str=None,end_date:str=None,probation_months:int=None,termination_date:str=None,termination_reason:str=None,file_url:str=None,**kwargs):
    try:
        employee_id = None
        if employee_no:
            employee_data = om.mysql_select_dict(conn,"employee",{"employee_no":employee_no})["data"]
            if employee_data:
                employee_id = employee_data[0][0]
            else:
                print("❌ didn't have this employee")
        
        field_mapping = {
            "contract_no":contract_no,
            "contract_type":contract_type,
            "contract.employee_id":employee_id,
            "start_date":start_date,
            "contract_status":contract_status,
            "sign_date":sign_date,
            "end_date":end_date,
            "probation_months":probation_months,
            "termination_date":termination_date,
            "termination_reason":termination_reason,
            "file_url":file_url
        }
        select_data = {
            **{k: v for k, v in field_mapping.items() if v is not None}
        }
        cont_data = om.mysql_select_dict(conn,
            tables=['contract'],  # 主表使用别名
            join_conditions=[
                {
                    'type': 'LEFT',
                    'table1': 'contract',
                    'table2': 'employee',
                    'on': 'contract.employee_id = employee.employee_id'
                }
            ],
            where_arg=select_data,
            select_columns=[
                'employee.name_cn', 
                'employee_no',
                "contract_no",
                "contract_type",
                "start_date",
                "contract_status",
                "sign_date",
                "end_date",
                "probation_months",
                "termination_date",
                "termination_reason",
                "file_url"
            ]
        )
        if cont_data:
            if cont_data['data']:
                return cont_data
            else:
                print("❌ didn't select data form select_cont()")
                return cont_data
        else:
            cont_data = {'column_name':["error"],"data":["❌ mysql_select_dict error form select_cont()"]}
            return cont_data

    except Exception as e:
        print(f'❌ Unknow error from select_cont() : {e}')
        return {"column_name": ["error"],"data": [["Maybe Department name duplication from select_cont()"]]}
    

#员工档案
@regulate(0b1101)
def add_empl_doc(conn:pymysql.Connection ,doc_type :str,employee_no:str,title:str,file_url:str,is_confidential:int = None,issued_by:str=None,issued_date:str=None,expire_date:str=None,verified_by_user_id:str=None,verified_at:str=None,remark:str=None,**kwargs):
    try:
        employee_id = None
        if employee_no:
            employee_data = om.mysql_select_dict(conn,"employee",{"employee_no":employee_no})["data"]
            if employee_data:
                employee_id = employee_data[0][0]
            else:
                print("❌ didn't have this employee")
                return False

            
        field_mapping = {
            "doc_type":doc_type,
            "employee_id":employee_id,
            "title":title,
            "is_confidential":is_confidential,
            "issued_by":issued_by,
            "issued_date":issued_date,
            "expire_date":expire_date,
            "verified_by_user_id":verified_by_user_id,
            "verified_at":verified_at,
            "remark":remark,
            "file_url":file_url
        }

        add_data = {
            "created_at": om.datetime.now(),
            "updated_at":om.datetime.now(),
            **{k: v for k, v in field_mapping.items() if v is not None}
        }
        if not om.mysql_select_dict(conn,"employee_document",{"employee_id":employee_id,"doc_type":doc_type,"title":title})["data"]:
            if om.mysql_insert_dict(conn,"employee_document",add_data) != None:
                return True
            else:
                raise Exception("error from mysql_insert_dict() 1114")
        else:
            print("❌ empl_document name duplication from add_empl_doc() 1124")
            return False
        
        
    except Exception as e:
        print(f'❌ Unknow error from add_empl_doc()1134 : {e}')
        return False
    
@regulate(0b1101)
def select_empl_doc(conn:pymysql.Connection ,doc_type :str=None,employee_no:str=None,title:str=None,file_url:str=None,is_confidential:int = None,issued_by:str=None,issued_date:str=None,expire_date:str=None,verified_by_user_id:str=None,verified_at:str=None,remark:str=None,**kwargs):
    try:
        employee_id = None
        if employee_no:
            employee_data = om.mysql_select_dict(conn,"employee",{"employee_no":employee_no})["data"]
            if employee_data:
                employee_id = employee_data[0][0]
            else:
                print("❌ didn't have this employee")
        
        field_mapping = {
            "doc_type":doc_type,
            "employee_document.employee_id":employee_id,
            "title":title,
            "is_confidential":is_confidential,
            "issued_by":issued_by,
            "issued_date":issued_date,
            "expire_date":expire_date,
            "verified_by_user_id":verified_by_user_id,
            "verified_at":verified_at,
            "remark":remark,
            "file_url":file_url
        }
        select_data = {
            **{k: v for k, v in field_mapping.items() if v is not None}
        }
        empl_contract_data = om.mysql_select_dict(conn,
            tables=['employee_document'],  # 主表使用别名
            join_conditions=[
                {
                    'type': 'LEFT',
                    'table1': 'employee_document',
                    'table2': 'employee',
                    'on': 'employee_document.employee_id = employee.employee_id'
                },
                {
                    'type': 'LEFT',
                    'table1': 'employee_document',
                    'table2': 'sys_user',
                    'on': 'employee_document.verified_by_user_id = sys_user.user_id'
                }
            ],
            where_arg=select_data,
            select_columns=[
                "title",
                "doc_type",
                'employee.name_cn',
                "is_confidential",
                "issued_by",
                "issued_date",
                "expire_date",
                "verified_by_user_id",
                "verified_at",
                "remark",
                "file_url",
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