'''

@Date: 2022/06/02
@Author: Walker
@Description:

                这个是后端Flask服务器部分的大致的框架，主要工作就是适配前后端交互时的协议约定。



'''
import logging

from flask import Flask, render_template, request

import admin_service as ms
import db as db
import structure as st
import user_service as us

'''

                Flask 需要的基本的导入

'''

app = Flask('app',
            template_folder="build", static_folder="build/static")

'''
                这里统一定义错误类型，包括(错误代码，错误输出)
'''
MethodNotFound = 'Method Not Found'
ParametersNotExpected = 'Parameters Not Expected'

'''
                ErrorObject做第一次封装，ErrorTemplate是最终的错误返回模板，假设遇到了方法不正确的错误，我将返回
                {
                    "jsonrpc": 2.0,
                    "success": false,
                    "error": {
                        "message": "Method Not Found",
                        "data": null
                    }
                }
'''


def ErrorObject(error, data):
    return {
        'message': error,
        'data': data
    }


def ErrorTemplate(error, data=None):
    return {
        'jsonrpc': 2.0,
        'error': ErrorObject(error, data),
        'success': False
    }


'''
                返回正确的resp的标准格式，这里是按照json rpc的标准定义的，
                result是实际的返回数据，data代表返回数据，message表示返回的数据说明，
                success表示返回的信息是正确类型还是错误类型。
                例如getBillsList返回正确信息将返回：
                    {
                        'jsonrpc': 2.0,
                        'result' : {
                            "message" : "success",
                            "data" : [
                                {"billID": 1, "billTime": 1234, "chargeQuantity": "high"}
                            ]
                        },
                        'success': true
                    }


'''


def SuccessTemplate(data=None, message="success"):
    succ = {
        'jsonrpc': 2.0,
        'result': {
            "data": data,
            "message": message
        },
        'success': True
    }
    return succ


# 这个是每次都有的用户验证，大概应该是和login的逻辑一样，但是返回值不是json，而是调用rpc
def userCheck(username, password):
    return {
        'username': 'walker'
    }


'''

                这部分都是前端可以调用的接口，这里会封装郭阳写好的接口，现在只有一个返回值模板，如果有不对的地方请告知

'''

'''
                我这里设计的是POST请求是这样：
                1. POST的路由全部为/api。
                2. 所有的POST都是rpc json
                3. 所有的输入都从req获取，解析req的时候就只看body的rpc json，不提取path variable 也不提取 request parameter
                4. POST不处理页面跳转任务，如果需要跳转，请在POST之后再发送GET（是我不太会写哈哈哈）
                5. 参数优先查询是否有目标方法以及目标方法的参数传递是否正确
                5. 无论是什么rpc，都首先检查头两个参数的用户信息，向郭阳传参时也没有拿掉。
'''

db = db.DB("data")
pd = st.PublicDataStruct(db)
userService = us.Service(db, pd)
adminService = ms.Service(db, pd)


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return render_template('index.html')


@app.route('/api', methods=['POST'])
def resp():
    req = request.json

    result, err = None, None

    try:
        method = req["method"]
        params = req['params']
        user = {"username": req['params']['username'], "password": req['params']['password']}
    except KeyError:
        return ErrorTemplate(ParametersNotExpected)

    if method == "userLogin":
        result, err = userService.userLogin(**user)

    elif method == "userRegister":
        result, err = userService.userRegister(**user)

    elif method == "adminLogin":
        result, err = adminService.adminLogin(**user)

    else:
        params.pop('password', None)
        try:
            if method.startswith("user"):
                fn = getattr(userService, method)
                result, err = fn(**params)
                pd.writestatenow()
            elif method.startswith("admin"):
                fn = getattr(adminService, method)
                result, err = fn(**params)
                pd.writestatenow()
            else:
                err = MethodNotFound
        except AttributeError as e:
            logging.getLogger('app').error(str(e))
            err = MethodNotFound

    print(method)

    if err is None:
        return SuccessTemplate(result)
    else:
        return ErrorTemplate(err)


if __name__ == '__main__':
    logging.basicConfig(format="%(message)s")

    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)

    fileHandler = logging.FileHandler("log.txt", encoding="utf-8")
    log = logging.getLogger('app')
    log.setLevel(logging.INFO)
    log.addHandler(fileHandler)

    fileHandler2 = logging.FileHandler("state.txt", encoding="utf-8")
    log2 = logging.getLogger('state')
    log2.setLevel(logging.INFO)
    log2.addHandler(fileHandler2)

    app.debug = True
    app.run(port=8081)
