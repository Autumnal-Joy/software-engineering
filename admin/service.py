class Service:
    def __init__(self, db):
        self.db = db

    def adminLogin(self, param):
        data, err = True, None  # False, "User Not Fount"
        return data, err

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
