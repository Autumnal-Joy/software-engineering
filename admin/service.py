import sys

sys.path.append("..")
import json
import time
import threading
from structure import Order
from structure import WaitArea
from structure import ChargeBoot

FPN = 0  # FastCharingPileNum(FPN)        快充电桩数
TPN = 0  # TrickleChargingPileNum(TPN)    慢充电桩数
N = 0  # WaitingAreaSize(N)           等候区车位容量
M = 0  # ChargingQueueLen(M)          充电桩排队队列长度


class Service:
    def __init__(self, db ,pd):
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

    def debug(self):
        print("userord:",self.usr2ord)
        print("userbill:", self.usr2bill)
        print("waitqueue:", self.waitqueue)
        print("FastReadyQueue:", self.FastReadyQueue)
        print("SlowReadyQueue:", self.SlowReadyQueue)
        print("FastBoot:", self.FastBoot)
        print("SlowBoot:", self.SlowBoot)
        print("Schedule:", self.Schedule)
        return 1



    """
    params
        username            用户名
        password            密码

    returns
        status              用于没有实际数据返回时，表示操作是否成功

    """

    def adminLogin(self, username: str, password: str):
        # data, err = None, "管理员用户不存在"
        data, err = {"status": False}, None
        table = self.db.Query("AdminInfo", username)
        if not table:  # 字典为空
            err = "用户不存在"
        elif table["password"] != password:
            err = "用户名或密码错误"
        else:
            data = {"status": True}
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

    def adminGetChargers(self, username: str):
        data, err = None, None
        data = self.db.Query("ChargerInfo", None)
        if not data:  # 列表为空
            err = "查询不到充电桩"
        return data, err

    """
    params
        username            用户名
        chargerID           充电桩编号
        turn                启动或关闭充电桩（"on":True , "off":False）

    returns
        status              用于没有实际数据返回时，表示操作是否成功

    """

    def adminTurnCharger(self, username: str, chargerID, turn):
        data, err = {"status": False}, None
        table = self.db.Query("ChargerInfo", None)
        if len(table) < chargerID:
            err = "编号不存在，编号超过充电桩总数"
        else:
            newEntry = table[chargerID - 1]
            if turn == "on":
                newEntry["working"] = True
            else:
                newEntry["working"] = False
            status = self.db.Update("ChargerInfo", chargerID, newEntry)
            if status:
                data = {"status": True}
            else:
                err = "更新数据库失败"
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

    # 临时用
    def adminGetUsersInterface(self, chargerID:int):
        if chargerID == 1:
            return [{
                "username": "walker",
                "chargeQuantity": 24,
                "waitingTime": 12345678
            }, {
                "username": "AutJ",
                "chargeQuantity": 32,
                "waitingTime": 23456781
            }]
        else:
            return None

    def adminGetUsers(self, username, chargerID):
        data, err = None, None
        id = int(chargerID)

        data = self.adminGetUsersInterface(id)
        if not data:
            err = "充电桩编号不存在"
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

    def adminGetTable(self, username: str):
        data, err = None, None
        data = self.db.Query("Report", None)
        if not data:
            err = "查询报表失败"
        return data, err
