from re import match

class Order:
    def __init__(self,username,chargeType,chargeQuantity):
        self.username = username             #用户名
        self.chargeType = chargeType         #充电类型
        self.chargeQuantity = chargeQuantity #充电量
        self.serialnum = 0                   #序列号
class WaitArea:
    def __init__(self,n:int):
        self.EN = n*n #排队队列中的订单假定最多不会超过n*n
        self.N = n
        self.emergency_fast_queue = Order[self.EN]
        self.emergency_slow_queue = Order[self.EN]
        self.Wait_Queue = Order[n]
        #循环队列头尾下标
        self.hh,self.tt,= 0,0
        self.hh_emf,self.tt_emf,self.hh_ems,self.tt_ems = 0,0,0,0
        #username->(队列名,下标)
        self.usr2num = {}
        self.fast_serial = 0
        self.slow_serial = 0
    def getCarBeforenum(self,username:str):
        if(self.usr2num.has_key(username) == False):
            return False
        # 在emergency_fast_queue中
        if(self.usr2num[username][0] == 'EF'):
            return (self.usr2num[username][1] - self.hh_emf + self.EN) % self.EN
        # 在emergency_slow_queue中
        if (self.usr2num[username][0] == 'ET'):
            return (self.usr2num[username][1] - self.hh_ems + self.EN) % self.EN
        # 在Slow_Queue中
        if (match('(T|F)[1-9][0-9]*$', self.usr2num[username])):
            ord = self.usr2num[username][1]
            type = self.Wait_Queue[ord].chargeType
            i = self.hh
            ans = 0
            while(i != ord):
                if(self.Wait_Queue[i].chargeType == type):
                    ans = ans + 1
            return ans
        return False
    # 将Order加入等待队列
    def addord(self,order: Order):
        if(self.tt - self.hh == self.N):
            return False
        if (order.chargeType == 'F'):
            order.serialnum = 'F' + str(self.fast_serial)
            self.Wait_Queue[self.tt] = order
            self.usr2num[order.username] = ('Wait',self.tt)
            self.tt = (self.tt + 1) % self.N
            self.fast_serial = self.fast_serial + 1
        else:
            order.serialnum = 'T' + str(self.slow_serial)
            self.Slow_Queue[self.tt_s] = order
            self.usr2num[order.username] = ('Wait',self.tt)
            self.tt = (self.tt + 1) % self.N
            self.slow_serial = self.slow_serial + 1
        return (True,order.serialnum)



