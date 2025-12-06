from app.api import api_bp
from flask import jsonify,request,send_file
from app.services import login_mysql as lm
from app.services import connect_mysql as cm
from app.services import visual_turnover_mysql as vt
from app.services import config_mysql as cf
@api_bp.route('/turnover/image',methods=['POST'])
def get_turnover_image():
    if not request.is_json:
        return {"column_name": ["error"],"data": [["Invalid type of post 1011: from get_turnover_image())"]]}
    try:
        data = request.get_json()
        conn = cm.connect_mysql(*cm.default)
        status = lm.login_mysql(conn,data['username'],data['password'])
        regulate_code = 0
        response = None
        if status:
            regulate_code = lm.get_regulate_code(conn,data['username'])
            if vt.generate_monthly_turnover_rate_no_table(conn,data['year'],output_file=f'turnover_rate_{data['year']}_fixed.png',r_flag = regulate_code):
                response = send_file(f'{cf.res_path}turnover_rate_{data['year']}_fixed.png', mimetype='image/jpeg')
                return response
            else:
                response = {"column_name": ["error"],"data": [["unknow error 1021: from get_turnover_image()"]]}
        else:
            response = {"column_name": ["error"],"data": [["Unable to verify login 1031: from get_turnover_image()"]]}
            response["regulate_code"] = regulate_code
        response["status"] = status
        return response
    except Exception as e:
        return jsonify({"regulate_code":0,"column_name": ["error"],"data": [[str(e)],["unknow error 1041:from get_turnover_image()"]]})
    finally:
        conn.close()