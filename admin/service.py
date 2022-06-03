class Service:
    def __init__(self, db):
        self.db = db

    """
    params
        username            用户名
        password            密码
    
    returns
        status              用于没有实际数据返回时，表示操作是否成功
        
    """

    def adminLogin(self, params):
        # data, err = None, "用户不存在"
        data, err = {
                        "status": True
                    }, None
        return data, err

    """
    params
        username            用户名

    returns
        chargerID           充电桩编号
        working             充电桩是否启动
        totalChargeCount    系统启动后充电桩累计充电次数
        totalChargeTime     系统启动后充电桩总计充电时间（毫秒时间戳）
        totalChargeQuantity 系统启动后充电桩总计充电量（度）
    """

    def adminGetChargers(self, params):
        data, err = [{
            "working": True,
            "totalChargeCount": 30,
            "totalChargeTime": 123456789,
            "totalChargeQuantity": 120
        }, {
            "working": False,
            "totalChargeCount": 12,
            "totalChargeTime": 123456789,
            "totalChargeQuantity": 120
        }, {
            "working": False,
            "totalChargeCount": 0,
            "totalChargeTime": 0,
            "totalChargeQuantity": 0
        }], None

        return data, err

    """
    params
        username            用户名
        chargerID           充电桩编号
        turn                启动或关闭充电桩（"on" or "off"）
        
    returns
        status              用于没有实际数据返回时，表示操作是否成功
    
    """

    def adminTurnCharger(self, params):
        data, err = {
                        "status": True
                    }, None
        return data, err

    """
    params
        username            用户名
        chargerID           充电桩编号
        
    returns
        username            充电桩服务的用户名
        chargeQuantity      用户充电量（度）
        waitingTime         用户等待时间（毫秒时间戳）
    """

    def adminGetUsers(self, params):
        data, err = [
                        {
                            "username": "walker",
                            "chargeQuantity": 24,
                            "waitTime": 12345678
                        }
                    ], None
        return data, err

    """
    params
        username            用户名

    returns
        time                报表对应的时间（"今日" or "本周" or "本月" or...）
        totalChargeCount    报表时间对应的所有充电桩累计充电次数
        totalChargeTime     报表时间对应的所有充电桩总计充电时间（毫秒时间戳）
        totalChargeQuantity 报表时间对应的所有充电桩总计充电量（度）
        totalChargeCost     报表时间对应的所有充电桩充电费用
        totalServiceCost    报表时间对应的所有充电桩服务费用
        totalCost           报表时间对应的所有充电桩总费用
        chargers: {
            chargerID           充电桩编号
            totalChargeCount    报表时间对应的单个充电桩累计充电次数
            totalChargeTime     报表时间对应的单个充电桩总计充电时间（毫秒时间戳）
            totalChargeQuantity 报表时间对应的单个充电桩总计充电量（度）
            totalChargeCost     报表时间对应的单个充电桩充电费用
            totalServiceCost    报表时间对应的单个充电桩服务费用
            totalCost           报表时间对应的单个充电桩总费用
        }
    """

    def adminGetTable(self, params):
        data, err = {
                        "time": "今日",
                        "totalChargeCount": 30,
                        "totalChargeTime": 99999999,
                        "totalChargeQuantity": 320,
                        "totalChargeCost": 1100,
                        "totalServiceCost": 600,
                        "totalCost": 1700,
                        "chargers": [{
                            "chargerID": 1,
                            "totalChargeCount": 10,
                            "totalChargeTime": 12345678,
                            "totalChargeQuantity": 120,
                            "totalChargeCost": 100,
                            "totalServiceCost": 100,
                            "totalCost": 200
                        }, {
                            "chargerID": 2,
                            "totalChargeCount": 20,
                            "totalChargeTime": 87654321,
                            "totalChargeQuantity": 200,
                            "totalChargeCost": 1000,
                            "totalServiceCost": 500,
                            "totalCost": 1500
                        }, ]
                    }, None
        return data, err
