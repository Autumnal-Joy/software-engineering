class DB:
    def __init__(self, path):
        pass

    def Query(self,tablename: str, key: str) -> dict:
        # 前端测试密码为: 123456, 此处是MD5加密
        if(tablename == 'user'):
            return {"username": "user", "password": "e10adc3949ba59abbe56e057f20f883e"}
        elif(tablename == 'user1'):
            return {"username": "user1", "password": "e10adc3949ba59abbe56e057f20f883e"}
        elif(tablename == 'user2'):
            return {"username": "user2", "password": "e10adc3949ba59abbe56e057f20f883e"}
        elif(tablename == 'user3'):
            return {"username": "user3", "password": "e10adc3949ba59abbe56e057f20f883e"}
        elif(tablename == 'user4'):
            return {"username": "user4", "password": "e10adc3949ba59abbe56e057f20f883e"}
    def Insert(self,tablename: str, key: str, val: dict) -> bool:
        return True

    def Delete(self,tablename: str, key: str) -> bool:
        return True

    def Update(self,tablename: str, key: str, val: dict) -> bool:
        return True
