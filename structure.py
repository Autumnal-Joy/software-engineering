from threading import Timer
import time
import datetime
import json
import threading

FAST_SPEED = 0
SLOW_SPEED = 0


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
    def __init__(self, username, chargeType, chargeQuantity,Gettime):
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

    # 用于debug
    def show(self):
        print("Order信息:")
        print("username:", self.username)
        print("chargeType", self.chargeType)
        print("chargeQuantity", self.chargeQuantity)
        print("serialnum:", self.serialnum)
        print("status:", self.status)
        print("begin_time:", intTodatetime(int(self.begin * 1000)) if self.begin else "未开始")
        print("end_time:", intTodatetime(int(self.end * 1000)) if self.end else "未结束")
        print("aimed_end_time", intTodatetime(int(self.aimed_end_time * 1000)) if self.aimed_end_time else "未加入服务队列")


id = 1


class Bill:
    def __init__(self, order, Gettime , canceled=0):
        if type(order) == Order:
            global id
            self.BillID = id
            id = id + 1
            self.chargeID = order.chargeID
            self.billTime = Gettime() * 1000
            self.username = order.username
            self.charge_type = order.chargeType
            self.aimed_quantity = order.chargeQuantity
            # print(order.end,order.begin)
            self.real_quantity = round((order.end - order.begin) * (
                FAST_SPEED if order.chargeType == 'fast' else SLOW_SPEED) if canceled else order.chargeQuantity, 3)
            self.start_tm = intTodatetime(int(order.begin * 1000))
            self.end_tm = intTodatetime(int(order.end * 1000))
            self.start = order.begin * 1000
            self.end = order.end * 1000
            self.chargecost, self.servecost = self.Calc(FAST_SPEED if order.chargeType == 'F' else SLOW_SPEED)
            self.totalcost = round(self.chargecost + self.servecost, 2)
            self.aimed_end_time = intTodatetime(int(order.aimed_end_time))
            #self.Show()
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
        return

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
        fee = [0.3, 0.7, 1.0, 0.7, 1.0, 0.7, 0.3, 0.3]
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
            print("Calc Error")
        return round(charge_cost, 2), round(0.8 * self.real_quantity, 2)
    def Show(self):
        print("生成了账单:")
        print("username = ", self.username)
        print("billID = ", self.BillID)
        print("billTime = ", self.billTime)
        print("charge_type = ", self.charge_type)
        print("aimed_quantity = ", self.aimed_quantity)
        print("real_quantity = ", self.real_quantity)
        print("start_tm:", self.start_tm)
        print("end_tm:", self.end_tm)
        print("aimed_end_time", self.aimed_end_time)
        print("cost = ", self.chargecost, self.servecost)
        print("start", self.start)
        print("end", self.end)
        print("chargeID", self.chargeID)
        print("chargecost:", self.chargecost)
        print("servecost:", self.servecost)


class ChargeBoot:
    def __init__(self, M: int, type: str, speed: int, rank: int, ReadyQueue: list, ready_queue_lock, Schedule, Gettime,usr2bill,
                 usr2ord, time_acc,db):
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
        self.Gettime = Gettime
        self.time_acc = time_acc
    def get_all_ord_now(self):
        return self.ServeQueue.peek_all()

    # 开机，均摊
    def start(self):
        self.ready_queue_lock.acquire()
        if self.rank not in self.ReadyQueue:
            self.ReadyQueue.append(self.rank)
        self.ready_queue_lock.release()
        self.working = True

    # 关机，故障，其他均摊
    # 将在队列中的拿出去
    # 将队列中的全部拿出去
    def shut(self) -> list:
        # 从ReadyQueue中删除
        self.ready_queue_lock.acquire()
        # xmx修改过#之前del self.ReadyQueue[i]长度减小导致i越界
        del_cnt = 0
        for i in range(0, len(self.ReadyQueue)):
            if self.ReadyQueue[i - del_cnt] == self.rank:
                del self.ReadyQueue[i]
                del_cnt = del_cnt + 1
        self.ready_queue_lock.release()
        ans = []
        if self.busy:
            head = self.ServeQueue.pop()
            self.timers[head.username][0].cancel()
            head.status = 'Partial-Compelete'
            head.end = self.Gettime()
            if head.username in self.usr2bill:
                bill = Bill(head, self.Gettime,1)
                self.usr2bill[head.username].append(bill)
                table = self.db.Query("ChargerBillList", self.name)
                table[str(int(self.Gettime())) + '_' + str(bill.BillID)] = bill
                self.db.Update("ChargerBillList", self.name, table)
            else:
                bill = Bill(head,self.Gettime,1)
                self.usr2bill[head.username] = [bill]
                table = self.db.Query("ChargerBillList", self.name)
                table[str(int(self.Gettime())) + '_' + str(bill.BillID)] = bill
                self.db.Update("ChargerBillList", self.name, table)
            del self.timers[head.username]
            # 结算正在进行的
            ans.append(Order(head.username, head.chargeType,
                             head.chargeQuantity - (head.end - head.begin) * self.Charge_Speed))
        while self.ServeQueue.size:
            ans.append(self.ServeQueue.pop())
        self.working = False
        return ans

    # 添加订单 外面控制了是否满 因此这里没必要控制
    def add(self, order: Order):
        order.aimed_end_time = (self.Gettime() + self.CalcRealWaittime() + order.chargeQuantity / self.Charge_Speed) * 1000
        self.totalwait += order.chargeQuantity / self.Charge_Speed
        self.ServeQueue.push(order)
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
        self.timers[order.username] = (Timer(cgt , self.CallBack), self.Gettime())
        self.timers[order.username][0].start()
        order.begin = self.Gettime()
        print("user {}开启了一个{}s的定时(时间加速{}倍)".format(order.username, cgt,self.time_acc))

        self.busy = True

    # 定时器结束的回调函数，包含生成账单，从服务队列中移除等
    def CallBack(self, cancel=0):
        endt = self.Gettime()
        ord = self.ServeQueue.pop()
        ord.status = 'Compelete'
        ord.end = endt
        self.totalwait -= ord.chargeQuantity / self.Charge_Speed
        if ord.username in self.usr2bill:
            bill = Bill(ord, self.Gettime, cancel)
            self.usr2bill[ord.username].append(bill)
            table = self.db.Query("ChargerBillList", self.name)
            table[str(int(self.Gettime())) + '_' + str(bill.BillID)] = bill
            self.db.Update("ChargerBillList", self.name, table)
        else:
            bill = Bill(ord,self.Gettime,cancel)
            self.usr2bill[ord.username] = [bill]
            table = self.db.Query("ChargerBillList", self.name)
            table[str(int(self.Gettime())) + '_' + str(bill.BillID)] = bill
            self.db.Update("ChargerBillList", self.name, table)
        self.busy = False
        del self.timers[ord.username]
        del self.usr2ord[ord.username]
        # 继续服务下一个订单
        self.consume()
        self.ready_queue_lock.acquire()
        if self.rank not in self.ReadyQueue:
            self.ReadyQueue.append(self.rank)
        self.ready_queue_lock.release()
        self.Schedule()

    # 删除订单
    def delord(self, username):
        head = self.ServeQueue.peek()
        if head.username == username:
            # 计算已充电时间
            self.timers[username][0].cancel()
            self.CallBack(1)
            return True
        del self.usr2ord[username]
        return self.ServeQueue.cancel(username)

    # 计算实时全队等待时间
    def CalcRealWaittime(self):
        top = self.ServeQueue.peek()
        if top is None:
            return self.totalwait
        return self.totalwait - (self.Gettime() - self.timers[top.username][1])

    # 用于debug
    def witness(self):
        print("volumn:", self.volumn)
        print("ServeQueue:")
        print("type:", self.type)
        print("Schedule:", self.Schedule)
        print("timers:")
        for i in self.timers:
            print(i, self.timers[i])
        print("totalwait:", self.totalwait)
        print("ChargeSpeed:", self.Charge_Speed)
        print("busy:", self.busy)
        print("rank:", self.rank)
        print("usr2bill:")
        for i in self.usr2bill:
            print("User " + i + "的Bill:")
            for j in self.usr2bill[i]:
                j.show()
        print("ReadyQueue:")
        for i in self.ReadyQueue:
            print(i, end='')


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
            # print("***cur", cur)
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
        return True

    def emegency_add_f(self, order: Order):
        order.status = "emergency_wait_fast_queue"
        self.usr2num[order.username] = "EF"
        self.emergency_fast_queue.push(order)

    def emegency_add_s(self, order: Order):
        order.status = "emergency_wait_slow_queue"
        self.usr2num[order.username] = "ET"
        self.emergency_slow_queue.push(order)

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
        return True

    def fetch_first_fast_order(self):
        ans = self.emergency_fast_queue.pop()
        #print("emergency_fast_size", self.emergency_fast_queue.size)
        #print("Get", ans)
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

    # 用于debug
    def witness(self):
        print("EN=", self.EN)
        print("N=", self.N)
        print("emergency_fast_queue:")
        # self.emergency_fast_queue.traverse()
        print("emergency_slow_queue:")
        # self.emergency_slow_queue.traverse()
        print("Wait_Queue:")
        # self.Wait_Queue.traverse()
        print("usr2num:")
        for i in self.usr2num:
            print(i, ":", self.usr2num[i])
        print("fast_serial:", self.fast_serial)
        print("slow_serial:", self.slow_serial)


class PublicDataStruct:
    def __init__(self, db):
        global FAST_SPEED, SLOW_SPEED
        with open("./config.json", encoding='utf-8') as f:
            data = json.load(f)
        self.N, self.M, self.FPN, self.TPN = data['WSZ'], data['CQL'], data['FPN'], data['TPN']
        FAST_SPEED = data['FAST_SPEED']
        SLOW_SPEED = data['SLOW_SPEED']
        self.time_acc = data["TIME_ACC"] #时间加速比
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
        self.FastReadyQueue = [i for i in range(0, self.FPN)]
        self.SlowReadyQueue = [i for i in range(0, self.TPN)]
        self.FastBoot = [
            ChargeBoot(self.M, 'F', FAST_SPEED, i, self.FastReadyQueue, self.fast_ready_lock, self.Schedule,self.Gettime,
                       self.usr2bill,
                       self.usr2ord, self.time_acc,db) for i in range(0, self.FPN)]
        self.SlowBoot = [
            ChargeBoot(self.M, 'T', SLOW_SPEED, i, self.SlowReadyQueue, self.slow_ready_lock, self.Schedule,self.Gettime,
                       self.usr2bill,
                       self.usr2ord, self.time_acc,db) for i in range(0, self.TPN)]

        self.system_start_time = time.time()
        self.system_start_time_stamp = int(time.mktime(time.strptime("2022-06-14 06:00:00","%Y-%m-%d %H:%M:%S")))

    # 内部调度函数Schedule
    def Schedule(self):
        #print("准备调度")
        #("size:", self.waitqueue.Wait_Queue.size, self.waitqueue.usr2num)
        #print("fast_ready", self.FastReadyQueue)
        #print("slow_ready", self.SlowReadyQueue)
        self.mutex_wait_lock.acquire()
        self.fast_ready_lock.acquire()
        #print("开始调度快队列", self.waitqueue.fast_order_in_wait)
        while self.waitqueue.haswaitF() and len(self.FastReadyQueue):
            order = self.waitqueue.fetch_first_fast_order()
            # 找到waittotal最小的FastBoot
            if order is None:
                break  # 为了互斥锁
            sel = 0
            # 得到所有有空位同一时刻的FastBoot的实时totalwait
            Totalwait = []
            # 记录最开始的time
            t1 = time.time()
            for i in range(0, len(self.FastReadyQueue)):
                Totalwait.append(
                    max(0, self.FastBoot[self.FastReadyQueue[i]].CalcRealWaittime() + time.time() - t1))
            #print(Totalwait)
            for i in range(1, len(self.FastReadyQueue)):
                if Totalwait[i] < Totalwait[sel]:
                    sel = i
            order.status = "S_F" + str(self.FastReadyQueue[sel])
            order.chargeID = 'F' + str(self.FastReadyQueue[sel]+1)
            print("调度成功，将订单(username:{},chargetype:{},chargeQuantity:{})加入了充电桩F{}的服务队列...".format(order.username,
                                                                                                  order.chargeType,
                                                                                                  order.chargeQuantity,
                                                                                                  self.FastReadyQueue[
                                                                                                      sel]+1))
            self.FastBoot[self.FastReadyQueue[sel]].add(order)
            # 检测如果充电桩满了就删除
            if self.FastBoot[self.FastReadyQueue[sel]].isFull():
                del self.FastReadyQueue[sel]
        self.fast_ready_lock.release()
        self.slow_ready_lock.acquire()
        #print("开始调度慢队列", self.waitqueue.slow_order_in_wait)
        while self.waitqueue.haswaitS() and len(self.SlowReadyQueue):
            order = self.waitqueue.fetch_first_slow_order()
            if order is None:
                break  # 为了互斥锁
            # 找到waittotal最小的FastBoot
            sel = 0
            # 得到所有有空位同一时刻的SlowBoot的实时totalwait
            Totalwait = []
            # 记录最开始的time
            t1 = time.time()
            for i in range(0, len(self.SlowReadyQueue)):
                Totalwait.append(
                    max(0, self.SlowBoot[self.SlowReadyQueue[i]].CalcRealWaittime() + time.time() - t1))
            for i in range(0, len(self.SlowReadyQueue)):
                if Totalwait[i] < Totalwait[sel]:
                    sel = i
            order.status = "S_T" + str(self.SlowReadyQueue[sel])
            order.chargeID = 'T' + str(self.SlowReadyQueue[sel]+1)
            print("调度成功，将订单(username:{},chargetype:{},chargeQuantity:{})加入了充电桩T{}的服务队列...".format(order.username,
                                                                                                  order.chargeType,
                                                                                                  order.chargeQuantity,
                                                                                                  self.SlowReadyQueue[
                                                                                                      sel]+1))
            self.SlowBoot[self.SlowReadyQueue[sel]].add(order)
            if self.SlowBoot[self.SlowReadyQueue[sel]].isFull():
                del self.SlowReadyQueue[sel]
        self.slow_ready_lock.release()
        self.mutex_wait_lock.release()


    # 内部计算时间函数Gettime()
    def Gettime(self):
        return self.system_start_time_stamp + (time.time() - self.system_start_time) * self.time_acc
