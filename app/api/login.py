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

@api_bp.route('/test_connect', methods=['GET'])
def test_connect():
    return {
        "column_name": ["server"],
            "data": [
                [
                    "Hello user,welcome to connected",
                ]
            ] 
    }


@api_bp.route('/login', methods=['POST'])
def login():
    if not request.is_json:
        return jsonify({"error":"Invalid type of post"})
    try:
        data = request.get_json()
        conn = cm.connect_mysql(*cm.default)
        status = lm.login_mysql(conn,data['username'],data['password'],r_flag = data['regulate_code'])
        regulate_code = "-1"
        if status:
            regulate_code = lm.get_regulate_code(conn,data['username'],0)
            print('✅ Get regulate_code success!')
        response = {
            "status": True,
            "regulate_code":13,
            "status_code":"0000",
            "column_name": ["status","regulate_code","received"],
            "data": [
                [
                    status,
                    regulate_code,
                    str(data)
                ],
                [
                    False,
                    15,
                    "Hello user here is admin's responce"
                ]
            ]
        }
        return response
    except Exception as e:
        return jsonify({"error":"Unknow error!","msg":e})
    finally:
        conn.close()
    

    
