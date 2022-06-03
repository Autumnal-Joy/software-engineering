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

    def userLogin(self, params):
        # data, err = None, "用户不存在"
        data, err = {
                        "status": True
                    }, None
        return data, err

    """ 
    params
        username            用户名
        password            密码
        
    returns
        status              用于没有实际数据返回时，表示操作是否成功
    """

    def userRegister(self, params):
        # data, err = None, "用户名重复"
        data, err = {
                        "status": True
                    }, None
        return data, err

    """ 
    params
        username            用户名
        chargeQuantity      充电量（单位：度）
        chargeType          充电类别（取值："fast" or "slow"）
        
    returns
        status              用于没有实际数据返回时，表示操作是否成功
    """

    def userSendOrder(self, params):
        # data, err = None, "用户已经预约过"
        data, err = {
                        "status": True
                    }, None
        return data, err

    """ 
    params
        username            用户名
    
    returns
        chargeType          充电类别（"fast" or "slow"）
        chargeQuantity      充电量（单位：度）
    """

    def userGetOrder(self, params):
        # data, err = None, "用户尚未预约"
        data, err = {
                        "chargeType": "fast",
                        "chargeQuantity": 12
                    }, None
        return data, err

    """ 
    params
        username            用户名
    
    return
        lineNo              预约排号，由字母"F"、"T"后跟随一个数
    """

    def userGetLineNo(self, params):
        # data, err = None, "用户尚未预约"
        data, err = {
                        "lineNo": "T10"
                    }, None
        return data, err

    """ 
    params
        username            用户名
    
    return
        rank                正整数表示等待区前方等候者的熟练，0表示正在充电区
        endingTime          预计完成充电时间（毫秒时间戳）
    """

    def userGetRank(self, params):
        # data, err = None, "用户尚未预约"
        data, err = {
                        "rank": 10,
                        "endingTime": 1654275723231
                    }, None
        return data, err

    """ 
    params
        username            用户名
        chargeQuantity      充电量（单位：度）
        chargeType          充电类别（取值："fast" or "slow"）
        
    returns
        status              用于没有实际数据返回时，表示操作是否成功
    """

    def userSendChargeType(self, params):
        # data, err = None, "用户尚未预约"
        data, err = {
                        "status": True
                    }, None
        return data, err

    """ 
    params
        username            用户名
        chargeQuantity      充电量（单位：度）
        
    returns
        status              用于没有实际数据返回时，表示操作是否成功
    """

    def userSendChargeQuantity(self, param):
        # data, err = None, "用户尚未预约"
        data, err = {
                        "status": True
                    }, None
        return data, err

    """ 
    params
        username            用户名
        
    returns
        status              用于没有实际数据返回时，表示操作是否成功
    """

    def userSendCancelCharge(self, param):
        # data, err = None, "用户尚未预约"
        data, err = {
                        "status": True
                    }, None
        return data, err

    """ 
    params
        username            用户名
        
    returns
        billID              详单编号
        billTime            详单生成时间（毫秒时间戳）
        chargeQuantity      充电量
    """

    def userGetBillsList(self, param):
        # data, err = None, "未知错误"
        data, err = [
                        {"billID": 1, "billTime": 1654275723231, "chargeQuantity": 24},
                        {"billID": 2, "billTime": 1654276723231, "chargeQuantity": 12}
                    ], None
        return data, err

    """ 
    params
        username            用户名
        billID              账单编号
        
    returns
        billID              详单编号
        billTime            详单生成时间（毫秒时间戳）
        chargeQuantity      用户充电量
        chargeTime          用户充电时长（毫秒时间戳）
        startTime           用户开始充电时间（毫秒时间戳）
        endTime             用户结束充电时间（毫秒时间戳）
        chargeCost          充电费用
        serviceCost         服务费用
        cost                总费用
    """

    def userGetBill(self, param):
        # data, err = None, "未知错误"
        data, err = {
                        "billID": 1,
                        "billTime": 1654276723231,
                        "chargerID": 1,
                        "chargeQuantity": 30,
                        "chargeTime": 123456789,
                        "startTime": 1654275723231,
                        "endTime": 1654275723231,
                        "chargeCost": 100,
                        "serviceCost": 100,
                        "cost": 200
                    }, None
        return data, err
