class Service:

    def __init__(self, db):
        self.db = db

    def userLogin(self, param):
        data, err = True, None  # False, "User Not Fount"
        return data, err

    def userSendOrder(self, param):
        return True, None

    def userGetOrder(self, param):
        return {
                   "charge_type": "fast",
                   "charge_num": 0.53
               }, None

    def userGetLineNo(self, param):
        return {
                   "number": 10
               }, None

    def userGetRank(self, param):
        return {
                   "number": 10
               }, None

    def userSendChargeType(self, param):
        return True, None

    def userSendCahrgeQuantity(self, param):
        return True, None

    def userSendCancelCharge(self, param):
        return True, None

    def userGetBill(self, param):
        return {
                   "billID": 1,
                   "billTime": 1234,
                   "chargerID": 2,
                   "chargeQuantity": "high",
                   "chargeTime": 1234,
                   "startTime": 1234,
                   "endTime": 1234,
                   "chargeCost": 100,
                   "serviceCost": 100,
                   "cost": 200
               }, None

    def userGetBillsList(self, param):
        return [
                   {"billID": 1, "billTime": 1234, "chargeQuantity": "high"}
               ], None

    def adminLogin(self, param):
        return True, None

    def adminGetChargers(self, param):
        return [
                   {"working": False, "totalChargeCount": 100, "totalChargeTime": 100, "totalChargeQuantity": "high"}
               ], None

    def adminTurnCharger(self, param):
        return True, None

    def adminGetCars(self, param):
        return [
                   {"username": "walker", "chargeQuantity": "high", "waitTime": 1234}
               ], None

    def adminGetTable(self, param):
        return {
                   "time": 1234, "chargerID": 1, "totalChargeCount": 10, "totalChargeTime": 100,
                   "totalChargeQuantity": "high", "totalChargeCost": 100, "totalServiceCost": 100,
                   "totalCost": 100
               }, None
