from service import Service

# 临时用
ChargerDb = [{
            "chargerID": 1,
            "working": True,
            "totalChargeCount": 30,
            "totalChargeTime": 123456789,
            "totalChargeQuantity": 120
            }, {
            "chargerID": 2,
            "working": False,
            "totalChargeCount": 12,
            "totalChargeTime": 123456789,
            "totalChargeQuantity": 120
            }, {
            "chargerID": 3,
            "working": False,
            "totalChargeCount": 0,
            "totalChargeTime": 0,
            "totalChargeQuantity": 0
            }]

report = [{
            "time": "今日",
            "totalChargeCount": 30,
            "totalChargeTime": 99999999,
            "totalChargeQuantity": 320,
            "totalChargeCost": 1100,
            "totalServiceCost": 600,
            "totalCost": 1700,
            "chargers": [{
                "chargerID": 1,
                "totalChargeCount": 10,
                "totalChargeTime": 12345678,
                "totalChargeQuantity": 120,
                "totalChargeCost": 100,
                "totalServiceCost": 100,
                "totalCost": 200
            }, {
                "chargerID": 2,
                "totalChargeCount": 20,
                "totalChargeTime": 87654321,
                "totalChargeQuantity": 200,
                "totalChargeCost": 1000,
                "totalServiceCost": 500,
                "totalCost": 1500
            }]
        }, {
            "time": "本周",
            "totalChargeCount": 30,
            "totalChargeTime": 99999999,
            "totalChargeQuantity": 320,
            "totalChargeCost": 1100,
            "totalServiceCost": 600,
            "totalCost": 1700,
            "chargers": [{
                "chargerID": 1,
                "totalChargeCount": 10,
                "totalChargeTime": 12345678,
                "totalChargeQuantity": 120,
                "totalChargeCost": 100,
                "totalServiceCost": 100,
                "totalCost": 200
            }, {
                "chargerID": 2,
                "totalChargeCount": 20,
                "totalChargeTime": 87654321,
                "totalChargeQuantity": 200,
                "totalChargeCost": 1000,
                "totalServiceCost": 500,
                "totalCost": 1500
            }]
        }]

class DB:
    def __init__(self, path):
        print("DB", path)

    def Query(self, tablename: str, key: str):
        # 前端测试密码为: 123456, 此处是MD5加密
        if tablename == "AdminInfo":
            return {"username": key, "password": "1"}
        if tablename == "ChargerInfo":
            return ChargerDb
        if tablename == "Report":
            return report




    def Insert(self,tablename: str, key: str, val: dict) -> bool:
        return True

    def Delete(self,tablename: str, key: str) -> bool:
        return True

    def Update(self,tablename: str, id:int, newval: dict) -> bool:
        if tablename =="ChargeInfo":
            ChargerDb[id - 1] = newval
        return True


db = DB("1")
t = Service(db)

print("***************AdminLogin test**************:")
print(db.Query("AdminInfo", "a"))
print(t.adminLogin("a","1"))
print(t.adminLogin("a","2"))
print("***************Get chargers test**************:")
print(t.adminGetChargers())
print("***************Turn chargers test**************:")
print(t.adminTurnCharger(4 , False))
print(t.adminTurnCharger(1 , False))
print(t.adminGetChargers())
print("***************Get users test**************:")
print(t.adminGetUsers(1))
print(t.adminGetUsers(2))
print("***************Get report test**************:")
print(t.adminGetTable())