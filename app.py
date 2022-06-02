'''

@Date: 2022/06/02
@Author: Walker
@Description:

                这个是后端Flask服务器部分的大致的框架，主要工作就是适配前后端交互时的协议约定。



'''

'''

                Flask 需要的基本的导入

'''
from flask import Flask, render_template, request, redirect, make_response

app = Flask('Walker',
            template_folder="build", static_folder="build/static")

'''
                这里统一定义错误类型，包括(错误代码，错误输出)
'''
MethodNotFound = 'Method Not Found'
ParametersNotExpected = 'Parameters Not Expected'
UserNotFound = 'User Not Found Or Password Not Expected'

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
                        'error': None,
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
        'error': None,
        'result': {
            "data": data,
            "message": message
        },
        'success': True
    }
    return succ



methods = set()


# 这个是每次都有的用户验证，大概应该是和login的逻辑一样，但是返回值不是json，而是调用rpc
def userCheck(username, password):
    return {
        'username': 'walker'
    }

'''

                这部分都是前端可以调用的接口，这里会封装郭阳写好的接口，现在只有一个返回值模板，如果有不对的地方请告知

'''
class Service:

    def userLogin(self, param):
        # return ErrorTemplate(UserNotFound)
        return SuccessTemplate()

    def userSendOrder(self, param):
        # return ErrorTemplate(...)
        return SuccessTemplate()

    def userGetOrder(self, param):
        return SuccessTemplate({
            "charge_type": "fast",
            "charge_num": 0.53  # 我瞎写的
        })

    def userGetLineNo(self, param):
        return SuccessTemplate({
            "number": 10
        })

    def userGetRank(self, param):
        return SuccessTemplate({
            "number": 10
        })

    def userSendChargeType(self, param):
        return SuccessTemplate()

    def userSendCahrgeQuantity(self, param):
        return SuccessTemplate()

    def userSendCancelCharge(self, param):
        return SuccessTemplate()

    def userGetBill(self, param):
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

    def userGetBillsList(self, param):
        return SuccessTemplate([
            {"billID": 1, "billTime": 1234, "chargeQuantity": "high"}
        ])

    def adminLogin(self, param):
        # return ErrorTemplate(UserNotFound)
        return SuccessTemplate()

    def adminGetChargers(self, param):
        return SuccessTemplate([
            {"working": False, "totalChargeCount": 100, "totalChargeTime": 100, "totalChargeQuantity": "high"}
        ])

    def adminTurnCharger(self, param):
        return SuccessTemplate()

    def adminGetCars(self, param):
        return SuccessTemplate([
            {"username": "walker", "chargeQuantity": "high", "waitTime": 1234}
        ])

    def adminGetTable(self, param):
        return SuccessTemplate({
            "time": 1234, "chargerID": 1, "totalChargeCount": 10, "totalChargeTime": 100,
            "totalChargeQuantity": "high", "totalChargeCost": 100, "totalServiceCost": 100,
            "totalCost": 100
        })


'''
                我这里设计的是POST请求是这样：
                1. POST的路由全部为/api。
                2. 所有的POST都是rpc json
                3. 所有的输入都从req获取，解析req的时候就只看body的rpc json，不提取path variable 也不提取 request parameter
                4. POST不处理页面跳转任务，如果需要跳转，请在POST之后再发送GET（是我不太会写哈哈哈）
                5. 参数优先查询是否有目标方法以及目标方法的参数传递是否正确
                5. 无论是什么rpc，都首先检查头两个参数的用户信息，向郭阳传参时也没有拿掉。
'''


service = Service()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return render_template('index.html')


@app.route('/api', methods=['POST'])
def resp():
    req = request.json
    if req['method'] not in methods:
        return ErrorTemplate(MethodNotFound)

    username = req['params']['username']
    password = req['params']['password']

    if userCheck(username, password) is None:
        return ErrorTemplate(UserNotFound, {'username': username})
    try:
        result = eval('service.' + req['method'] + '(' + str(req['params']) + ')')
        return result
    except:
        return ErrorTemplate(ParametersNotExpected, req['params'])


if __name__ == '__main__':

    methods = set(dir(Service))
    # print(methods)
    app.run(port=8081)
