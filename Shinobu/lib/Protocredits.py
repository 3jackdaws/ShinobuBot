import Shinobu.database as db
db = None

def setdb(database):
    global db
    db = database

def get_account(user_id):
    sql = "SELECT * FROM Accounts WHERE UserID=%s"
    results = db.execute(sql, (user_id), show_errors=True)
    if results:
        return results.fetchone()
    else:
        return None

def transaction(from_id, to_id, amount):
    

