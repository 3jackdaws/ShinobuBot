import pymysql.cursors
import json

__all__ = [
    "execute","dbopen", "dbclose", "assure_table", "create_insert",
    "create_delete", "create_select", "create_update", "Record",
    "DatabaseDict"
]


db = None # type: pymysql.Connection

def execute(sql, params=None, show_errors=False, auto_commit=True, cursor=None):
    try:
        if not cursor:
            cursor = db.cursor()
        cursor.execute(sql, params)
        if auto_commit:
            db.commit()
        return cursor
    except Exception as e:
        if show_errors:
            print(e, sql)
        return False

def dbclose():
    db.close()

def dbset(database):
    global db
    db = database

def dbopen(host, database, user, password):
    global db
    if password:
        db = pymysql.Connect(host=host,
                     db=database,
                     user=user,
                     password=password,
                     charset='utf8mb4',
                     cursorclass=pymysql.cursors.DictCursor)

        assure_table("KVStore", (
            "KVGroup VARCHAR(32)",
            "KVKey VARCHAR(32)",
            "KVVal VARCHAR(2048)",
            "PRIMARY KEY(KVGroup ,KVKey)"
        ))
    else:
        db.connect()


def assure_table(table_name, columns:tuple):
    if not execute("SELECT 1 FROM {} LIMIT 1".format(table_name)):
        print("CREATING {}".format(table_name))
        sql = "CREATE TABLE {}(\n".format(table_name)
        for column in columns:
            sql+= " " + column + ","
        sql = sql[:-1] + ")"
        execute(sql, None, show_errors=True)

def create_insert(table_name, **kwargs):
    num_args = len(kwargs)
    print(num_args)
    param_str = ""
    for i in range(num_args):
        param_str += "{}, "
    param_str = param_str[:-2]
    sql = "INSERT INTO {} ({}) VALUES({})".format(table_name, param_str, param_str)
    # sql = sql.format()
    columns = []
    values = []
    for key in kwargs:
        columns.append(key)
        values.append(kwargs[key] if not isinstance(kwargs[key], str) else "'" + kwargs[key] + "'")
    return sql.format(*columns, *values)

def create_delete(table_name, where):
    return "DELETE FROM {} WHERE {}".format(table_name, where)

def create_select(table_name, columns="*", where=None, fetch_type="all"):
    num_cols = len(columns)
    cols = ""
    if columns == "*":
        cols = "*"
    else:
        cols = "("
        for col in columns:
            cols += " " + col + ","
        cols = cols[:-1] + ")"
    sql = "SELECT {} FROM {}".format(cols, table_name)
    if where:
        sql += " WHERE {}".format(where)
    return sql

def create_update(table_name, where, **kwargs):
    #UPDATE TABLENAME SET COL=VAL, COL2=VAL2 WHERE 1=1
    sql = "UPDATE {} SET ".format(table_name)
    for key in kwargs:
        sql += "{}='{}',".format(key, str(kwargs[key]))

    sql = (sql[:-1] + " WHERE {}").format(where)
    return sql

class Record:
    def __init__(self, select=None, update=None):
        self._update_query = update
        self._select_query = select
        # self._delete_query = delete
        # self._insert_query = insert
        self._values = self._fetch() # type: dict
        print(self._values)
        if self._values == None:
            raise Exception("UserID not found")

    def _fetch(self):
        results = execute(self._select_query, show_errors=True)
        return results.fetchone()

    def update(self):
        values = [str(x) + "='" + str(self._values[x]) + "'" for x in self._values]
        updates = ",".join(values)
        sql = self._update_query.format(updates)
        execute(sql)
        db.commit()

    def __str__(self):
        return str(self._values)

    def __iter__(self):
        return iter(self._values)

    def __getitem__(self, item):
        return self._values[item]

    def __setitem__(self, key, value):
        self._values[key] = value
class DatabaseDict(dict):
    def __init__(self, group):
        self._group = group
        kvdict = self.fetch()
        super(DatabaseDict, self).__init__(*[{x["KVKey"]:json.loads(x["KVVal"]) for x in kvdict}])
        self.itemlist = super(DatabaseDict, self).keys()
        self._del_cache = []

    def fetch(self):
        sql = "SELECT KVKey, KVVal FROM KVStore WHERE KVGroup=%s"
        cursor = execute(sql, (self._group), show_errors=True)
        if cursor:
            return cursor.fetchall()
        else:
            return {}

    def commit(self):
        sql = "INSERT INTO KVStore (KVGroup, KVKey, KVVal) " \
              "VALUES (%s,%s,%s) " \
              "ON DUPLICATE KEY UPDATE " \
              "KVVal=%s"
        for key in self:
            value = json.dumps(self[key])
            execute(sql, (self._group, key, value, value),show_errors=True, auto_commit=False)
        for stmt in self._del_cache:
            execute(stmt, show_errors=True, auto_commit=False)
        db.commit()

    def __delitem__(self, key):
        super(DatabaseDict, self).__delitem__(key)
        self._del_cache.append("DELETE FROM KVStore WHERE KVGroup='{}' AND KVKey='{}'".format(self._group, key))
