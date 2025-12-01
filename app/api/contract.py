from app.api import api_bp
from flask import jsonify,request
from app.services import connect_mysql as cm
from app.services import department_mysql as dm
from app.services import login_mysql as lm
from app.services import contract_mysql as tm 

@api_bp.route('/cont/add', methods=['POST'])
def cont_add():
    """
    username :str 用户,
    passward :str 密码,
    contract_no: str 合同编号,
    contract_type :str fixed/open/intern ,
    employee_no:str 员工编号,
    start_date:str 生效日期,
    contract_status:str ('active','draft','terminated'),

    sign_date:str=None 签订日期,
    end_date:str=None 结束日期,
    probation_months:int=None 试用期（月）,
    termination_date:str=None 解约日期,
    termination_reason:str=None 解约原因,
    file_url:str=None 合同扫描件
    """
    if not request.is_json:
        return jsonify({"error":"Invalid type of post"})
    try:
        data = request.get_json()
        conn = cm.connect_mysql(*cm.default)
        status = lm.login_mysql(conn,data['username'],data['password'])
        regulate_code = 0
        response = None
        if status:
            regulate_code = lm.get_regulate_code(conn,data['username'])
            if tm.add_contract(conn,**data,r_flag = regulate_code):
                response = dm.read_info(conn,"contract",{"contract_no":data['contract_no']},r_flag = regulate_code)
            else:
                response = {"column_name": ["error"],"data": [["Maybe contract no/type duplication from cont_add()1111"]]}
            
        else:
            response = {"column_name": ["error"],"data": [["Unable to verify login1121"]]}
            response["regulate_code"] = regulate_code
        response["status"] = status
        return response
    except Exception as e:
        return jsonify({"regulate_code":0,"column_name": ["error1131"],"data": [[str(e)]]})
    finally:
        conn.close()

@api_bp.route('/cont/renew', methods=['POST'])
def cont_renew():
    """
    username :str 用户,
    passward :str 密码,
    contract_no: str 合同编号,
    end_date:str 结束日期,
    start_date:str 生效日期,

    
    contract_type :str=None fixed/open/intern ,
    probation_months:int=None 试用期（月）,
    termination_date:str=None 解约日期,
    termination_reason:str=None 解约原因,
    file_url:str=None 合同扫描件
    """
    if not request.is_json:
        return jsonify({"error":"Invalid type of post"})
    try:
        data = request.get_json()
        conn = cm.connect_mysql(*cm.default)
        status = lm.login_mysql(conn,data['username'],data['password'])
        regulate_code = 0
        response = None
        if status:
            regulate_code = lm.get_regulate_code(conn,data['username'])
            if tm.renew_contract(conn,**data,r_flag = regulate_code):
                response = dm.read_info(conn,"contract",{"contract_no":data['contract_no']},r_flag = regulate_code)
            else:
                response = {"column_name": ["error"],"data": [["Maybe contract no/type duplication from cont_renew()1112"]]}
            
        else:
            response = {"column_name": ["error"],"data": [["Unable to verify login1122"]]}
            response["regulate_code"] = regulate_code
        response["status"] = status
        return response
    except Exception as e:
        return jsonify({"regulate_code":0,"column_name": ["error1132"],"data": [[str(e)]]})
    finally:
        conn.close()