
def regulate(role_code: int):
    def decorator(func):
        def wrapper(*args, **kwargs):
            flag = kwargs.pop('r_flag', 0)
            
            # 处理特殊权限（role_code < 0）
            if role_code < 0:
                if flag != role_code:
                    print(f"( {role_code} : {flag} Lack of special permissions)")
                    return f"( {role_code} : {flag} Lack of special permissions)"
                else:
                    return func(*args, **kwargs)
            
            # 处理普通权限（role_code >= 0）- 使用二进制位判断
            if role_code & flag != role_code:  # 检查flag的所有权限位是否都包含在role_code中
                print(f"( {role_code} : {flag} permission denied)")
                return f"( {role_code} : {flag} permission denied)"
            
            return func(*args, **kwargs)
        return wrapper
    return decorator



if __name__ == '__main__':
    import flask
    from flask import request

    app = flask.Flask(__name__)

    @regulate(0)
    def p_hello(name:str):
        return f"Hello, {name}!"


    @app.route('/hello', methods=['POST'])
    def hello():
        return p_hello('kty',r_flag = request.get_json()['id'])


    app.run(port=25000, debug=True)  # 启动服务，端口5000