from Shinobu.utility import ConfigManager
from .database import Account

def set_db_mod(module):
    global db
    db = module

db = None

def assure_tables():
    print("Assure Table")
    print(db.assure_table)
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



def add_account(user_id, name, balance):
    sql = "INSERT INTO Accounts (UserID, Name, Balance) VALUES (%s, %s, %s)"
    db.execute(sql, (user_id, name, balance), show_errors=True)
    return Account(user_id)

def add_transaction_record(from_user, to_user, amount, reason=None):
    sql = "INSERT INTO Transactions (DebitID, CreditID, Amount, Reason) VALUES (%s,%s,%s,%s)"
    db.execute(sql, (from_user, to_user, amount, reason,), show_errors=True)

def transaction(from_id, to_id, amount, reason=None):
    if amount < 0:
        return False
    from_record = Account(from_id)
    to_record = Account(to_id)
    if from_record["Balance"] - amount > 0:
        from_record["Balance"] -= amount
        to_record["Balance"] += amount
        from_record.update()
        to_record.update()
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


