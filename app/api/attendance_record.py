from app.api import api_bp
from flask import jsonify,request
from app.services import connect_mysql as cm
from app.services import attendance_record_mysql as am
from app.services import login_mysql as lm
from app.services import operation_mysql as om
from app.services import department_mysql as dm

@api_bp.route('/attend_cod/add', methods=['POST'])
def attend_cod_add():
    """
    username :str 用户,
    passward :str 密码,
    employee_no:str 员工编号,
    date:str 日期,

    absent:int = None 旷工标识,
    shift_type:str = None 班次类型,
    checkin_time:str=None 上班打卡,
    source:str=None 数据来源 enum('device','import'),
    checkout_time:str=None 下班打卡,
    work_hours:str=None 工时,
    location:str=None 打卡地点,
    approver_user_name:str=None 审批人,
    approved_at:str=None 审批时间,
    late_minutes:int = None 迟到分钟, 
    early_leave_minutes:int=None 早退分钟,
    remark:str=None 备注
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
            if data['employee_no']:
                employee_data = om.mysql_select_dict(conn,"employee",{"employee_no":data['employee_no']})["data"]
            if employee_data:
                employee_id = employee_data[0][0]
            if am.add_attend_cod(conn,**data,r_flag = regulate_code):
                response = dm.read_info(conn,"attendance_record",{"date":data['date'],"employee_id":employee_id},r_flag = regulate_code)
            else:
                response = {"column_name": ["error"],"data": [["Maybe attend_cod date duplication from attend_cod_add()1121"]]}
            
        else:
            response = {"column_name": ["error"],"data": [["Unable to verify login1131"]]}
            response["regulate_code"] = regulate_code
        response["status"] = status
        return response
    except Exception as e:
        return jsonify({"regulate_code":0,"column_name": ["error1141"],"data": [[str(e)]]})
    finally:
        conn.close()


@api_bp.route('/attend_cod/update', methods=['POST'])
def attend_cod_update():
    """
    username :str 用户,
    passward :str 密码,
    employee_no:str 员工编号,
    date:str 日期,

    absent:int = None 旷工标识,
    shift_type:str = None 班次类型,
    checkin_time:str=None 上班打卡,
    source:str=None 数据来源 enum('device','import'),
    checkout_time:str=None 下班打卡,
    work_hours:str=None 工时,
    location:str=None 打卡地点,
    approved_user_name:str=None 审批人,
    approver_at:str=None 审批时间,
    late_minutes:int = None 迟到分钟, 
    early_leave_minutes:int=None 早退分钟,
    remark:str=None 备注,
    status:str=None enum('initial','corrected','approved','locked')
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
            if data['employee_no']:
                employee_data = om.mysql_select_dict(conn,"employee",{"employee_no":data['employee_no']})["data"]
            if employee_data:
                employee_id = employee_data[0][0]
            if am.update_attend_cod(conn,**data,r_flag = regulate_code):
                response = dm.read_info(conn,"attendance_record",{"date":data['date'],"employee_id":employee_id},r_flag = regulate_code)
            else:
                response = {"column_name": ["error"],"data": [["Maybe attend_cod date duplication from attend_cod_update()1122"]]}
            
        else:
            response = {"column_name": ["error"],"data": [["Unable to verify login1132"]]}
            response["regulate_code"] = regulate_code
        response["status"] = status
        return response
    except Exception as e:
        return jsonify({"regulate_code":0,"column_name": ["error1142"],"data": [[str(e)]]})
    finally:
        conn.close()

@api_bp.route('/attend_cod/select', methods=['POST'])
def attend_cod_select():
    """
    username :str 用户,
    passward :str 密码,
    employee_no:str=None 员工编号,
    date:st=None 日期,
    absent:int = None 旷工标识,
    shift_type:str = None 班次类型,
    checkin_time:str=None 上班打卡,
    source:str=None 数据来源 enum('device','import'),
    checkout_time:str=None 下班打卡,
    work_hours:str=None 工时,
    location:str=None 打卡地点,
    approver_user_name:str=None 审批人,
    approved_at:str=None 审批时间,
    late_minutes:int = None 迟到分钟, 
    early_leave_minutes:int=None 早退分钟,
    remark:str=None 备注
    status:str=None enum('initial','corrected','approved','locked')
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
            response = am.select_attend_cod(conn,**data,r_flag = regulate_code)
        else:
            response = {"column_name": ["error"],"data": [["Unable to verify login1123"]]}
            response["regulate_code"] = regulate_code
        response["status"] = status
        return response
    except Exception as e:
        return jsonify({"regulate_code":0,"column_name": ["error"],"data": [[str(e)],["attend_cod_select11133"]]})
    finally:
        conn.close()