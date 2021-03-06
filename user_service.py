import logging
from structure import Gettime
from structure import intTodatetime
from structure import Order

# FastChargingPileNum(FPN)        快充电桩数
# TrickleChargingPileNum(TPN)    慢充电桩数
# WaitingAreaSize(N)           等候区车位容量
# ChargingQueueLen(M)          充电桩排队队列长度

log = logging.getLogger('app')


class Service:
    def __init__(self, db, pd):
        self.db = db
        self.N, self.M, self.FPN, self.TPN = pd.N, pd.M, pd.FPN, pd.TPN
        self.usr2ord = pd.usr2ord  # username->Order
        self.usr2bill = pd.usr2bill  # username->[Bill]
        self.mutex_wait_lock = pd.mutex_wait_lock
        self.waitqueue = pd.waitqueue
        self.fast_ready_lock = pd.fast_ready_lock
        self.slow_ready_lock = pd.slow_ready_lock
        self.FastReadyQueue = pd.FastReadyQueue
        self.SlowReadyQueue = pd.SlowReadyQueue
        self.FastBoot = pd.FastBoot
        self.SlowBoot = pd.SlowBoot
        self.Fast_Speed = pd.Fast_Speed
        self.Slow_Speed = pd.Slow_Speed
        self.Schedule = pd.Schedule

    """ 
    params
        username            用户名
        password            密码
        
    returns
        status              用于没有实际数据返回时，表示操作是否成功
    """

    def userLogin(self, username: str, password: str):
        # data, err = None, "用户不存在"
        data, err = None, None
        table = self.db.Query("UserInfo", username)
        if "password" not in table:
            err = "用户不存在"
        elif table["password"] != password:
            err = "用户名或密码错误"
        else:
            data = {"status": True}
        if err is None:
            log.info("{}:用户{}登入成功".format(intTodatetime(int(1000*Gettime())),username))
        else:
            log.info("{}:用户{}登入失败, {}".format(intTodatetime(int(1000*Gettime())),username, err))
        return data, err

    """ 
    params
        username            用户名
        password            密码
        
    returns
        status              用于没有实际数据返回时，表示操作是否成功
    """

    def userRegister(self, username: str, password: str):
        # data, err = None, "用户名重复"
        data, err = {
                        "status": True
                    }, None
        table = self.db.Query("UserInfo", username)
        if "password" in table:
            data, err = None, "用户名重复"
        else:
            table = {
                'username': username,
                'password': password
            }
            if self.db.Insert("UserInfo", username, table) is False:
                data, err = None, "数据库载入错误"
        if err is None:
            log.info("{}:用户{}注册成功".format(intTodatetime(int(1000*Gettime())),username))
        else:
            log.info("{}:用户{}注册失败, {}".format(intTodatetime(int(1000*Gettime())),username, err))
        return data, err

    """ 
    params
        username            用户名
        chargeQuantity      充电量（单位：度）
        chargeType          充电类别（取值："fast" or "slow"）
        
    returns
        status              用于没有实际数据返回时，表示操作是否成功
    """

    def userSendOrder(self, username: str, chargeType: str, chargeQuantity: int):
        # data, err = None, "用户已经预约过"
        data, err = {
                        "status": True
                    }, None
        if username in self.usr2ord:
            data, err = None, "用户已经预约过"
        else:
            new_ord = Order(username, chargeType, chargeQuantity)
            res = self.waitqueue.addord(new_ord)
            if res is False:
                data, err = None, "等待区满，预约被拒绝"
            else:
                self.usr2ord[username] = new_ord
                self.Schedule()
        if err is None:
            log.info("{}:用户{}预约成功".format(intTodatetime(int(1000*Gettime())),username))
        else:
            log.info("{}:用户{}预约失败, {}".format(intTodatetime(int(1000*Gettime())),username, err))
        return data, err

    """ 
    params
        username            用户名
    
    returns
        chargeType          充电类别（"fast" or "slow"）
        chargeQuantity      充电量（单位：度）
    """

    def userGetOrder(self, username: str):
        # data, err = None, "用户尚未预约"
        data, err = {}, None
        if username not in self.usr2ord:
            data, err = None, "用户尚未预约"
        else:
            data["chargeType"] = self.usr2ord[username].chargeType
            data["chargeQuantity"] = self.usr2ord[username].chargeQuantity
        return data, err

    """ 
    params
        username            用户名
    
    return
        lineNo              预约排号，由字母"F"、"T"后跟随一个数
    """

    def userGetLineNo(self, username: str):
        # data, err = None, "用户尚未预约"
        data, err = {}, None
        if username not in self.usr2ord:
            data, err = None, "用户尚未预约"
        else:
            data["lineNo"] = self.usr2ord[username].serialnum
        return data, err

    """ 
    params
        username            用户名

    return
        rank                正整数表示等待区前方等候者的熟练，0表示正在充电区
        endingTime          预计完成充电时间（毫秒时间戳）
    """

    def userGetRank(self, username: str):
        # data, err = None, "用户尚未预约"
        data, err = {}, None
        if username not in self.usr2ord:
            data, err = None, "用户尚未预约"
        else:
            ans = self.waitqueue.getCarBeforenum(username)
            if ans == -1:
                data["rank"] = 0
                data["endingTime"] = self.usr2ord[username].aimed_end_time
            else:
                data["rank"] = ans + 1
                data["endingTime"] = -1
        return data, err

    """ 
    params
        username            用户名
        chargeQuantity      充电量（单位：度）
        chargeType          充电类别（取值："fast" or "slow"）
        
    returns
        status              用于没有实际数据返回时，表示操作是否成功
    """

    def userSendChargeType(self, username: str, chargeQuantity: int, chargeType: str):
        # data, err = None, "用户尚未预约"
        data, err = {
                        "status": True
                    }, None
        if username not in self.usr2ord:
            data, err = None, "用户尚未预约"
        elif self.usr2ord[username].status != 'Wait':
            data, err = None, "订单不在等候区,请求被拒绝"
        else:
            self.waitqueue.delord(username)
            del self.usr2ord[username]
            data, err = self.userSendOrder(username, chargeType, chargeQuantity)
        if err is None:
            log.info("{}:用户{}修改充电方式->({}, {}, {})".format(intTodatetime(int(1000*Gettime())),username, username, chargeType, chargeQuantity))
        else:
            log.info("{}:用户{}修改失败,err = {}".format(intTodatetime(int(1000*Gettime())),username,err))
        return data, err

    """ 
    params
        username            用户名
        chargeQuantity      充电量（单位：度）
        
    returns
        status              用于没有实际数据返回时，表示操作是否成功
    """

    def userSendChargeQuantity(self, username: str, chargeQuantity: int):
        # data, err = None, "用户尚未预约"
        data, err = {
                        "status": True
                    }, None
        if username not in self.usr2ord:
            data, err = None, "用户尚未预约"
        elif self.usr2ord[username].status != 'Wait':
            data, err = None, "用户不在等候区,请求被拒绝"
        else:
            self.waitqueue.change_quantity(username, chargeQuantity)
        if err is None:
            log.info("{}:用户{}修改充电量->({}, {})".format(intTodatetime(int(1000*Gettime())),username, username,
                                              self.usr2ord[username].chargeQuantity))
        else:
            log.info("{}:用户{}修改充电量失败,err = {}".format(intTodatetime(int(1000*Gettime())),username,err))
        return data, err

    """ 
    params
        username            用户名
        
    returns
        status              用于没有实际数据返回时，表示操作是否成功
    """

    def userSendCancelCharge(self, username: str):
        # data, err = None, "用户尚未预约"
        data, err = {
                        "status": True
                    }, None
        if username not in self.usr2ord:
            data, err = None, "用户尚未预约"
        elif self.usr2ord[username].status[0] == 'S':
            if self.usr2ord[username].status[2] == 'F':
                rank = int(self.usr2ord[username].status[3:])
                # 快充的删除
                if self.FastBoot[rank].delord(username) is False:
                    data, err = None, "订单已结束"
            else:
                rank = int(self.usr2ord[username].status[3:])
                # 慢充的删除
                if self.SlowBoot[rank].delord(username) is False:
                    data, err = None, "订单已结束"
        else:
            if self.waitqueue.delord(username) is False:  # 订单刚刚调度到服务队列去
                return self.userSendCancelCharge(username)
            else:
                del self.usr2ord[username]
        if err is None:
            log.info("{}:用户{}取消了订单".format(intTodatetime(int(1000*Gettime())),username))
            self.Schedule()
        else:
            log.info("{}:用户{}订单取消失败, {}".format(intTodatetime(int(1000*Gettime())),username, err))
        return data, err

    """ 
    params
        username            用户名
        
    returns
        billID              详单编号
        billTime            详单生成时间（毫秒时间戳）
        chargeQuantity      充电量
    """

    def userGetBillsList(self, username: str):
        # data, err = None, "未知错误"
        data, err = [], None
        if username in self.usr2bill:
            for x in self.usr2bill[username]:
                data.append({"billID": x.BillID, "billTime": x.end, "chargeQuantity": x.real_quantity})
        return data, err

    """ 
    params
        username            用户名
        billID              账单编号
        
    returns
        billID              详单编号
        billTime            详单生成时间（毫秒时间戳）
        chargeQuantity      用户充电量（度）
        chargeTime          用户充电时长（毫秒时间戳）
        startTime           用户开始充电时间（毫秒时间戳）
        endTime             用户结束充电时间（毫秒时间戳）
        chargeCost          充电费用
        serviceCost         服务费用
        cost                总费用
    """

    def userGetBill(self, username: str, billID: int):
        # data, err = None, "未知错误"
        data, err = {}, None
        if username not in self.usr2bill:
            data, err = {}, None
        for x in self.usr2bill[username]:
            if x.BillID == billID:
                data = {
                    "billID": billID,
                    "billTime": x.billTime,
                    "chargerID": x.chargeID,
                    "chargeQuantity": x.real_quantity,
                    "chargeTime": x.end - x.start,
                    "startTime": x.start,
                    "endTime": x.end,
                    "chargeCost": x.chargecost,
                    "serviceCost": x.servecost,
                    "cost": x.totalcost
                }
                break
        else:
            data, err = None, "该用户没有该billID的账单"
        return data, err
