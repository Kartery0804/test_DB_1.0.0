from app.api import api_bp
from flask import jsonify,request,send_file
from app.services import login_mysql as lm
from app.services import connect_mysql as cm
from app.services import visual_attendrate_mysql as va
from app.services import config_mysql as cf
@api_bp.route('/attendrate/image',methods=['POST'])
def get_attendrate_image():
    if not request.is_json:
        return {"column_name": ["error"],"data": [["Invalid type of post 1011: from get_attendrate_image())"]]}
    try:
        data = request.get_json()
        conn = cm.connect_mysql(*cm.default)
        status = lm.login_mysql(conn,data['username'],data['password'])
        regulate_code = 0
        response = None
        if status:
            regulate_code = lm.get_regulate_code(conn,data['username'])
            if va.plot_monthly_attendance_rate_with_table(conn,data['month'],data['year'],output_path=f'attendance_table_{data['year']}_{data['month']}.png',r_flag = regulate_code):
                response = send_file(f'{cf.res_path}attendance_table_{data['year']}_{data['month']}.png', mimetype='image/jpeg')
                return response
            else:
                response = {"column_name": ["error"],"data": [["unknow error 1021: from get_attendrate_image()"]]}
        else:
            response = {"column_name": ["error"],"data": [["Unable to verify login 1031: from get_attendrate_image()"]]}
            response["regulate_code"] = regulate_code
        response["status"] = status
        return response
    except Exception as e:
        return jsonify({"regulate_code":0,"column_name": ["error"],"data": [[str(e)],["unknow error 1041:from get_attendrate_image()"]]})
    finally:
        conn.close()