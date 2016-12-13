from Database.database import ShinobuDatabase

db = ShinobuDatabase(host="isogen.net", user="shinobu", db="shinobu", password="rQz-du3-Qyq-qCH")


print(db.get_user(name="Bob"))