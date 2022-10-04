import sqlite3

connection = sqlite3.connect('signals.db')
db = connection.cursor()
text = "final"
imgtitle = [(text)]
#db.execute('INSERT INTO org(name) VALUES (?)', text)
#connection.commit()



org_signal_list_db = db.execute("SELECT id, name FROM org")
org_signal_list =org_signal_list_db.fetchall()
print(org_signal_list[0][0])