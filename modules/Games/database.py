from connector_db.highlevel import Record

class Account(Record):
    def __init__(self, user_id):
        select_sql = "SELECT * FROM Accounts WHERE UserID={}".format(user_id)
        update_sql = "UPDATE Accounts SET {} WHERE UserID={}".format("{}",user_id)
        super(Account, self).__init__(select=select_sql, update=update_sql)

