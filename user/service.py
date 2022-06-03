import json,time
import sys
sys.path.append("..")
from structure import  Order
from structure import WaitArea
from structure import ChargeBoot

FPN = 0 # FastCharingPileNum(FPN)        快充电桩数
TPN = 0 # TrickleChargingPileNum(TPN)    慢充电桩数
N = 0 # WaitingAreaSize(N)           等候区车位容量
M = 0 # ChargingQueueLen(M)          充电桩排队队列长度

class Service:
    def __init__(self, db):
        self.db = db
        global N,M,FPN,TPN
        with open("./config.json", encoding='utf-8') as f:
            data = json.load(f)
        N,M,FPN,TPN = data['WSZ'],data['CQL'],data['FPN'],data['TPN']
        self.usr2ord = {}  #username->Order
        self.usr2bill = {} #username->[Bill]
        self.N = N         #WaitQueueLen
        self.waitqueue = WaitArea(self.N)
        self.FastReadyQueue = [i for i in range(0,FPN)]
        self.SlowReadyQueue = [i for i in range(0,TPN)]
        self.FastBoot = [ChargeBoot(M,'F',30,i,self.FastReadyQueue,self.Schedule,self.usr2bill,self.usr2ord) for i in range(0,FPN)]
        self.SlowBoot = [ChargeBoot(M,'T',10,i,self.SlowReadyQueue,self.Schedule,self.usr2bill,self.usr2ord) for i in range(0,TPN)]
    """ 
    params
        username            用户名
        password            密码
        
    returns
        status              用于没有实际数据返回时，表示操作是否成功
    """

    def userLogin(self, username:str,password:str):
        # data, err = None, "用户不存在"
        data, err = {
                        "status": True
                    }, None
        table = self.db.Query("UserInfo", username)
        if "password" not in table:
            data,err = None,"用户不存在"
        elif (table["password"] != password):
            data,err = None,"用户名或密码错误"
        return data, err

    """ 
    params
        username            用户名
        password            密码
        
    returns
        status              用于没有实际数据返回时，表示操作是否成功
    """

    def userRegister(self, username:str,password:str):
        # data, err = None, "用户名重复"
        data, err = {
                        "status": True
                    }, None
        table = self.db.Query("UserInfo", username)
        if "password" in table:
            data,err = None,"用户名重复"
            return data, err
        table = {
                    'username': username,
                    'password': password
        }
        if (self.db.Insert("UserInfo", username, table) == False):
            data,err = None,"数据库载入错误"
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
            data,err = None,"用户已经预约过"
            return data, err
        new_ord = Order(username, chargeType, chargeQuantity)
        res = self.waitqueue.addord(new_ord)
        if (res == False):
            data,err = None,"等待区满，预约被拒绝"
        else:
            self.usr2ord[username] = new_ord
            self.Schedule()
        return data, err

    """ 
    params
        username            用户名
    
    returns
        chargeType          充电类别（"fast" or "slow"）
        chargeQuantity      充电量（单位：度）
    """

    def userGetOrder(self, username:str):
        # data, err = None, "用户尚未预约"
        data, err = {
                        "chargeType": "fast",
                        "chargeQuantity": 12
                    }, None
        if username not in self.usr2ord:
            data,err = None,"用户尚未预约"
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

    def userGetLineNo(self, username:str):
        # data, err = None, "用户尚未预约"
        data, err = {
                        "lineNo": "T10"
                    }, None
        if username not in self.usr2ord:
            data,err = None,"用户尚未预约"
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

    def userGetRank(self, username:str):
        # data, err = None, "用户尚未预约"
        data, err = {
                        "rank": 10,
                        "endingTime": 1654275723231
                    }, None
        if username not in self.usr2ord:
            data,err = None,"用户尚未预约"
            return data,err
        ans = self.waitqueue.getCarBeforenum(username)
        if (ans == -1):
            data["rank"] = 0
            data["endingTime"] = self.usr2ord[username].aimed_end_time
        else:
            data["rank"] = ans + 1
            data["endingTime"] = None
        return data, err

    """ 
    params
        username            用户名
        chargeQuantity      充电量（单位：度）
        chargeType          充电类别（取值："fast" or "slow"）
        
    returns
        status              用于没有实际数据返回时，表示操作是否成功
    """

    def userSendChargeType(self, username:str,chargeQuantity:int,chargeType:str):
        # data, err = None, "用户尚未预约"
        data, err = {
                        "status": True
                    }, None
        if (username not in self.usr2ord):
            data,err = None,"用户尚未预约"
        elif (self.usr2ord[username].status != 'Wait'):
            data,err = None,"订单不在等候区,请求被拒绝"
        else:
            self.waitqueue.delord(username)
            d,e = self.userSendOrder(username,chargeType,chargeQuantity)
            if d is None:
                return d,e
        return data, err

    """ 
    params
        username            用户名
        chargeQuantity      充电量（单位：度）
        
    returns
        status              用于没有实际数据返回时，表示操作是否成功
    """

    def userSendChargeQuantity(self, username:str,chargeQuantity:int):
        # data, err = None, "用户尚未预约"
        data, err = {
                        "status": True
                    }, None
        if username not in self.usr2ord:
            data,err = None,"用户尚未预约"
        elif (self.usr2ord[username].status != 'Wait'):
            data,err = "用户不在等候区,请求被拒绝"
        else:
            self.waitqueue.change_quantity(username,chargeQuantity)
        return data, err

    """ 
    params
        username            用户名
        
    returns
        status              用于没有实际数据返回时，表示操作是否成功
    """

    def userSendCancelCharge(self, username:str):
        # data, err = None, "用户尚未预约"
        data, err = {
                        "status": True
                    }, None
        if username not in self.usr2ord:
            data,err = None,"用户尚未预约"
        elif (self.usr2ord[username].status[0] == 'S'):
            if (self.usr2ord[username].status[2] == 'F'):
                rank = int(self.usr2ord[username].status[3:])
                # 快充的删除
                return self.FastBoot[rank].delord(username)
            else:
                rank = int(self.usr2ord[username].status[3:])
                # 慢充的删除
                return self.SlowBoot[rank].delord(username)
        else:
            return self.waitqueue.delord(username)
        return data, err

    """ 
    params
        username            用户名
        
    returns
        billID              详单编号
        billTime            详单生成时间（毫秒时间戳）
        chargeQuantity      充电量
    """

    def userGetBillsList(self, username:str):
        # data, err = None, "未知错误"
        data, err = [
                        {"billID": 1, "billTime": 1654275723231, "chargeQuantity": 24},
                        {"billID": 2, "billTime": 1654276723231, "chargeQuantity": 12}
                    ], None
        if username not in self.usr2bill:
            data,err = [],None
        for x in self.usr2bill[username]:
            data.append({"billID":x.BillID,"billTime":x.end,"chargeQuantity":x.real_quantity})
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

    def userGetBill(self, username:str,billID:int):
        # data, err = None, "未知错误"
        data, err = {}, None
        if username not in self.usr2bill:
            data,err = {},None
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
                    "cost": x.chargecost + x.servecost
                }
                break
        else:
            data,err = None,"该用户没有该billID的账单"
        return data, err
    #内部调度函数Schedule
    def Schedule(self):
        #print("准备调度")
        #print(self.waitqueue.usr2num)
        #print("fast_ready",self.FastReadyQueue)
        #print("slow_ready",self.SlowReadyQueue)
        while(self.waitqueue.haswaitF() and len(self.FastReadyQueue)):
            order = self.waitqueue.fetch_first_fast_order()
            #找到waittotal最小的FastBoot
            if order is None:
                break #为了互斥锁
            sel = 0
            #得到所有有空位同一时刻的FastBoot的实时totalwait
            Totalwait = []
            #记录最开始的time
            t1 = time.time()
            for i in range(0,len(self.FastReadyQueue)):
                Totalwait.append(
                    max(0,self.FastBoot[self.FastReadyQueue[i]].CalcRealWaittime() + time.time() - t1))
            print(Totalwait)
            for i in range(1,len(self.FastReadyQueue)):
                if(Totalwait[i] < Totalwait[sel]):
                    sel = i
            order.status = "S_F" + str(self.FastReadyQueue[sel])
            order.chargeID = 'F' + str(self.FastReadyQueue[sel])
            print("调度成功，将订单(username:{},chargetype:{},chargeQuantity:{})加入了充电桩F{}的服务队列...".format(order.username,order.chargeType,order.chargeQuantity,self.FastReadyQueue[sel]))
            self.FastBoot[self.FastReadyQueue[sel]].add(order)
            #检测如果充电桩满了就删除
            if(self.FastBoot[self.FastReadyQueue[sel]].isFull()):
                del self.FastReadyQueue[sel]
        while(self.waitqueue.haswaitS() and len(self.SlowReadyQueue)):
            order = self.waitqueue.fetch_first_slow_order()
            if order is None:
                break #为了互斥锁
            # 找到waittotal最小的FastBoot
            sel = 0
            # 得到所有有空位同一时刻的SlowBoot的实时totalwait
            Totalwait = []
            # 记录最开始的time
            t1 = time.time()
            for i in range(0, len(self.SlowReadyQueue)):
                Totalwait.append(
                    max(0, self.SlowBoot[self.SlowReadyQueue[i]].CalcRealWaittime() + time.time() - t1))
            for i in range(0,len(self.SlowReadyQueue)):
                if(Totalwait[i] < Totalwait[sel]):
                    sel = i
            order.status = "T" + str(self.SlowReadyQueue[sel])
            order.chargeID = 'T' + str(self.SlowReadyQueue[sel])
            print("调度成功，将订单(username:{},chargetype:{},chargeQuantity:{})加入了充电桩T{}的服务队列...".format(order.username,order.chargeType,order.chargeQuantity,self.SlowReadyQueue[sel]))
            self.SlowBoot[self.SlowReadyQueue[sel]].add(order)
            if (self.SlowBoot[self.SlowReadyQueue[sel]].isFull()):
                del self.SlowReadyQueue[sel]
