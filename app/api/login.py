from app.api import api_bp
from flask import jsonify,request
from app.services import login_mysql as lm
from app.services import connect_mysql as cm
"""
{
    "username":"kartery",
    "password":"my_password"
}

"""


@api_bp.route('/login', methods=['POST'])
def login():
    if not request.is_json:
        return jsonify({"error":"Invalid type of post"})
    try:
        data = request.get_json()
        conn = cm.connect_mysql(*cm.default)
        status = lm.login_mysql(conn,data['username'],data['password'],r_flag = data['permission'])
        regulate_code = None
        if status:
            regulate_code = lm.get_regulate_code(conn,data['username'],0)
        response = {
            "state": status,
            "regulate_code": regulate_code,
            "received": data,
        }
        return response
    except Exception as e:
        return jsonify({"error":"Unknow error!","msg":e})
    finally:
        conn.close()
    

    
