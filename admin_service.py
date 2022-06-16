import logging
import sys
from structure import Gettime
from structure import intTodatetime
from structure import Bill

sys.path.append("")

FPN = 0  # FastCharingPileNum(FPN)        快充电桩数
TPN = 0  # TrickleChargingPileNum(TPN)    慢充电桩数
N = 0  # WaitingAreaSize(N)           等候区车位容量
M = 0  # ChargingQueueLen(M)          充电桩排队队列长度

'''
log.info("message")
'''

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

    def debug(self):
        print("userord:", self.usr2ord)
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
        if data["status"] == True:
            log.info("{}:管理员".format(intTodatetime(int(1000 * Gettime()))) + username + ": 登录成功")
        else:
            log.info("{}:登录失败，".format(intTodatetime(int(1000 * Gettime()))) + err)
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
        data, err = [], None
        BootList = []
        BootList.extend(self.FastBoot)
        BootList.extend(self.SlowBoot)
        # print("*******F", len(self.FastBoot))
        # print("*******T", len(self.SlowBoot))
        # print("*******b", len(BootList))
        for boot in BootList:
            table = self.db.Query("ChargerBillList", boot.name)
            # print(table)
            totalChargeCount = 0
            totalChargeTime = 0
            totalChargeQuantity = 0
            for i in table:
                # print(i)
                bill = Bill(table[i])
                # print(bill)
                totalChargeCount = totalChargeCount + 1
                totalChargeTime = totalChargeTime + (bill.end - bill.start)
                # print(bill.end - bill.start)
                totalChargeQuantity = totalChargeQuantity + bill.real_quantity
                # print("**********totalChargestart", bill.start)
                # print("**********totalChargestart", bill.end)
            # print("**********totalChargeTime",totalChargeTime)
            Info = {"chargerID": boot.name, "working": boot.working, "totalChargeCount": totalChargeCount,
                    "totalChargeTime": totalChargeTime, "totalChargeQuantity": totalChargeQuantity}
            data.append(Info)
        log.info("{}:管理员".format(intTodatetime(int(1000 * Gettime()))) + username + ": 查询充电桩成功")
        return data, err

    """
    params
        username            用户名
        chargerID           充电桩编号
        turn                启动或关闭充电桩（"on" , "off"）

    returns
        status              用于没有实际数据返回时，表示操作是否成功

    """

    def adminTurnCharger(self, username: str, chargerID, turn):
        # print("#########turn",turn)
        # print("#########chargerID",int(chargerID[1:]))
        # print("#########test", self.FastBoot[int(chargerID[1:])])
        data, err = {"status": True}, None
        # print("****test")
        if chargerID[0] == 'T':
            if turn == "off":
                orderList = self.SlowBoot[int(chargerID[1:]) - 1].shut()
                for order in orderList:
                    # print(order.username)
                    self.waitqueue.emegency_add_s(order)
                # print("******workingstate", self.SlowBoot[int(chargerID[1:]) - 1].working)
            else:
                orderList = []
                for chargerBoot in self.SlowBoot:
                    orderList.extend(chargerBoot.pop_order_in_wait())
                orderList.sort(key=lambda x: int(x.serialnum[1:]), reverse=False)
                for order in orderList:
                    self.waitqueue.emegency_add_s(order)
                orderList = []
                for chargerBoot in self.FastBoot:
                    orderList.extend(chargerBoot.pop_order_in_wait())
                orderList.sort(key=lambda x: int(x.serialnum[1:]), reverse=False)
                for order in orderList:
                    self.waitqueue.emegency_add_f(order)
                self.SlowBoot[int(chargerID[1:]) - 1].start()
        else:
            if turn == "off":

                orderList = self.FastBoot[int(chargerID[1:]) - 1].shut()
                # print("****test1")
                # print(orderList)
                for order in orderList:
                    # print(order.username)
                    self.waitqueue.emegency_add_f(order)
            else:
                orderList = []
                for chargerBoot in self.SlowBoot:
                    orderList.extend(chargerBoot.pop_order_in_wait())
                orderList.sort(key=lambda x: int(x.serialnum[1:]), reverse=False)
                for order in orderList:
                    self.waitqueue.emegency_add_s(order)
                orderList = []
                for chargerBoot in self.FastBoot:
                    orderList.extend(chargerBoot.pop_order_in_wait())
                orderList.sort(key=lambda x: int(x.serialnum[1:]), reverse=False)
                for order in orderList:
                    self.waitqueue.emegency_add_f(order)
                self.FastBoot[int(chargerID[1:]) - 1].start()
        self.Schedule()
        if turn == 'off':
            logtxt = ": 关闭"
        else:
            logtxt = ": 打开"
        logtxt = logtxt + "充电桩" + chargerID
        log.info("{}:管理员".format(intTodatetime(int(1000 * Gettime()))) + username + logtxt)
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
    def adminGetUsersInterface(self, chargerID: int):
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
        data, err = [], None
        if chargerID[0] == 'T':
            boot = self.SlowBoot[int(chargerID[1:]) - 1]
        else:
            boot = self.FastBoot[int(chargerID[1:]) - 1]
        table = boot.get_all_ord_now()
        for ord in table:
            # ord.show()
            info = {}
            info["username"] = ord.username
            info["chargeQuantity"] = ord.chargeQuantity
            now = Gettime()
            begin = ord.createtime
            info["waitingTime"] = (now - begin) * 1000
            data.append(info)
            # print("******data", info)
            # print("***now", now)
            # print("***begin", begin)
            # print("waittimg",(now - begin) / 3600)
        # print("*******table", table)
        # print("******data",data)
        log.info("{}:管理员".format(intTodatetime(int(1000 * Gettime()))) + username + ": 查询充电桩" + chargerID + "服务用户成功")
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

    def tableAdd(self, table: dict, add: dict):
        table["totalChargeCount"] = table["totalChargeCount"] + 1
        table["totalChargeTime"] = table["totalChargeTime"] + add["ChargeTime"]
        table["totalChargeQuantity"] = table["totalChargeQuantity"] + add["ChargeQuantity"]
        table["totalChargeCost"] = table["totalChargeCost"] + add["ChargeCost"]
        table["totalServiceCost"] = table["totalServiceCost"] + add["ServiceCost"]
        table["totalCost"] = table["totalServiceCost"] + table["totalChargeCost"]
        return table

    def adminGetTable(self, username: str):
        # print("********now", 1)
        data, err = [], None
        BootList = []
        BootList.extend(self.FastBoot)
        BootList.extend(self.SlowBoot)

        billday = {"time": "今日", "totalChargeCount": 0, "totalChargeTime": 0, "totalChargeQuantity": 0,
                   "totalChargeCost": 0, "totalServiceCost": 0, "totalCost": 0, "chargers": []}
        billweek = {"time": "本周", "totalChargeCount": 0, "totalChargeTime": 0, "totalChargeQuantity": 0,
                    "totalChargeCost": 0, "totalServiceCost": 0, "totalCost": 0, "chargers": []}
        billmonth = {"time": "本月", "totalChargeCount": 0, "totalChargeTime": 0, "totalChargeQuantity": 0,
                     "totalChargeCost": 0, "totalServiceCost": 0, "totalCost": 0, "chargers": []}
        billall = {"time": "总共", "totalChargeCount": 0, "totalChargeTime": 0, "totalChargeQuantity": 0,
                   "totalChargeCost": 0, "totalServiceCost": 0, "totalCost": 0, "chargers": []}
        bootbilltable = {}
        now = Gettime()

        for boot in BootList:
            table = self.db.Query("ChargerBillList", boot.name)
            bootbilltable[boot.name] = {
                "day": {"chargerID": boot.name, "totalChargeCount": 0, "totalChargeTime": 0, "totalChargeQuantity": 0,
                        "totalChargeCost": 0, "totalServiceCost": 0, "totalCost": 0},
                "week": {"chargerID": boot.name, "totalChargeCount": 0, "totalChargeTime": 0, "totalChargeQuantity": 0,
                         "totalChargeCost": 0, "totalServiceCost": 0, "totalCost": 0},
                "month": {"chargerID": boot.name, "totalChargeCount": 0, "totalChargeTime": 0, "totalChargeQuantity": 0,
                          "totalChargeCost": 0, "totalServiceCost": 0, "totalCost": 0},
                "all": {"chargerID": boot.name, "totalChargeCount": 0, "totalChargeTime": 0, "totalChargeQuantity": 0,
                        "totalChargeCost": 0, "totalServiceCost": 0, "totalCost": 0}
            }
            for i in table:
                bill = Bill(table[i])
                # bill.Show()  # 需修改，/ 3600
                # print(bill.end - bill.start)
                addDict = {"ChargeTime": round((bill.end - bill.start) / 3600000, 3),
                           "ChargeQuantity": round(bill.real_quantity, 3),
                           "ChargeCost": round(bill.chargecost, 3), "ServiceCost": round(bill.servecost, 3)
                           }
                passtime = now - bill.billTime / 1000
                if passtime < 86400:
                    billday = self.tableAdd(billday, addDict)
                    bootbilltable[boot.name]["day"] = self.tableAdd(bootbilltable[boot.name]["day"], addDict)
                if passtime < 604800:
                    billweek = self.tableAdd(billweek, addDict)
                    bootbilltable[boot.name]["week"] = self.tableAdd(bootbilltable[boot.name]["week"], addDict)
                if passtime < 2592000:
                    billmonth = self.tableAdd(billmonth, addDict)
                    bootbilltable[boot.name]["month"] = self.tableAdd(bootbilltable[boot.name]["month"], addDict)
                billall = self.tableAdd(billall, addDict)
                bootbilltable[boot.name]["all"] = self.tableAdd(bootbilltable[boot.name]["all"], addDict)

                # print("**********totalChargestart", bill.start)
                # print("**********totalChargestart", bill.end)
            # print("**********totalChargeTime",totalChargeTime)
        for boot in BootList:
            billday["chargers"].append(bootbilltable[boot.name]["day"])
            billweek["chargers"].append(bootbilltable[boot.name]["week"])
            billmonth["chargers"].append(bootbilltable[boot.name]["month"])
            billall["chargers"].append(bootbilltable[boot.name]["all"])

        # print(billday)
        # print(billweek)
        # print(billmonth)
        # print(billall)

        data = [billday, billweek, billmonth, billall]
        log.info("{}:管理员".format(intTodatetime(int(1000 * Gettime()))) + username + ": 查看报表成功")
        return data, err
