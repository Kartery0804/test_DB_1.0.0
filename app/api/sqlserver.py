from app.services import with_mysql
from flask import jsonify
from app.api import api_bp


@api_bp.route('/sqlserver/<flag>', methods=['GET'])
def control_mysql(flag):
    if flag == "on":
        if with_mysql.start_mysql_service():
            return "on successful!"
        else:
            return "can't start"
    elif flag == "off":
        if with_mysql.stop_mysql_service():
            return "off successful!"
        else:
            return "can't stop!"