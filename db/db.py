from ast import main
import os, json
'''
2022/06/15: 董文阔

    实现了一个DB，并赋予以下功能。
    
    Query, Insert, Update, Del，
    


'''

class DB:

    # 构造函数传入一个路径，代表数据文件存放的位置
    def __init__(self, path=None):
        self.path = path
        self.buf = None
        self.table = None


    # 读取文件的方法，如果没有该文件，则创建，并加载json到内存中去
    def Read(self, table):
        self.table = table
        file = ""

        if self.path == None:
            file = table + '.json'
        else:
            file = os.path.join(self.path, table + ".json")

        if os.path.exists(file):
            j = open(file, 'r').read()
        else:
            open(file, 'w')
            j = ""

        if len(j) == 0:
            self.buf = dict()
        else:
            self.buf = json.loads(j)

    # 写回到数据文件中
    def Commit(self):
        if self.table == None:
            print('fatal error! write table is empty')
        if (self.path == None):
            json.dump(self.buf, open(self.table + '.json', 'w'))
        else:
            json.dump(self.buf, open(os.path.join(self.path, self.table + ".json"), "w"))
        self.buf = None
        self.table = None

    # 每次调用接口之前都要将数据装配到内存中去
    def Load(self, table):
        if self.table is None:
            self.Read(table)
        elif self.table != table:
            self.Commit()
            self.Read(table)

    def Query(self, tablename, key) -> dict:
        self.Load(tablename)
        if key in self.buf.keys():
            return self.buf[key]
        return dict()

    def Insert(self, tablename, key, value) -> bool:
        self.Load(tablename)
        if key in self.buf.keys():
            return False
        self.buf[key] = value
        return True

    def Del(self, tablename, key) -> bool:
        self.Load(tablename)
        if key in self.buf.keys():
            del self.buf[key]
            return True
        else:
            return False

    def Update(self, tablename, key, value) -> bool:
        self.Load(tablename)
        # if key in self.buf.keys():
        self.buf[key] = value
        return True
        # else:
        #     return False



'''

接口是之前说好的，Insert，Del，Update，Query
然后这里我有一个地方需要说一下，
1. 不同的表存放在不同的json文件，并存放在同一个文件夹里，默认就应该是当前文件夹，具体位置在构造函数初始化
2. 我这个设计是设计了一个表缓冲区，你如果一直访问同一个表，
   那这个表会一直在内存中，如果你换了一个表，那这个缓冲区就会开始发生置换，
   之后可以多设计几个缓冲，来做类似于LRU那种缓冲算法。
3. 你不需要自己创建这些文件，如果找不到某一个表他会自己创建一个

'''
