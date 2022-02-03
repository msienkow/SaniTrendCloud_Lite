import sqlite3
import os
import time


DEFAULT_PATH = os.path.join(os.path.dirname(__file__), 'STC.db')
start = time.perf_counter()
with sqlite3.connect(database=DEFAULT_PATH) as db:
    cur = db.cursor()
    insert_query = ''' INSERT INTO sanitrend (data, twx) VALUES (?,?); '''
    records = []


    # cur.execute(''' CREATE TABLE if not exists sanitrend (data text, twx integer) ''')
    # for i in range(1000000):
    #     text = f'Test {i + 1}'
    #     records.append((text, False))

    # cur.executemany(insert_query, records)
    # db.commit()

    query = '''select ROWID,data,twx from sanitrend where twx = false'''
    cur.execute(query)
    records2 = cur.fetchall()
    sql = ''' DELETE FROM sanitrend where ROWID=? '''
    for row in records2:
        print(row)
        id = row[0];
        cur.execute(sql, (id,))
    db.commit()

end = time.perf_counter()
totaltime = end - start
print(f'Total Time: {totaltime} seconds')
