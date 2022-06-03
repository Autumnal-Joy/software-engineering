class DB:
    def __init__(self, path):
        pass

    def Query(self,tablename: str, key: str) -> dict:
        return {"username": "郭阳", "password": "123456"}

    def Insert(self,tablename: str, key: str, val: dict) -> bool:
        return True

    def Delete(self,tablename: str, key: str) -> bool:
        return True

    def Update(self,tablename: str, key: str, val: dict) -> bool:
        return True
