from app.api import api_bp
from flask import jsonify,request
from app.services import connect_mysql as cm
from app.services import department_mysql as dm
from app.services import login_mysql as lm
from app.services import employee_mysql as em 

@api_bp.route('/empl/create', methods=['POST'])
def empl_create():
    """
    必填项：
    "username":"kartery",
    "password":"my_password",
    "regulate_code":0,
    "dept_name":"Animation Dept",
    "employee_no": "114568421",
    "name_cn": "王五",
    "hire_date": "2025-11-30",
    "employment_type": "intern",
    "dept_name": "Animation Dept",
    "status": "active",
    "position_name": "Concept_Art"

    选填项：
    manager_employee_no:"23907508"
    """
    if not request.is_json:
        return {"column_name": ["error"],"data": [["Invalid type of post 1011: from empl_update())"]]}
    try:
        data = request.get_json()
        conn = cm.connect_mysql(*cm.default)
        status = lm.login_mysql(conn,data['username'],data['password'])
        regulate_code = 0
        response = None
        if status:
            regulate_code = lm.get_regulate_code(conn,data['username'])
            if em.add_employee(conn,**data,r_flag = regulate_code):
                em.update_employee(conn,data['employee_no'],data['username'])
                response = em.select_employee(conn,data['employee_no'],r_flag = regulate_code)
            else:
                response = {"column_name": ["error"],"data": [["unknow error 1021: from empl_create()"]]}
            
        else:
            response = {"column_name": ["error"],"data": [["Unable to verify login 1031: from empl_create()"]]}
            response["regulate_code"] = regulate_code
        response["status"] = status
        return response
    except Exception as e:
        return jsonify({"regulate_code":0,"column_name": ["error"],"data": [[str(e)],["unknow error 1001:from empl_create()"]]})
    finally:
        conn.close()

@api_bp.route('/empl/update', methods=['POST'])
def empl_update():
    """
    必填项：
    "username":"kartery",
    "password":"my_password",

    选填项(所有字段):
    "dept_name":"Animation Dept",
    "employee_no": "114568421",
    "name_cn": "王五",
    "hire_date": "2025-11-30",
    "employment_type": "intern",
    "dept_name": "Animation Dept",
    "status": "active",
    "position_name": "Concept_Art",
    "manager_employee_no":"23907508"
    name_en: str = None,
    gender: str = None,
    date_of_birth: str = None,
    id_number: str = None,
    phone: str = None,
    email: str = None,
    probation_end_date: str = None,
    work_location: str = None,
    salary_base: str = None,
    bank_name: str = None,
    bank_account_no: str = None,
    social_city: str = None,
    address: str = None,
    emergency_name: str = None,
    emergency_phone: str = None,
    photo_url: str = None,
    """
    if not request.is_json:
        return {"column_name": ["error"],"data": [["Invalid type of post 1012: from empl_update())"]]}
    try:
        data = request.get_json()
        conn = cm.connect_mysql(*cm.default)
        status = lm.login_mysql(conn,data['username'],data['password'])
        regulate_code = 0
        response = None
        if status:
            regulate_code = lm.get_regulate_code(conn,data['username'])
            if em.select_employee(conn,**data,r_flag = regulate_code)['data']:
                em.update_employee(conn,**data,r_flag = regulate_code)
                response = em.select_employee(conn,data['employee_no'],r_flag = regulate_code)
            else:
                response = {"column_name": ["error"],"data": [["unknow error 1022: from empl_update()"]]}
            
        else:
            response = {"column_name": ["error"],"data": [["Unable to verify login 1032: from empl_update()"]]}
            response["regulate_code"] = regulate_code
        response["status"] = status
        return response
    except Exception as e:
        return jsonify({"regulate_code":0,"column_name": ["error"],"data": [[str(e)],["unknow error 1002:from empl_update()"]]})
    finally:
        conn.close()

@api_bp.route('/empl/select', methods=['POST'])
def empl_select():
    """
    必填项：
    "username":"kartery",
    "password":"my_password",

    选填项(所有字段):
    "dept_name":"Animation Dept",
    "employee_no": "114568421",
    "name_cn": "王五",
    "hire_date": "2025-11-30",
    "employment_type": "intern",
    "dept_name": "Animation Dept",
    "status": "active",
    "position_name": "Concept_Art",
    "manager_employee_no":"23907508"
    name_en: str = None,
    gender: str = None,
    date_of_birth: str = None,
    id_number: str = None,
    phone: str = None,
    email: str = None,
    probation_end_date: str = None,
    work_location: str = None,
    salary_base: str = None,
    bank_name: str = None,
    bank_account_no: str = None,
    social_city: str = None,
    address: str = None,
    emergency_name: str = None,
    emergency_phone: str = None,
    photo_url: str = None,
    """
    if not request.is_json:
        return {"column_name": ["error"],"data": [["Invalid type of post 1013: from empl_select()"]]}
    try:
        data = request.get_json()
        conn = cm.connect_mysql(*cm.default)
        status = lm.login_mysql(conn,data['username'],data['password'])
        regulate_code = 0
        response = None
        if status:
            regulate_code = lm.get_regulate_code(conn,data['username'])
            response = em.select_employee(conn,**data,r_flag = regulate_code)
            if not response['data']:
                response = {"column_name": ["error"],"data": [["No such items 1023: from empl_select()"]]}
            
        else:
            response = {"column_name": ["error"],"data": [["Unable to verify login 1033:from empl_select()"]]}
            response["regulate_code"] = regulate_code
        response["status"] = status
        return response
    except Exception as e:
        return jsonify({"regulate_code":0,"column_name": ["error"],"data": [[str(e)],["unknow error 1003:from empl_select()"]]})
    finally:
        conn.close()


