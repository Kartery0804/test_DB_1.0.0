from app.api import api_bp
from flask import jsonify,request
from app.services import connect_mysql as cm
from app.services import department_mysql as dm
from app.services import login_mysql as lm
from app.services import contract_mysql as tm 
from app.services import operation_mysql as om

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
        return jsonify({"error":"Invalid type of post1111"})
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
                response = {"column_name": ["error"],"data": [["Maybe contract no/type duplication from cont_add()1121"]]}
            
        else:
            response = {"column_name": ["error"],"data": [["Unable to verify login1131"]]}
            response["regulate_code"] = regulate_code
        response["status"] = status
        return response
    except Exception as e:
        return jsonify({"regulate_code":0,"column_name": ["error1141"],"data": [[str(e)]]})
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

    
    probation_months:int=None 试用期（月）,
    termination_date:str=None 解约日期,
    termination_reason:str=None 解约原因,
    file_url:str=None 合同扫描件
    """
    if not request.is_json:
        return jsonify({"error":"Invalid type of post1112"})
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
                response = {"column_name": ["error"],"data": [["Maybe contract no/type duplication from cont_renew()1122"]]}
            
        else:
            response = {"column_name": ["error"],"data": [["Unable to verify login1132"]]}
            response["regulate_code"] = regulate_code
        response["status"] = status
        return response
    except Exception as e:
        return jsonify({"regulate_code":0,"column_name": ["error1142"],"data": [[str(e)]]})
    finally:
        conn.close()

@api_bp.route('/cont/temin', methods=['POST'])
def cont_termination():
    """
    username :str 用户,
    passward :str 密码,
    contract_no: str 合同编号,

    termination_reason:str=None 解约原因,
    """
    if not request.is_json:
        return jsonify({"error":"Invalid type of post1113"})
    try:
        data = request.get_json()
        conn = cm.connect_mysql(*cm.default)
        status = lm.login_mysql(conn,data['username'],data['password'])
        regulate_code = 0
        response = None
        if status:
            regulate_code = lm.get_regulate_code(conn,data['username'])
            if tm.termination_contract(conn,**data,r_flag = regulate_code):
                response = dm.read_info(conn,"contract",{"contract_no":data['contract_no']},r_flag = regulate_code)
                response["empl_status"] = "resigned"
            else:
                response = {"column_name": ["error"],"data": [["Maybe contract no/type duplication from cont_termination()1123"]]}
            
        else:
            response = {"column_name": ["error"],"data": [["Unable to verify login1133"]]}
            response["regulate_code"] = regulate_code
        response["status"] = status
        return response
    except Exception as e:
        return jsonify({"regulate_code":0,"column_name": ["error1143"],"data": [[str(e)]]})
    finally:
        conn.close()

@api_bp.route('/cont/select', methods=['POST'])
def cont_select():
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
            response = tm.select_cont(conn,**data,r_flag = regulate_code)
        else:
            response = {"column_name": ["error"],"data": [["Unable to verify login"]]}
            response["regulate_code"] = regulate_code
        response["status"] = status
        return response
    except Exception as e:
        return jsonify({"regulate_code":0,"column_name": ["error"],"data": [[str(e)],["cont_select"]]})
    finally:
        conn.close()

#人员档案

@api_bp.route('/empl_doc/add', methods=['POST'])
def empl_doc_add():
    """
    username :str 用户,
    passward :str 密码,
    doc_type :str ID_copy/diploma/cert/NDA/...,
    employee_no:str 员工编号,
    title:str 标题,
    file_url:str 文件地址,

    is_confidential:int=None 是否涉密,
    issued_by:str=None 签发单位,
    issued_date:str=None 签发日期,
    expire_date:str=None 到期时间,
    verified_by_user_id:str=None 校验人,
    verified_at:str=None 校验时间,
    remark:str=None 备注
    """

    if not request.is_json:
        return jsonify({"error":"Invalid type of post"})
    try:
        data = request.get_json()
        conn = cm.connect_mysql(*cm.default)
        status = lm.login_mysql(conn,data['username'],data['password'])
        regulate_code = 0
        response = None
        employee_id = None
        employee_data = om.mysql_select_dict(conn,"employee",{"employee_no":data['employee_no']})["data"]
        if employee_data:
            employee_id = employee_data[0][0]
        if status:
            regulate_code = lm.get_regulate_code(conn,data['username'])
            if tm.add_empl_doc(conn,**data,r_flag = regulate_code):
                response = dm.read_info(conn,"employee_document",{"employee_id":employee_id,"doc_type":data['doc_type'],"title":data['title']},r_flag = regulate_code)
            else:
                response = {"column_name": ["error"],"data": [["Maybe employee_document name duplication from empl_doc_add()"]]}
            
        else:
            response = {"column_name": ["error"],"data": [["Unable to verify login"]]}
            response["regulate_code"] = regulate_code
        response["status"] = status
        return response
    except Exception as e:
        return jsonify({"regulate_code":0,"column_name": ["error"],"data": [[str(e)]]})
    finally:
        conn.close()

@api_bp.route('/empl_doc/select', methods=['POST'])
def empl_doc_select():
    """
    username :str 用户,
    passward :str 密码,
    doc_type :str ID_copy/diploma/cert/NDA/...,
    employee_no:str 员工编号,
    title:str 标题,
    file_url:str 文件地址,
    is_confidential:int 是否涉密,
    issued_by:str=None 签发单位,
    issued_date:str=None 签发日期,
    expire_date:str=None 到期时间,
    verified_by_user_id:str=None 校验人,
    verified_at:str=None 校验时间,
    remark:str=None 备注
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
            response = tm.select_empl_doc(conn,**data,r_flag = regulate_code)
        else:
            response = {"column_name": ["error"],"data": [["Unable to verify login"]]}
            response["regulate_code"] = regulate_code
        response["status"] = status
        return response
    except Exception as e:
        return jsonify({"regulate_code":0,"column_name": ["error"],"data": [[str(e)],["empl_doc_select"]]})
    finally:
        conn.close()
