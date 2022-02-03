import SaniTrendCloud
import sqlite3

db = sqlite3.connect('STC.db')
cur = db.cursor()

cur.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='sanitrend' ''')
if cur.fetchone()[0] == 0:
    cur.execute(''' CREATE TABLE sanitrend (data text, twx integer) ''')
else:
    print('exits')
db.commit()
db.close