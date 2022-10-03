import sqlite3

connection = sqlite3.connect('signals.db')
db = connection.cursor()
text = "final"
imgtitle = [(text)]
#db.execute('INSERT INTO org(name) VALUES (?)', text)
#connection.commit()


max_id_db = db.execute("SELECT MAX(id) FROM org")
max_id = max_id_db.fetchone()[0]
imgcount = 0
if max_id != None:
    imgcount = max_id

print(imgcount)