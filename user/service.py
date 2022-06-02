class Service:

    def __init__(self, db):
        self.db = db

    def userLogin(self, params):
        data, err = True, None  # False, "User Not Fount"
        return data, err

    def userRegister(self, params):
        data, err = True, None  # False, "User Not Fount"
        return data, err

    def userSendOrder(self, params):
        return True, None

    def userGetOrder(self, params):
        return {
                   "charge_type": "fast",
                   "charge_num": 0.53
               }, None

    def userGetLineNo(self, params):
        return {
                   "number": 10
               }, None

    def userGetRank(self, params):
        return {
                   "number": 10
               }, None

    def userSendChargeType(self, params):
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
