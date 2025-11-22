
def regulate(role_code):
    def decorator(func):
        def wrapper(*args, **kwargs):
            flag = kwargs.pop('r_flag', 0)
            if flag != role_code and role_code < 0:
                return f"( {role_code} : {flag} Lack of special permissions)"
            elif flag < role_code:
                return f"( {role_code} : {flag} permission denied)"
            else:
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