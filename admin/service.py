class Service:
    def __init__(self, db):
        self.db = db

    # params.username
    # params.password
    def adminLogin(self, params):
        data, err = True, None  # False, "User Not Fount"
        return data, err

    # params.username
    def adminGetChargers(self, params):
        return [
                   {"working": False, "totalChargeCount": 100, "totalChargeTime": 100, "totalChargeQuantity": "high"}
               ], None

    # params.username
    # params.chargerID
    # params.turn: "on"|"off"
    def adminTurnCharger(self, params):
        return True, None

    # params.username
    # params.chargerID
    def adminGetCars(self, params):
        return [
                   {"username": "walker", "chargeQuantity": "high", "waitTime": 1234}
               ], None

    # params.username
    def adminGetTable(self, params):
        return {
                   "time": 1234, "chargerID": 1, "totalChargeCount": 10, "totalChargeTime": 100,
                   "totalChargeQuantity": "high", "totalChargeCost": 100, "totalServiceCost": 100,
                   "totalCost": 100
               }, None
