import datetime
import json
import logging
import math
import threading
import time
from threading import Timer

FAST_SPEED = 0
SLOW_SPEED = 0

log = logging.getLogger('app')
log2 = logging.getLogger('state')

system_start_time_stamp = 0
system_start_time = 0
TIME_ACC = 0
# 计算时间函数Gettime()
def Gettime():
    return system_start_time_stamp + (time.time() - system_start_time) * TIME_ACC
def intTodatetime(intValue):
    intValue = int(intValue)
    if len(str(intValue)) == 10:  # 精确到秒
        timeValue = time.localtime(intValue)
        tempDate = time.strftime("%Y-%m-%d %H:%M:%S", timeValue)
        datetimeValue = datetime.datetime.strptime(tempDate, "%Y-%m-%d %H:%M:%S")
    elif 10 < len(str(intValue)) < 15:  # 精确到毫秒
        k = len(str(intValue)) - 10
        timetamp = datetime.datetime.fromtimestamp(intValue / (1 * 10 ** k))
        datetimeValue = timetamp.strftime("%Y-%m-%d %H:%M:%S.%f")
        datetimeValue = datetimeValue[:datetimeValue.find('.') + 4]
    else:
        return -1
    return datetimeValue


class Order:
    def __init__(self, username, chargeType, chargeQuantity):
        self.username = username  # 用户名
        self.chargeType = chargeType  # 充电类型
        self.chargeQuantity = chargeQuantity  # 充电量
        self.serialnum = 0  # 序列号
        # Generating Wait EF ET S_Fi S_Ti Compelete
        self.status = "Generating"  # 订单状态
        self.begin = 0
        self.end = 0
        self.aimed_end_time = 0
        self.chargeID = 0  # 充电桩编号
        self.createtime = Gettime()  # 订单生成时间


id = 1


class Bill:
    def __init__(self, order, canceled=0):
        if type(order) == Order:
            global id
            self.BillID = id
            id = id + 1
            self.chargeID = order.chargeID
            self.billTime = Gettime() * 1000
            self.username = order.username
            self.charge_type = order.chargeType
            self.aimed_quantity = order.chargeQuantity
            self.real_quantity = round((order.end - order.begin) * (
                FAST_SPEED if order.chargeType == 'F' else SLOW_SPEED) if canceled else order.chargeQuantity, 3)
            self.start_tm = intTodatetime(int(order.begin * 1000))
            self.end_tm = intTodatetime(int(order.end * 1000))
            self.start = order.begin * 1000
            self.end = order.end * 1000
            self.chargecost, self.servecost = self.Calc(FAST_SPEED if order.chargeType == 'F' else SLOW_SPEED)
            self.totalcost = round(self.chargecost + self.servecost, 2)
            self.aimed_end_time = intTodatetime(int(order.aimed_end_time))
            # self.Show()
        elif type(order) == dict:
            self.BillID = order["BillID"]
            self.chargeID = order["chargeID"]
            self.billTime = order["billTime"]
            self.username = order["username"]
            self.charge_type = order["charge_type"]
            self.aimed_quantity = order["aimed_quantity"]
            self.real_quantity = order["real_quantity"]
            self.start_tm = order["start_tm"]
            self.end_tm = order["end_tm"]
            self.start = order["start"]
            self.end = order["end"]
            self.chargecost = order["chargecost"]
            self.servecost = order["servecost"]
            self.totalcost = order["totalcost"]
            self.aimed_end_time = order["aimed_end_time"]

    # 为了存储，转换成dict
    def todict(self):
        ans = {
            "BillID": self.BillID,
            "chargeID": self.chargeID,
            "billTime": self.billTime,
            "username": self.username,
            "charge_type": self.charge_type,
            "aimed_quantity": self.aimed_quantity,
            "real_quantity": self.real_quantity,
            "start_tm": self.start_tm,
            "end_tm": self.end_tm,
            "start": self.start,
            "end": self.end,
            "chargecost": self.chargecost,
            "servecost": self.servecost,
            "totalcost": self.totalcost,
            "aimed_end_time": self.aimed_end_time
        }
        return ans

        # 计算费用

    def Calc(self, ChargeSpeed):
        # 因为速度恒定，所以只知道start_tm和end_tm可以求出
        # 峰时(1.0元/度) (10:00-15:00 18:00-21:00)
        # 平时(0.7元/度) (7:00-10:00 15:00-18:00 21:00-23:00)
        # 谷时(0.4元/度) (23:00-次日7:00)
        t1 = self.start_tm
        start = list(map(int, t1.split(' ')[0].split('-'))) + list(
            map(int, t1.split(' ')[1].split('.')[0].split(':'))) + list(map(int, [t1.split(' ')[1].split('.')[1]]))
        t1 = self.end_tm
        end = list(map(int, t1.split(' ')[0].split('-'))) + list(
            map(int, t1.split(' ')[1].split('.')[0].split(':'))) + list(map(int, [t1.split(' ')[1].split('.')[1]]))
        # [year,month,day,hour,min,sec,msec]
        # 因为是连续的,所以提前算出一天的,
        # 最多一次100度 慢充10度/小时 最多10小时 不跨过一天
        charge_cost = 0
        time_point = [0, 7, 10, 15, 18, 21, 23, 24]
        fee = [0.4, 0.7, 1.0, 0.7, 1.0, 0.7, 0.4, 0.4]
        st = 0  # 第一个大于start.hour的时间节点
        for i in range(0, len(time_point)):
            if time_point[i] > start[3]:
                st = i
                break
        ed = 0  # 最后一个小于end.hour的时间节点
        for i in range(0, len(time_point)):
            if time_point[i] > end[3]:
                ed = (i - 1) % len(time_point)
                break
        # 循环统计
        day = start[2]
        if (day != end[2] or st <= ed):
            charge_cost += ((time_point[st] * 3600 - start[3] * 3600 - start[4] * 60 - start[5] - start[6] * 0.001) % (
                    24 * 3600)) * ChargeSpeed * fee[(st - 1) % len(fee)]
            while (day != end[2] or st != ed):
                charge_cost += (((time_point[(st + 1) % len(time_point)] - time_point[st]) % 24) * 3600) * ChargeSpeed * \
                               fee[(st) % len(fee)]
                st = st + 1
                if st == len(time_point):
                    st = 0
                    day = day + 1
            charge_cost += ((end[3] * 3600 + end[4] * 60 + end[5] + end[6] * 0.001 - time_point[ed] * 3600) % (
                    24 * 3600)) * ChargeSpeed * fee[(ed) % len(fee)]
        elif (st == ed + 1):
            charge_cost += (end[3] * 3600 + end[4] * 60 + end[5] + end[6] * 0.001 - start[3] * 3600 - start[4] * 60 -
                            start[5] - start[6] * 0.001) * ChargeSpeed * fee[(ed) % len(fee)]
        else:
            log.error("Bill Calc Error")
        return round(charge_cost, 2), round(0.8 * self.real_quantity, 2)


class ChargeBoot:
    def __init__(self, M: int, type: str, speed: int, rank: int, ReadyQueue: list, ready_queue_lock, Schedule,
                 usr2bill,
                 usr2ord, time_acc, db):
        self.db = db
        self.volumn = M
        self.ServeQueue = Queue(M)
        self.timers = {}  # username->{定时器句柄的字典,starttime}
        self.totalwait = 0
        self.Charge_Speed = speed
        self.busy = False
        self.usr2bill = usr2bill
        self.ReadyQueue = ReadyQueue
        self.ready_queue_lock = ready_queue_lock
        self.type = type
        self.rank = rank
        self.Schedule = Schedule
        self.usr2ord = usr2ord
        self.name = type + str(rank + 1)
        self.working = True
        self.time_acc = time_acc
        self.lock = threading.Lock()

    def realcalc(self,bgtm,entm,nowquantity):
        # 因为速度恒定，所以只知道start_tm和end_tm可以求出
        # 峰时(1.0元/度) (10:00-15:00 18:00-21:00)
        # 平时(0.7元/度) (7:00-10:00 15:00-18:00 21:00-23:00)
        # 谷时(0.4元/度) (23:00-次日7:00)
        t1 = bgtm
        start = list(map(int, t1.split(' ')[0].split('-'))) + list(
            map(int, t1.split(' ')[1].split('.')[0].split(':'))) + list(map(int, [t1.split(' ')[1].split('.')[1]]))
        t1 = entm
        end = list(map(int, t1.split(' ')[0].split('-'))) + list(
            map(int, t1.split(' ')[1].split('.')[0].split(':'))) + list(map(int, [t1.split(' ')[1].split('.')[1]]))
        # [year,month,day,hour,min,sec,msec]
        # 因为是连续的,所以提前算出一天的,
        # 最多一次100度 慢充10度/小时 最多10小时 不跨过一天
        charge_cost = 0
        time_point = [0, 7, 10, 15, 18, 21, 23, 24]
        fee = [0.4, 0.7, 1.0, 0.7, 1.0, 0.7, 0.4, 0.4]
        st = 0  # 第一个大于start.hour的时间节点
        for i in range(0, len(time_point)):
            if time_point[i] > start[3]:
                st = i
                break
        ed = 0  # 最后一个小于end.hour的时间节点
        for i in range(0, len(time_point)):
            if time_point[i] > end[3]:
                ed = (i - 1) % len(time_point)
                break
        # 循环统计
        day = start[2]
        if (day != end[2] or st <= ed):
            charge_cost += ((time_point[st] * 3600 - start[3] * 3600 - start[4] * 60 - start[5] - start[6] * 0.001) % (
                    24 * 3600)) * self.Charge_Speed * fee[(st - 1) % len(fee)]
            while (day != end[2] or st != ed):
                charge_cost += (((time_point[(st + 1) % len(time_point)] - time_point[st]) % 24) * 3600) * self.Charge_Speed * \
                               fee[(st) % len(fee)]
                st = st + 1
                if st == len(time_point):
                    st = 0
                    day = day + 1
            charge_cost += ((end[3] * 3600 + end[4] * 60 + end[5] + end[6] * 0.001 - time_point[ed] * 3600) % (
                    24 * 3600)) * self.Charge_Speed * fee[(ed) % len(fee)]
        elif (st == ed + 1):
            charge_cost += (end[3] * 3600 + end[4] * 60 + end[5] + end[6] * 0.001 - start[3] * 3600 - start[4] * 60 -
                            start[5] - start[6] * 0.001) * self.Charge_Speed * fee[(ed) % len(fee)]
        else:
            log.error("Real Calc Error")
        return math.fabs(round(charge_cost + 0.8 * nowquantity, 2))

    def get_real_time_info(self):
        self.lock.acquire()
        res = self.ServeQueue.peek_all()
        ans = []
        if len(res) >= 1:
            nowt = Gettime()
            bgtm = intTodatetime(res[0].begin * 1000)
            edtm = intTodatetime(nowt * 1000)
            nowquantity = self.Charge_Speed * (nowt - res[0].begin)
            ans.append([res[0].username,round(nowquantity,2),self.realcalc(bgtm,edtm,nowquantity)])
            del res[0]
        for ord in res:
            ans.append([ord.username,0,0])
        self.lock.release()
        return ans

    def get_all_ord_now(self):
        self.lock.acquire()
        ans = self.ServeQueue.peek_all()
        self.lock.release()
        return ans

    #用于负载均衡时将在等待的订单重新编排
    def pop_order_in_wait(self):
        self.lock.acquire()
        if self.ServeQueue.size < 2:
            self.lock.release()
            return []
        lis = []
        tail = self.ServeQueue.head.next
        while tail is not None:
            ord = tail.order
            lis.append(ord)
            self.totalwait -= ord.chargeQuantity / self.Charge_Speed
            ptail = tail.next
            self.ServeQueue.cancel(ord.username)
            tail = ptail
        self.lock.release()
        return lis

    # 开机，均摊
    def start(self):
        self.totalwait = 0
        self.working = True
        log.info("{}:充电桩 {} 开机".format(intTodatetime(int(1000*Gettime())),self.name))

    # 关机，故障，其他均摊
    # 将在队列中的拿出去
    # 将队列中的全部拿出去
    def shut(self) -> list:
        # 从ReadyQueue中删除
        self.ready_queue_lock.acquire()
        # 设置等待时间无限大
        self.totalwait = 0x3f3f3f3f
        self.ready_queue_lock.release()
        ans = []
        if self.busy:
            head = self.ServeQueue.pop()
            self.timers[head.username][0].cancel()
            head.status = 'Partial-Compelete'
            head.end = Gettime()
            if head.username in self.usr2bill:
                bill = Bill(head, 1)
                self.usr2bill[head.username].append(bill)
                table = self.db.Query("ChargerBillList", self.name)
                table[str(int(Gettime())) + '_' + str(bill.BillID)] = bill.todict()
                self.db.Update("ChargerBillList", self.name, table)
                table = self.db.Query("UserBillList", head.username)
                table[str(int(Gettime())) + '_' + str(bill.BillID)] = bill.todict()
                self.db.Update("UserBillList", head.username, table)
            else:
                bill = Bill(head, 1)
                self.usr2bill[head.username] = [bill]
                table = self.db.Query("ChargerBillList", self.name)
                table[str(int(Gettime())) + '_' + str(bill.BillID)] = bill.todict()
                self.db.Update("ChargerBillList", self.name, table)
                table = self.db.Query("UserBillList", head.username)
                table[str(int(Gettime())) + '_' + str(bill.BillID)] = bill.todict()
                self.db.Update("UserBillList", head.username, table)
            del self.timers[head.username]
            # 结算正在进行的
            neworder = Order(head.username, head.chargeType,
                             head.chargeQuantity - (head.end - head.begin) * self.Charge_Speed)
            neworder.serialnum = head.serialnum
            self.usr2ord[head.username] = neworder
            ans.append(neworder)
        while self.ServeQueue.size:
            ans.append(self.ServeQueue.pop())
        self.working = False
        self.busy = False
        log.info("{}:充电桩 {} 关机".format(intTodatetime(int(1000*Gettime())),self.name))
        return ans

    # 添加订单 外面控制了是否满 因此这里没必要控制
    def add(self, order: Order):
        order.aimed_end_time = (
                                       Gettime() + self.CalcRealWaittime() + order.chargeQuantity / self.Charge_Speed) * 1000
        self.totalwait += order.chargeQuantity / self.Charge_Speed
        self.ServeQueue.push(order)
        log.info("{}:充电桩 {} 接到新订单: ({}, {}, {})".format(intTodatetime(int(1000*Gettime())),self.name, order.username, order.chargeType, order.chargeQuantity))
        allord = self.ServeQueue.peek_all()
        msg = "{}:充电桩 {} 现有订单: [ ".format(intTodatetime(int(1000*Gettime())),self.name)
        for singleord in allord:
            msg += '({}, {}, {}) '.format(singleord.username, singleord.chargeType, singleord.chargeQuantity)
        msg += ']'
        log.info(msg)
        if self.busy is False:
            self.consume()

    # 是否满
    def isFull(self):
        return self.ServeQueue.size >= self.volumn

    # 消费订单 每次消费结束开启
    def consume(self):
        order = self.ServeQueue.peek()
        if order is None:
            return

        cgt = order.chargeQuantity / self.Charge_Speed / self.time_acc
        self.timers[order.username] = (Timer(cgt, self.CallBack), Gettime())
        self.timers[order.username][0].start()
        order.begin = Gettime()
        # print("user {}开启了一个{}s的定时(时间加速{}倍)".format(order.username, cgt,self.time_acc))
        log.info(
            "{}:user {} 的订单 ({}, {}) 在充电桩 {} 开始执行".format(intTodatetime(int(1000*Gettime())),order.username, order.chargeType, order.chargeQuantity,
                                                       self.name))

        self.busy = True

    # 定时器结束的回调函数，包含生成账单，从服务队列中移除等
    def CallBack(self, cancel=0):
        self.lock.acquire()
        endt = Gettime()
        ord = self.ServeQueue.pop()
        ord.status = 'Compelete'
        ord.end = endt
        self.totalwait -= ord.chargeQuantity / self.Charge_Speed
        if ord.username in self.usr2bill:
            bill = Bill(ord, cancel)
            self.usr2bill[ord.username].append(bill)
            #print("1现在查的表是",self.name,ord.username)
            table = self.db.Query("ChargerBillList", self.name)
            table[str(int(Gettime())) + '_' + str(bill.BillID)] = bill.todict()
            self.db.Update("ChargerBillList", self.name, table)

            table = self.db.Query("UserBillList", ord.username)
            table[str(int(Gettime())) + '_' + str(bill.BillID)] = bill.todict()
            self.db.Update("UserBillList", ord.username, table)
        else:
            bill = Bill(ord, cancel)
            self.usr2bill[ord.username] = [bill]
            #print("2现在查的表是",self.name,ord.username)
            table = self.db.Query("ChargerBillList", self.name)
            table[str(int(Gettime())) + '_' + str(bill.BillID)] = bill.todict()
            self.db.Update("ChargerBillList", self.name, table)

            table = self.db.Query("UserBillList", ord.username)
            table[str(int(Gettime())) + '_' + str(bill.BillID)] = bill.todict()
            self.db.Update("UserBillList", ord.username, table)
        self.busy = False
        del self.timers[ord.username]
        del self.usr2ord[ord.username]
        # 继续服务下一个订单
        self.consume()
        self.lock.release()
        if cancel == 0:
            log.info(
                "{}:user {} 的订单 ({}, {}) 在充电桩 {} 执行完毕".format(intTodatetime(int(1000*Gettime())),ord.username, ord.chargeType, ord.chargeQuantity, self.name))
        else:
            log.info(
                "{}:user {} 的订单 ({}, {}) 在充电桩 {} 被终止".format(intTodatetime(int(1000*Gettime())),ord.username, ord.chargeType, ord.chargeQuantity, self.name))
        allord = self.ServeQueue.peek_all()
        msg = "{}:充电桩{}现有订单:[ ".format(intTodatetime(int(1000*Gettime())),self.name)
        for singleord in allord:
            msg += '({}, {}, {}) '.format(singleord.username, singleord.chargeType, singleord.chargeQuantity)
        msg += ']'
        log.info(msg)
        self.Schedule()

    # 删除订单
    def delord(self, username):
        head = self.ServeQueue.peek()
        if head.username == username:
            # 计算已充电时间
            self.timers[username][0].cancel()
            self.CallBack(1)
            return True
        t = self.ServeQueue.cancel(username)
        if t is True:
            ord = self.usr2ord[username]
            self.totalwait -= ord.chargeQuantity / self.Charge_Speed
            msg = '订单 ({}, {}, {}) 取消成功'.format(ord.username, ord.chargeType, ord.chargeQuantity)
            allord = self.ServeQueue.peek_all()
            msg += "{}:充电桩 {} 现有订单: [ ".format(intTodatetime(int(1000*Gettime())),self.name)
            for singleord in allord:
                msg += '({}, {}, {}) '.format(singleord.username, singleord.chargeType, singleord.chargeQuantity)
            msg += ']'
            log.info(msg)
            del self.usr2ord[username]
        return t

    # 计算实时全队等待时间
    def CalcRealWaittime(self):
        self.lock.acquire()
        if self.totalwait == 0x3f3f3f3f:
            self.lock.release()
            return 0x3f3f3f3f
        top = self.ServeQueue.peek()
        if top is None:
            self.lock.release()
            return self.totalwait
        self.lock.release()
        return self.totalwait - (Gettime() - self.timers[top.username][1])


class ListNode:
    def __init__(self, order: Order):
        self.order = order
        self.pre = None
        self.next = None


class Queue:
    def __init__(self, N: int):
        self.mutex = threading.Lock()  # 队列的锁，防止多线程同时调用多个函数造成链表损坏
        self.head = None
        self.tail = None
        self.size = 0
        self.volumn = N
        self.ord2idx = {}
        # self.mutex = threading.Lock() #互斥锁，防止定时器回调函数脏数据

    # 添加元素(从队列尾)
    def push(self, order: Order):
        self.mutex.acquire()
        if self.size == self.volumn:
            self.mutex.release()
            return False
        new_node = ListNode(order)
        self.ord2idx[order.username] = new_node
        if self.size == 0:
            self.head = new_node
            self.tail = new_node
            self.size = 1
            self.mutex.release()
            return True
        self.tail.next = new_node
        new_node.pre = self.tail
        self.tail = new_node
        self.size = self.size + 1
        self.mutex.release()
        return True

    # 删除元素(从队列头)
    def pop(self):
        self.mutex.acquire()
        if self.size == 0:
            self.mutex.release()
            return None
        ans = self.head
        del self.ord2idx[ans.order.username]
        self.size = self.size - 1
        if self.head.next is None:
            self.head = None
        else:
            self.head = self.head.next
            self.head.pre = None
        self.mutex.release()
        return ans.order

    # 查看第一个但是不删除
    def peek(self):
        self.mutex.acquire()
        ret = self.head.order if self.size else None
        self.mutex.release()
        return ret

    # 删除元素(中间删除)
    def cancel(self, username: str):
        self.mutex.acquire()
        if username not in self.ord2idx:
            self.mutex.release()
            return False
        before = self.ord2idx[username].pre
        after = self.ord2idx[username].next
        self.size = self.size - 1
        del self.ord2idx[username]
        if before is not None:
            before.next = after
        if after is not None:
            after.pre = before
        if before is None:
            self.head = after
        if after is None:
            self.tail = before
        self.mutex.release()
        return True

    def peek_all(self):
        self.mutex.acquire()
        ret = []
        cur = self.head
        while cur is not None:
            ret.append(cur.order)
            cur = cur.next
        self.mutex.release()
        return ret


class WaitArea:
    def __init__(self, n: int, mutex_wait_lock):
        self.EN = n * n  # 排队队列中的订单假定最多不会超过n*n
        self.N = n
        self.emergency_fast_queue = Queue(self.EN)
        self.emergency_slow_queue = Queue(self.EN)
        self.Wait_Queue = Queue(self.N)
        # 循环队列头尾下标
        # username->(队列名)
        self.usr2num = {}
        self.fast_serial = 1
        self.slow_serial = 1
        self.fast_order_in_wait = 0
        self.slow_order_in_wait = 0
        self.mutex_wait_lock = mutex_wait_lock

    def getCarBeforenum(self, username: str):
        if username not in self.usr2num:
            return -1
        ans = 0
        # 在emergency_fast_queue中
        if self.usr2num[username] == 'EF':
            tail = self.emergency_fast_queue.head
            while tail is not None and tail.order.username != username:
                tail = tail.next
                ans = ans + 1
            return ans
        # 在emergency_slow_queue中
        if self.usr2num[username] == 'ET':
            tail = self.emergency_slow_queue.head
            while tail is not None and tail.order.username != username:
                tail = tail.next
                ans = ans + 1
            return ans
        # 在Wait_Queue中
        if self.usr2num[username] == 'Wait':
            tail = self.Wait_Queue.head
            while tail is not None and tail.order.username != username:
                tail = tail.next
                ans = ans + 1
            return ans
        return -1

    # 将Order加入等待队列
    def addord(self, order: Order):
        self.mutex_wait_lock.acquire()
        if order.chargeType == 'F':
            order.serialnum = 'F' + str(self.fast_serial)
            self.usr2num[order.username] = "Wait"
            self.fast_serial = self.fast_serial + 1
            self.fast_order_in_wait = self.fast_order_in_wait + 1
        else:
            order.serialnum = 'T' + str(self.slow_serial)
            self.usr2num[order.username] = "Wait"
            self.slow_serial = self.slow_serial + 1
            self.slow_order_in_wait = self.slow_order_in_wait + 1
        order.status = "Wait"
        if self.Wait_Queue.push(order) is False:
            order.status = 'Declined'
            del self.usr2num[order.username]
            if order.chargeType == 'F':
                self.fast_serial = self.fast_serial - 1
                self.fast_order_in_wait = self.fast_order_in_wait - 1
            else:
                self.slow_serial = self.slow_serial - 1
                self.slow_order_in_wait = self.slow_order_in_wait - 1
            self.mutex_wait_lock.release()
            return False
        self.mutex_wait_lock.release()
        msg = "{}:新订单 ({}, {}, {}) 预约成功".format(intTodatetime(int(1000*Gettime())),order.username, order.chargeType, order.chargeQuantity)
        log.info(msg)
        msg = "{}:现在的等候区:[ ".format(intTodatetime(int(1000*Gettime())))
        allord = self.Wait_Queue.peek_all()
        for singleord in allord:
            msg += '({}, {}, {}) '.format(singleord.username, singleord.chargeType, singleord.chargeQuantity)
        msg += ']'
        log.info(msg)
        return True

    def emegency_add_f(self, order: Order):
        order.status = "emergency_wait_fast_queue"
        self.usr2num[order.username] = "EF"
        self.emergency_fast_queue.push(order)
        allorder = self.emergency_fast_queue.peek_all()
        msg = "{}:系统调度，紧急调度队列 F:[ ".format(intTodatetime(int(1000*Gettime())))
        for singleord in allorder:
            msg += '({}, {}, {}) '.format(singleord.username, singleord.chargeType, singleord.chargeQuantity)
        msg += ']'
        log.info(msg)

    def emegency_add_s(self, order: Order):
        order.status = "emergency_wait_slow_queue"
        self.usr2num[order.username] = "ET"
        self.emergency_slow_queue.push(order)
        allorder = self.emergency_slow_queue.peek_all()
        msg = "{}:系统调度，紧急调度队列slow:[ ".format(intTodatetime(int(1000*Gettime())))
        for singleord in allorder:
            msg += '({}, {}, {}) '.format(singleord.username, singleord.chargeType, singleord.chargeQuantity)
        msg += ']'
        log.info(msg)

    # 删除订单
    def delord(self, username):
        self.mutex_wait_lock.acquire()
        if username not in self.usr2num:
            self.mutex_wait_lock.release()
            return False
        if self.usr2num[username] == "EF":
            del self.usr2num[username]
            self.emergency_fast_queue.cancel(username)
        elif self.usr2num[username] == "ET":
            del self.usr2num[username]
            self.emergency_slow_queue.cancel(username)
        elif self.usr2num[username] == "Wait":
            if self.Wait_Queue.ord2idx[username].order.chargeType == 'F':
                self.fast_order_in_wait = self.fast_order_in_wait - 1
            else:
                self.slow_order_in_wait = self.slow_order_in_wait - 1
            del self.usr2num[username]
            self.Wait_Queue.cancel(username)
        else:
            self.mutex_wait_lock.release()
            return False
        self.mutex_wait_lock.release()
        msg = "{}:用户 {} 的订单取消成功".format(intTodatetime(int(1000*Gettime())),username)
        log.info(msg)
        msg = "{}:现在的等候区: [ ".format(intTodatetime(int(1000*Gettime())))
        allord = self.Wait_Queue.peek_all()
        for singleord in allord:
            msg += '({}, {}, {}) '.format(singleord.username, singleord.chargeType, singleord.chargeQuantity)
        msg += ']'
        log.info(msg)
        return True

    def touch_first_fast_order(self):
        ans = self.emergency_fast_queue.peek()
        if ans is not None:
            return ans
        cur = self.Wait_Queue.head
        while cur is not None and cur.order.chargeType != 'F':
            cur = cur.next
        if cur is None:
            return None
        ans = cur.order
        return ans

    def touch_first_slow_order(self):
        ans = self.emergency_slow_queue.peek()
        if ans is not None:
            return ans
        cur = self.Wait_Queue.head
        while cur is not None and cur.order.chargeType != 'T':
            cur = cur.next
        if cur is None:
            return None
        ans = cur.order
        return ans

    def fetch_first_fast_order(self):
        ans = self.emergency_fast_queue.pop()
        if ans is not None:
            del self.usr2num[ans.username]
            return ans
        # 在WaitQueue中找
        cur = self.Wait_Queue.head
        while cur is not None and cur.order.chargeType != 'F':
            cur = cur.next
        if cur is None:
            return None
        ans = cur.order
        self.fast_order_in_wait = self.fast_order_in_wait - 1
        del self.usr2num[ans.username]
        self.Wait_Queue.cancel(ans.username)
        return ans

    def fetch_first_slow_order(self):
        ans = self.emergency_slow_queue.pop()
        if ans is not None:
            del self.usr2num[ans.username]
            return ans
        # 在WaitQueue中找
        cur = self.Wait_Queue.head
        while cur is not None and cur.order.chargeType != 'T':
            cur = cur.next
        if cur is None:
            return None
        ans = cur.order
        self.slow_order_in_wait = self.slow_order_in_wait - 1
        del self.usr2num[ans.username]
        self.Wait_Queue.cancel(ans.username)
        return ans

    def change_quantity(self, username: str, quantity: int):
        self.Wait_Queue.ord2idx[username].order.chargeQuantity = quantity
        msg = "{}:现在的等候区: [ ".format(intTodatetime(int(1000 * Gettime())))
        allord = self.Wait_Queue.peek_all()
        for singleord in allord:
            msg += '({}, {}, {}) '.format(singleord.username, singleord.chargeType, singleord.chargeQuantity)
        msg += ']'
        log.info(msg)

    # 检测是否有等待
    def haswaitF(self):
        if self.fast_order_in_wait:
            return 1
        if self.emergency_fast_queue.size:
            return 1
        return 0

    def haswaitS(self):
        if self.slow_order_in_wait:
            return 1
        if self.emergency_slow_queue.size:
            return 1
        return 0


class PublicDataStruct:
    def __init__(self, db):
        global FAST_SPEED, SLOW_SPEED,TIME_ACC,system_start_time,system_start_time_stamp
        with open("./config.json", encoding='utf-8') as f:
            data = json.load(f)
        self.N, self.M, self.FPN, self.TPN = data['WSZ'], data['CQL'], data['FPN'], data['TPN']
        FAST_SPEED = data['FAST_SPEED']
        SLOW_SPEED = data['SLOW_SPEED']
        self.time_acc = data["TIME_ACC"]  # 时间加速比
        TIME_ACC = data["TIME_ACC"]
        # FAST_SPEED和SLOW_SPEED用于structure的其他类
        # self.Fast_Speed和self.Slow_Speed用于user.Service和admin.Service作为参数传递
        self.Fast_Speed = FAST_SPEED
        self.Slow_Speed = SLOW_SPEED
        self.usr2ord = {}  # username->Order
        self.usr2bill = {}  # username->[Bill]
        self.mutex_wait_lock = threading.Lock()
        self.waitqueue = WaitArea(self.N, self.mutex_wait_lock)
        self.fast_ready_lock = threading.Lock()
        self.slow_ready_lock = threading.Lock()
        # readyqueue = [{i}]
        self.FastReadyQueue = [i for i in range(0, self.FPN)]
        self.SlowReadyQueue = [i for i in range(0, self.TPN)]
        self.FastBoot = [
            ChargeBoot(self.M, 'F', FAST_SPEED, i, self.FastReadyQueue, self.fast_ready_lock, self.Schedule,
                       self.usr2bill,
                       self.usr2ord, self.time_acc, db) for i in range(0, self.FPN)]
        self.SlowBoot = [
            ChargeBoot(self.M, 'T', SLOW_SPEED, i, self.SlowReadyQueue, self.slow_ready_lock, self.Schedule,
                       self.usr2bill,
                       self.usr2ord, self.time_acc, db) for i in range(0, self.TPN)]

        system_start_time = time.time()
        system_start_time_stamp = int(time.mktime(time.strptime("2022-06-14 06:00:00", "%Y-%m-%d %H:%M:%S")))

    # 内部调度函数Schedule
    def Schedule(self):
        self.mutex_wait_lock.acquire()
        self.fast_ready_lock.acquire()
        while self.waitqueue.haswaitF() and len(self.FastReadyQueue):
            order = self.waitqueue.touch_first_fast_order()
            # 找到waittotal最小的FastBoot
            if order is None:
                break  # 为了互斥锁
            sel = []
            mi = 0x3f3f3f3f - 1
            # 得到所有有空位同一时刻的FastBoot的实时totalwait
            Totalwait = []
            # 记录最开始的time
            t1 = time.time()
            tm = intTodatetime(int(1000 * Gettime()))
            for i in range(0, len(self.FastReadyQueue)):
                Totalwait.append(
                    max(0, self.FastBoot[self.FastReadyQueue[i]].CalcRealWaittime() + time.time() - t1))
            for i in range(0, len(self.FastReadyQueue)):
                log.info("{}:充电桩 {} 预计等待时间: {}".format(tm,self.FastBoot[self.FastReadyQueue[i]].name, Totalwait[i]))
                if Totalwait[i] < mi:
                    sel = [i]
                    mi = Totalwait[i]
                elif math.fabs(Totalwait[i] - mi) < 1e-6:
                    sel.append(i)
            if len(sel) == 0:
                log.info("{}:调度中，没有正在工作的F型充电桩".format(intTodatetime(int(1000 * Gettime()))))
                break
            for i in sel:
                if self.FastBoot[self.FastReadyQueue[i]].isFull() is False:
                    sel = i
                    break
            else:
                log.info("{}:最短调度的充电桩 {} 满了".format(intTodatetime(int(1000*Gettime())),self.FastBoot[self.FastReadyQueue[sel[0]]].name))
                break
            order = self.waitqueue.fetch_first_fast_order()
            order.status = "S_F" + str(self.FastReadyQueue[sel])
            order.chargeID = 'F' + str(self.FastReadyQueue[sel] + 1)
            log.info("{}:调度成功，将订单 ({}, {}, {}) 加入了充电桩 F{} 的服务队列...".format(intTodatetime(int(1000*Gettime())),order.username,
                                                                        order.chargeType,
                                                                        order.chargeQuantity,
                                                                        self.FastReadyQueue[
                                                                            sel] + 1))
            self.FastBoot[self.FastReadyQueue[sel]].add(order)
        self.fast_ready_lock.release()
        self.slow_ready_lock.acquire()
        while self.waitqueue.haswaitS() and len(self.SlowReadyQueue):
            order = self.waitqueue.touch_first_slow_order()
            if order is None:
                break  # 为了互斥锁
            # 找到waittotal最小的SlowBoot
            sel = []
            mi = 0x3f3f3f3f - 1
            # 得到所有有空位同一时刻的SlowBoot的实时totalwait
            Totalwait = []
            # 记录最开始的time
            tm = intTodatetime(int(1000*Gettime()))
            t1 = time.time()
            for i in range(0, len(self.SlowReadyQueue)):
                Totalwait.append(
                    max(0, self.SlowBoot[self.SlowReadyQueue[i]].CalcRealWaittime() + time.time() - t1))
            for i in range(0, len(self.SlowReadyQueue)):
                log.info("{}:充电桩 {} 预计等待时间: {}".format(tm, self.SlowBoot[self.SlowReadyQueue[i]].name, Totalwait[i]))
                if Totalwait[i] < mi:
                    sel = [i]
                    mi = Totalwait[i]
                elif math.fabs(Totalwait[i] - mi) < 1e-6:
                    sel.append(i)
            if len(sel) == 0:
                log.info("{}:调度中，没有正在工作的S型充电桩".format(intTodatetime(int(1000 * Gettime()))))
                break
            for i in sel:
                if self.SlowBoot[self.SlowReadyQueue[i]].isFull() is False:
                    sel = i
                    break
            else:
                log.info("{}:最短调度的充电桩{}满了".format(intTodatetime(int(1000*Gettime())),self.SlowBoot[self.SlowReadyQueue[sel[0]]].name))
                break
            order = self.waitqueue.fetch_first_slow_order()
            order.status = "S_T" + str(self.SlowReadyQueue[sel])
            order.chargeID = 'T' + str(self.SlowReadyQueue[sel] + 1)
            log.info("{}:调度成功，将订单 ({}, {}, {}) 加入了充电桩 T{} 的服务队列...".format(intTodatetime(int(1000*Gettime())),order.username,
                                                                        order.chargeType,
                                                                        order.chargeQuantity,
                                                                        self.SlowReadyQueue[
                                                                            sel] + 1))
            self.SlowBoot[self.SlowReadyQueue[sel]].add(order)
        self.slow_ready_lock.release()
        self.mutex_wait_lock.release()

        msg = "{}:现在的等候区:[ ".format(intTodatetime(int(1000*Gettime())))
        allord = self.waitqueue.Wait_Queue.peek_all()
        for singleord in allord:
            msg += '({}, {}, {}) '.format(singleord.username, singleord.chargeType, singleord.chargeQuantity)
        msg += ']'
        log.info(msg)


    def writestatenow(self):
        #等待区所有的状态
        t1 = self.waitqueue.Wait_Queue.peek_all()
        str = "等待区:[ "
        for ord in t1:
            str += "({},{},{}) ".format(ord.username,ord.chargeType,ord.chargeQuantity)
        str += ']\n'
        #紧急快队列状态
        t1 = self.waitqueue.emergency_fast_queue.peek_all()
        str += "紧急快队列:[ "
        for ord in t1:
            str += "({},{},{}) ".format(ord.username, ord.chargeType, ord.chargeQuantity)
        str += ']\n'
        #紧急慢队列状态
        t1 = self.waitqueue.emergency_slow_queue.peek_all()
        str += "紧急慢队列:[ "
        for ord in t1:
            str += "({},{},{}) ".format(ord.username, ord.chargeType, ord.chargeQuantity)
        str += ']\n'
        #快充充电桩状态
        for boot in self.FastBoot:
            if boot.working is False:
                str += "充电桩{}:关闭\n".format(boot.name)
                continue
            t1 = boot.get_real_time_info()
            str += "充电桩{}:[ ".format(boot.name)
            for ord in t1:
                str += "({},{},{}) ".format(ord[0], ord[1], ord[2])
            str += ']\n'
        #慢充充电桩状态
        for boot in self.SlowBoot:
            if boot.working is False:
                str += "充电桩{}:关闭\n".format(boot.name)
                continue
            t1 = boot.get_real_time_info()
            str += "充电桩{}:[ ".format(boot.name)
            for ord in t1:
                str += "({},{},{}) ".format(ord[0], ord[1], ord[2])
            str += ']\n'
        log2.info("{}:".format(intTodatetime(int(Gettime()*1000))) + str)