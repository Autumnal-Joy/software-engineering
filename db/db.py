import logging

FPN = 2
TPN = 3

'''
log.info("message")
'''

log = logging.getLogger('app')


class DB:
    def __init__(self, path):
        # 临时用
        self.ChargerBillList = {}
        for i in range(1,FPN+1):
            self.ChargerBillList["F" + str(i)] = {}
        for i in range(1,TPN+1):
            self.ChargerBillList["T" + str(i)] = {}
        # print("ChargerBillList",self.ChargerBillList)

    def Query(self, tablename: str, key: str):
        # 前端测试密码为: 123456, 此处是MD5加密
        if tablename == "UserInfo":
            return {"username": key, "password": "e10adc3949ba59abbe56e057f20f883e"}
        if tablename == "AdminInfo":
            return {"username": key, "password": "e10adc3949ba59abbe56e057f20f883e"}
        if tablename == "ChargerBillList":
            return self.ChargerBillList[key]
        if tablename == "Report":
            return self.bill

    def Insert(self, tablename: str, key: str, val: dict) -> bool:
        return True

    def Delete(self, tablename: str, key: str) -> bool:
        return True

    def Update(self, tablename: str, id: str, val: dict) -> bool:
        if tablename == "ChargerBillList":
            for i in val:
                bill = val[i]
                name = bill.chargeID
                self.ChargerBillList[name][i] = bill
        return True
