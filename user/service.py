class Service:

    def __init__(self, db):
        self.db = db

    # params.username
    # params.password
    def userLogin(self, params):
        data, err = True, None  # False, "User Not Fount"
        return data, err

    # params.username
    # params.password
    def userRegister(self, params):
        data, err = True, None  # False, "User Not Fount"
        return data, err

    # params.username
    # params.chargeQuantity
    # params.chargeType: "fast"|"slow"
    def userSendOrder(self, params):
        return True, None

    # params.username
    def userGetOrder(self, params):
        # data, err = None, "用户尚未预约"
        data, err = {
                        "chargeType": "fast",
                        "chargeQuantity": 12
                    }, None
        return data, err

    # params.username
    def userGetLineNo(self, params):
        return {
                   "lineNo": "T10"
               }, None

    # params.username
    def userGetRank(self, params):
        return {
                   "rank": 10,
                   "waitingTime": 1654275723231
               }, None

    # params.username
    # params.chargeType
    # params.chargeQuantity
    def userSendChargeType(self, params):
        return True, None

    # params.username
    # params.chargeQuantity
    def userSendChargeQuantity(self, param):
        return True, None

    # params.username
    def userSendCancelCharge(self, param):
        return True, None

    # params.username
    def userGetBillsList(self, param):
        return [
                   {"billID": 1, "billTime": 1234, "chargeQuantity": "high"}
               ], None

    # params.username
    # params.billID
    def userGetBill(self, param):
        return {
                   "billID": 1,
                   "billTime": 1234,
                   "chargerID": 2,
                   "chargeQuantity": 123,
                   "chargeTime": 1234,
                   "startTime": 1234,
                   "endTime": 1234,
                   "chargeCost": 100,
                   "serviceCost": 100,
                   "cost": 200
               }, None
