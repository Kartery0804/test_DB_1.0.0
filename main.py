from app.services import with_mysql
from flask import Flask, request ,jsonify

app = Flask(__name__)

# 定义路由：当访问 /hello 时触发此函数
@app.route('/api/sqlsever/<flag>', methods=['GET'])
def hello(flag):
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

if __name__ == '__main__':
    app.run(port=25000, debug=True)  # 启动服务，端口5000