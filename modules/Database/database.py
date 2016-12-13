import pymysql.cursors

class ShinobuDatabase:
    def __init__(self, host="localhost", user='default', db='db', password='', auto_connect = True):
        self.connection = None #type: pymysql.Connection
        self.host = host
        self.user = user
        self.db = db
        self.password = password
        if auto_connect:
            self.connect()


    def get_user(self, id=None, name=None):

        if id:
            return self.execute("SELECT * FROM Users WHERE UserID = %s", (id), fetch="one")
        if name:
            return self.execute("SELECT * FROM Users WHERE UserName = %s", ("Bob"), fetch="all")


    def set_user(self, id, name, groupid=3):
        sql = "INSERT INTO Users (UserID, UserName, GroupID) VALUES(%s,%s,%s)"
        params = (id, name, groupid)
        self.execute(sql, params)

    def connect(self):
        self.connection = pymysql.connect(host=self.host,
                                          user=self.user,
                                          password=self.password,
                                          db=self.db,
                                          charset='utf8mb4',
                                          cursorclass=pymysql.cursors.DictCursor)

    def close(self):
        self.connection.close()

    def execute(self, sql, params:tuple, fetch=None):
        with self.connection.cursor() as cursor:    #type: pymysql.cursors.DictCursor
            try:
                cursor.execute(sql, params)
                self.connection.commit()
                if fetch:
                    return cursor.__getattribute__("fetch" + fetch)()
                return True
            except Exception as e:
                print(e)
                return False

class ConfigSynchronizer:
    def __init__(self, token):
        pass

