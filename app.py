'''

@Date: 2022/06/01
@Author: Walker
@Description:

                这个是后端Flask服务器部分的大致的框架，主要工作就是适配前后端交互时的协议约定。



'''

'''

                Flask 需要的基本的导入

'''
from flask import Flask, render_template, request, redirect, make_response

app = Flask('Walker')

'''
                这里统一定义错误类型，包括(错误代码，错误输出)
'''
MethodNotFound = (-32601, 'Method Not Found')
ParametersNumberNotExpected = (-36602, 'Parameter Number Not Expected')
UserNotFound = (0, 'User Not Found Or Password Not Expected')

'''
                ErrorObject做第一次封装，ErrorTemplate是最终的错误返回模板，假设遇到了方法不正确的错误，我将返回
                {
                    "jsonrpc": 2.0,
                    "success": false,
                    "error": {
                        "code": -32601,
                        "message": "Method Not Found",
                        "data": null
                    }
                }
'''


def ErrorObject(error, data):
    return {
        'code': error[0],
        'message': error[1],
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
                result是实际的返回数据，data代表额外信息，表示返回的信息是正确类型还是错误类型。
                例如getBillsList返回正确信息将返回：
                    {
                        'jsonrpc': 2.0,
                        'error': None,
                        'result': [
                            {"billID": 1, "billTime": 1234, "chargeQuantity": "high"}
                        ],
                        'success': True
                    }

'''


def SuccessTemplate(result):
    succ = {
        'jsonrpc': 2.0,
        'error': None,
        'result': result,
        'success': True
    }
    return succ


'''
                    
                    这里是前端可以调用的所有的函数的名字和对应的参数数量。

'''
methods = {
    'userLogin': 2,
    'userSendOrder': 4,
    'userGetOrder': 2,
    'userGetLineNo': 2,
    'userGetRank': 2,
    'userSendChargeType': 3,
    'userSendChargeQuantity': 3,
    'userSendCancelCharge': 2,
    'userGetBillsList': 2,
    'userGetBill': 3,
    'adminLogin': 2,
    'adminGetChargers': 2,
    'adminTurnCharger': 4,
    'adminGetCars': 3,
    'adminGetTable': 2
}

'''

                这部分都是在methods中出现过的rpc接口，这里会封装郭阳写好的接口，现在只有一个返回值模板，如果有不对的地方请告知

'''


def userCheck(username, password):
    return {
        'username': 'walker'
    }


def userLogin(param):
    # return ErrorTemplate(UserNotFound)
    return SuccessTemplate("success")


def userSendOrder(param):
    # return ErrorTemplate(...)
    return SuccessTemplate("success")


def userGetOrder(param):
    return SuccessTemplate({
        "charge_type": "fast",
        "charge_num": 0.53  # 我瞎写的
    })


def userGetLineNo(param):
    return SuccessTemplate({
        "number": 10
    })


def userGetRank(param):
    return SuccessTemplate({
        "number": 10
    })


def userSendChargeType(param):
    return SuccessTemplate("success")


def userSendCahrgeQuantity(param):
    return SuccessTemplate("success")


def userSendCancelCharge(param):
    return SuccessTemplate("success")


def userGetBill(param):
    return SuccessTemplate({
        "billID": 1,
        "billTime": 1234,
        "chargerID": 2,
        "chargeQuantity": "high",
        "chargeTime": 1234,
        "startTime": 1234,
        "endTime": 1234,
        "chargeCost": 100,
        "serviceCost": 100,
        "cost": 200
    })


def userGetBillsList(param):
    return SuccessTemplate([
        {"billID": 1, "billTime": 1234, "chargeQuantity": "high"}
    ])


def adminLogin(param):
    # return ErrorTemplate(UserNotFound)
    return SuccessTemplate("success")


def adminGetChargers(param):
    return SuccessTemplate([
        {"working": False, "totalChargeCount": 100, "totalChargeTime": 100, "totalChargeQuantity": "high"}
    ])


def adminTurnCharger(param):
    return SuccessTemplate("success")


def adminGetCars(param):
    return SuccessTemplate([
        {"username": "walker", "chargeQuantity": "high", "waitTime": 1234}
    ])


def adminGetTable(param):
    return SuccessTemplate({
        "time": 1234, "chargerID": 1, "totalChargeCount": 10, "totalChargeTime": 100,
        "totalChargeQuantity": "high", "totalChargeCost": 100, "totalServiceCost": 100,
        "totalCost": 100
    })


'''
                我这里设计的是POST请求是这样：
                1. POST的路由全部为根路由。
                2. 所有的POST都是rpc json
                3. 所有的输入都从req获取，解析req的时候就只看body的rpc json，不提取path variable 也不提取 request parameter
                4. POST不处理页面跳转任务，如果需要跳转，请在POST之后再发送GET（是我不太会写哈哈哈）
                5. 参数优先查询是否有目标方法以及目标方法的参数传递是否正确
                5. 无论是什么rpc，都首先检查头两个参数的用户信息，向郭阳传参时也没有拿掉。
'''


@app.route('/', methods=['POST'])
def resp():
    req = request.json
    if req['method'] not in methods:
        return ErrorTemplate(MethodNotFound)
    elif len(req['params']) != methods[req['method']]:
        return ErrorTemplate(ParametersNumberNotExpected)

    username = req['params'][0]
    password = req['params'][1]
    if userCheck(username, password) is None:
        return ErrorTemplate(UserNotFound, {'username': username})

    return eval(req['method'] + '(' + req['params'] + ')')


'''
                这里是GET请求的页面设计，但是我还没拿到前端页面，就暂时写成这样了，得到了前端页面再改
'''


@app.route('/login', methods=['GET'])
def login():
    return 'login'


@app.route('/user', methods=['GET'])
def user():
    return 'user'


@app.route('/admin', methods=['GET'])
def admin():
    return 'admin'


@app.route('/user/order', methods=['GET'])
def chargeInfo():
    return 'user_order'


@app.route('/user/order_info', methods=['GET'])
def orderInfo():
    return 'user_order_info'


@app.route('/user/bills', methods=['GET'])
def bills():
    return 'user_bills'


@app.route('/admin/chargers', methods=['GET'])
def getChargers():
    return 'chargers'


@app.route('/admin/chargers/cars', methods=['GET'])
def getCars():
    return 'cars'


@app.route('/admin/table', methods=['GET'])
def table():
    return 'table'


if __name__ == '__main__':
    app.run()
