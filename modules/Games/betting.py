from Shinobu.utility import ConfigManager
import Shinobu.database
import pymysql.cursors

def set_db_mod(module):
    global db
    db = module

db = None # type: Shinobu.database

def assure_tables():
    db.assure_table("Accounts", (
        "UserID BIGINT UNSIGNED",
        "Name VARCHAR(64)",
        "Balance DOUBLE",
        "Frozen BOOLEAN DEFAULT FALSE",
        "PRIMARY KEY(UserID)"
    ,))

    db.assure_table("Transactions", (
        "TransactionID SERIAL",
        "Time DATETIME DEFAULT CURRENT_TIMESTAMP",
        "DebitID BIGINT UNSIGNED",
        "CreditID BIGINT UNSIGNED",
        "Amount DOUBLE NOT NULL",
        "Reason VARCHAR(128)",
        "FOREIGN KEY(DebitID) REFERENCES Accounts(UserID)",
        "FOREIGN KEY(CreditID) REFERENCES Accounts(UserID)"
    ,))



def get_account(user_id):
    sql = "SELECT * FROM Accounts WHERE UserID=%s"
    results = db.execute(sql, (user_id), show_errors=True)
    if results:
        return results.fetchone()
    else:
        return None

def save_account(account:dict):
    pass

def execute_transaction(from_id, to_id, amount):
    cursor = db.db.cursor() #type: pymysql.cursors.Cursor
    sql = "SELECT (Balance - %s) >= 0 as CanTransfer FROM Accounts WHERE UserID = %s"
    cursor.execute(sql, (amount, from_id))
    results = cursor.fetchone()
    if results and results['CanTransfer']:
        try:
            sql = "UPDATE Accounts SET Balance = (Balance - %s) WHERE UserID = %s"
            cursor.execute(sql, (amount, from_id))
            sql = "UPDATE Accounts SET Balance = (Balance + %s) WHERE UserID = %s"
            cursor.execute(sql, (amount, to_id))
            db.db.commit()
            return True
        except:
            return False
    else:
        print(results)
        return False


def add_account(user_id, name, balance):
    sql = "INSERT INTO Accounts (UserID, Name, Balance) VALUES (%s, %s, %s)"
    db.execute(sql, (user_id, name, balance), show_errors=True)
    return get_account(user_id)

def add_transaction_record(from_user, to_user, amount, reason=None):
    sql = "INSERT INTO Transactions (DebitID, CreditID, Amount, Reason) VALUES (%s,%s,%s,%s)"
    db.execute(sql, (from_user, to_user, amount, reason,), show_errors=True)



def transaction(from_id, to_id, amount, reason=None):
    if execute_transaction(from_id, to_id, amount):
        add_transaction_record(from_id, to_id, amount, reason)
        return True
    else:
        return False

def fetch_top_balances(num):
    sql = "SELECT UserID, Balance " \
          "FROM Accounts " \
          "WHERE UserID > 3 " \
          "ORDER BY Balance DESC"
    cursor = db.execute(sql, show_errors=True)
    return cursor.fetchall()


