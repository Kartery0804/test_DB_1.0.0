from app.api import api_bp
from flask import jsonify,request
from app.services import connect_mysql as cm
from app.services import department_mysql as dm
from app.services import login_mysql as lm

@api_bp.route('/dept/show', methods=['POST'])
def dept_show():
    if not request.is_json:
        return jsonify({"error":"Invalid type of post"})
    try:
        data = request.get_json()
        conn = cm.connect_mysql(*cm.default)
        status = lm.login_mysql(conn,data['username'],data['password'])
        regulate_code = "0"


        response = None
        if status:
            regulate_code = lm.get_regulate_code(conn,data['username'])
            response = dm.read_info(conn,data["table_name"],r_flag = regulate_code)
            response["regulate_code"] = regulate_code
        else:
            response = {"column_name": ["error"],"data": ["Unable to verify login"]}
            response["regulate_code"] = "0"
        response["status"] = status
        return response
    except Exception as e:
        return jsonify({"regulate_code":0,"column_name": ["error"],"data": [str(e)]})
    finally:
        conn.close()

@api_bp.route('/dept/create', methods=['POST'])
def dept_create():
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
            if dm.add_dept(conn,data["dept_name"],data["dept_code"],data["parent_dept_name"],r_flag = regulate_code):
                response = dm.read_info(conn,"department",{"dept_name":data["dept_name"]},r_flag = regulate_code)
            else:
                response = {"column_name": ["error"],"data": [["Maybe Department name/code duplication from add_dept()"]]}
            
        else:
            response = {"column_name": ["error"],"data": [["Unable to verify login"]]}
            response["regulate_code"] = regulate_code
        response["status"] = status
        return response
    except Exception as e:
        return jsonify({"regulate_code":0,"column_name": ["error"],"data": [[str(e)]]})
    finally:
        conn.close()
        
@api_bp.route('/dept/delete', methods=['POST'])
def dept_delete():
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
            if dm.delete_dept(conn,data["dept_name"],r_flag = regulate_code):
                response = dm.read_info(conn,"department",r_flag = regulate_code)
            else:
                response = {"column_name": ["error"],"data": [["Maybe Department name duplication from delete_dept()"]]}
            
        else:
            response = {"column_name": ["error"],"data": [["Unable to verify login"]]}
            response["regulate_code"] = regulate_code
        response["status"] = status
        return response
    except Exception as e:
        return jsonify({"regulate_code":0,"column_name": ["error"],"data": [[str(e)]]})
    finally:
        conn.close()
@api_bp.route('/dept/update', methods=['POST'])
def dept_update():
    """
    'username':str.
    "passward":str
    dept_name: str,
    new_dept_name: str = None,
    dept_code: str = None,
    parent_dept_name: str = None,
    manager_employee_id: str = None,
    status: int = None
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
            if dm.update_dept(conn,data['dept_name'],data['new_dept_name'],data['dept_code'],data['parent_dept_name'],data['manager_employee_id'],data['status'],r_flag = regulate_code):
                response = dm.read_info(conn,"department",{"dept_name":data["dept_name"]},r_flag = regulate_code)
            else:
                response = {"column_name": ["error"],"data": [["Maybe Department name duplication from update_dept()"]]}
            
        else:
            response = {"column_name": ["error"],"data": [["Unable to verify login"]]}
            response["regulate_code"] = regulate_code
        response["status"] = status
        return response
    except Exception as e:
        return jsonify({"regulate_code":0,"column_name": ["error"],"data": [[str(e)],["dept_update 123"]]})
    finally:
        conn.close()
@api_bp.route('/dept/select', methods=['POST'])
def dept_select():
    """
    'username':str.
    "passward":str
    dept_name: str,
    dept_code: str = None,
    parent_dept_name: str = None,
    manager_employee_id: str = None,
    status: int = None
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
            select_data = dm.select_dept(conn,data['dept_name'],data['dept_code'],data['parent_dept_name'],data['manager_employee_id'],data['status'],r_flag = regulate_code)
            if select_data:
                response = select_data
            else:
                response = {"column_name": ["error"],"data": [["Maybe Department name duplication from select_dept()"]]}
            
        else:
            response = {"column_name": ["error"],"data": [["Unable to verify login"]]}
            response["regulate_code"] = regulate_code
        response["status"] = status
        return response
    except Exception as e:
        return jsonify({"regulate_code":0,"column_name": ["error"],"data": [[str(e)],["dept_select"]]})
    finally:
        conn.close()