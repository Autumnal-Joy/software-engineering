from structure import Order
from structure import WaitArea
usr2ord = {}
N = 10 #等待区大小
waitqueue = WaitArea(N)

#假定 数据库查表操作 Query(表名,key) Insert(表名,key,dict) Delete(表名,key) Update(表名,key,dict)
#设计成Nosql一样的 key->dict
def Query(tablename:str,key:str)->dict:
    return {}
def Insert(tablename:str,key:str,val:dict)->bool:
    return True
def Delete(tablename:str,key:str)->bool:
    return True
def Update(tablename:str,key:str,val:dict)->bool:
    return True



def userLogin(username:str,password:str):
    table = Query("UserInfo",username)
    if(table.has_key("password") == False):
        return (False,"用户不存在")
    if(table["password"] != password):
        return (False,"用户名或密码错误")
    return True

def register(username:str,password:str):
    table = Query("UserInfo",username)
    if(table.has_key("password")):
        return (False,"用户已存在")
    table = {'username':username,'password':password}
    if(Insert("UserInfo",username,table) == False):
        return (False,"数据库载入错误")
    return True


#内部函数


#提交订单(包含车辆排队号码生成)预约排号
#Info为表单信息，如果等候区满，则返回ERROR{等候区满}
#否则根据表单信息生成Order并加入等候区队列中，返回True
def userSendOrder(username:str,chargeType:str,chargeQuantity:int):
    new_ord = Order(username,chargeType,chargeQuantity)
    res = waitqueue.addord(new_ord)
    if(res == False):
        return {False,"同类型的等待区已满"}
    new_ord.serialnum = res[1]
    usr2ord[username] = new_ord
    return True
def userGetOrder(username:str):
    if(usr2ord.has_key(username) == False):
        return (False,"该用户不存在订单")
    return usr2ord[username]

def getLineNo(username:str):
    if (usr2ord.has_key(username) == False):
        return (False, "该用户不存在订单")
    return usr2ord[username].serialnum
#获取前面还有多少种同类型的订单
def userGetRank(username:str):
    if (usr2ord.has_key(username) == False):
        return (False, "该用户不存在订单")
    ans = WaitArea.getCarBeforenum(username)
    if (ans == False):
        return (False, "该用户的订单正在服务队列")
    return ans

def userSendChargeType(username:str,type:str):

def userSendChargeQuantity(username:str,quantity:int):

def userSendCancelCharge(username:str):

def userGetBillsList(username:str):

def userGetBill(username:str,billID:int):







