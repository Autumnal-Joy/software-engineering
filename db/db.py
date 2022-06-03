class DB:
    def __init__(self, path):
        pass

    def Query(self,tablename: str, key: str) -> dict:
        # 前端测试密码为: 123456, 此处是MD5加密
        return {"username": "user", "password": "e10adc3949ba59abbe56e057f20f883e"}

    def Insert(self,tablename: str, key: str, val: dict) -> bool:
        return True

    def Delete(self,tablename: str, key: str) -> bool:
        return True

    def Update(self,tablename: str, key: str, val: dict) -> bool:
        return True
