from threading import Timer
import time
import datetime


def intTodatetime(intValue):
    if len(str(intValue)) == 10:  # 精确到秒
        timeValue = time.localtime(intValue)
        tempDate = time.strftime("%Y-%m-%d %H:%M:%S", timeValue)
        datetimeValue = datetime.datetime.strptime(tempDate, "%Y-%m-%d %H:%M:%S")
    elif 10 < len(str(intValue)) < 15:  # 精确到毫秒
        k = len(str(intValue)) - 10
        timetamp = datetime.datetime.fromtimestamp(intValue / (1 * 10 ** k))
        datetimeValue = timetamp.strftime("%Y-%m-%d %H:%M:%S.%f")
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


id = 0


class Bill:
    def __init__(self, order: Order, canceled=0):
        global id
        self.BillID = id
        id = id + 1
        self.chargeID = order.chargeID
        self.billTime = time.time()
        self.username = order.username
        self.charge_type = order.chargeType
        self.aimed_quantity = order.chargeQuantity
        # print(order.end,order.begin)
        self.real_quantity = (order.end - order.begin) * (
            30 if order.chargeType == 'fast' else 10) if canceled else order.chargeQuantity
        self.start_tm = intTodatetime(int(order.begin * 1000))
        self.end_tm = intTodatetime(int(order.end * 1000))
        self.start = order.begin
        self.end = order.end
        self.chargecost, self.servecost = self.Calc()
        self.aimed_end_time = intTodatetime(int(order.aimed_end_time * 1000))
        self.Show()

    # 计算费用
    def Calc(self):
        return 1, 1

    def Show(self):
        print("生成了账单:")
        print("username = ", self.username)
        print("billID = ", self.BillID)
        print("charge_type = ", self.charge_type)
        print("aimed_quantity = ", self.aimed_quantity)
        print("real_quantity = ", self.real_quantity)
        print("start_tm:", self.start_tm)
        print("end_tm:", self.end_tm)
        print("aimed_end_time", self.aimed_end_time)
        print("cost = ", self.chargecost, self.servecost)


class ChargeBoot:
    def __init__(self, M: int, type: str, speed: int, rank: int, ReadyQueue: list, ready_queue_lock, Schedule, usr2bill,
                 usr2ord):
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

    # 开机，均摊
    def start(self):
        self.ready_queue_lock.acquire()
        if self.rank not in self.ReadyQueue:
            self.ReadyQueue.append(self.rank)
        self.ready_queue_lock.release()

    # 关机，故障，其他均摊
    # 将在队列中的拿出去
    # 将队列中的全部拿出去
    def shut(self) -> list:
        # 从ReadyQueue中删除
        self.ready_queue_lock.acquire()
        for i in range(0, len(self.ReadyQueue)):
            if self.ReadyQueue[i] == self.rank:
                del self.ReadyQueue[i]
        self.ready_queue_lock.release()
        ans = []
        if self.busy:
            head = self.ServeQueue.pop()
            self.timers[head.username][0].cancel()
            head.status = 'Partial-Compelete'
            head.end = time.time()
            if head.username in self.usr2bill:
                self.usr2bill[head.username].append(Bill(head, 1))
            else:
                self.usr2bill[head.username] = [Bill(head, 1)]
            del self.timers[head.username]
            # 结算正在进行的
            ans.append(Order(head.username, head.chargeType,
                             head.chargeQuantity - (head.end - head.begin) * self.Charge_Speed))
        while self.ServeQueue.size:
            ans.append(self.ServeQueue.pop())
        return ans

    # 添加订单 外面控制了是否满 因此这里没必要控制
    def add(self, order: Order):
        order.aimed_end_time = time.time() + self.CalcRealWaittime() + order.chargeQuantity / self.Charge_Speed
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
        self.timers[order.username] = (Timer(order.chargeQuantity / self.Charge_Speed, self.CallBack), time.time())
        self.timers[order.username][0].start()
        order.begin = time.time()
        print("user {}开启了一个{}s的定时".format(order.username, order.chargeQuantity / self.Charge_Speed))

        self.busy = True

    # 定时器结束的回调函数，包含生成账单，从服务队列中移除等
    def CallBack(self, cancel=0):
        endt = time.time()
        ord = self.ServeQueue.pop()
        ord.status = 'Compelete'
        ord.end = endt
        self.totalwait -= ord.chargeQuantity / self.Charge_Speed
        if ord.username in self.usr2bill:
            self.usr2bill[ord.username].append(Bill(ord, cancel))
        else:
            self.usr2bill[ord.username] = [Bill(ord, cancel)]
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
        return self.totalwait - (time.time() - self.timers[top.username][1])

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
        self.head = None
        self.tail = None
        self.size = 0
        self.volumn = N
        self.ord2idx = {}
        # self.mutex = threading.Lock() #互斥锁，防止定时器回调函数脏数据

    # 添加元素(从队列尾)
    def push(self, order: Order):
        if self.size == self.volumn:
            return False
        new_node = ListNode(order)
        self.ord2idx[order.username] = new_node
        if self.size == 0:
            self.head = new_node
            self.tail = new_node
            self.size = 1
            return True
        self.tail.next = new_node
        new_node.pre = self.tail
        self.tail = new_node
        self.size = self.size + 1
        return True

    # 删除元素(从队列头)
    def pop(self):
        if self.size == 0:
            return None
        ans = self.head
        del self.ord2idx[ans.order.username]
        self.size = self.size - 1
        if self.head.next is None:
            self.head = None
        else:
            self.head = self.head.next
            self.head.pre = None
        return ans.order

    # 查看第一个但是不删除
    def peek(self):
        return self.head.order if self.size else None

    # 删除元素(中间删除)
    def cancel(self, username: str):
        if username not in self.ord2idx:
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
        return True


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
        if order.chargeType == 'fast':
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
            if order.chargeType == 'fast':
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
            if self.Wait_Queue.ord2idx[username].order.chargeType == 'fast':
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
        print("emergency_fast_size", self.emergency_fast_queue.size)
        print("Get", ans)
        if ans is not None:
            del self.usr2num[ans.username]
            return ans
        # 在WaitQueue中找
        cur = self.Wait_Queue.head
        while cur is not None and cur.order.chargeType != 'fast':
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
        while cur is not None and cur.order.chargeType != 'slow':
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