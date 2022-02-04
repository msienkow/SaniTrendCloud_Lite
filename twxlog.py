import sqlite3
import json
import os
import time


DEFAULT_PATH = os.path.join(os.path.dirname(__file__), 'stc.db')
start = time.perf_counter()
with sqlite3.connect(database=DEFAULT_PATH) as db:
    cur = db.cursor()
    insert_query = ''' INSERT INTO sanitrend (data, twx) VALUES (?,?); '''
    records = []
    sql_as_text = ''

    cur.execute(''' CREATE TABLE if not exists sanitrend (data text, twx integer) ''')
    for i in range(1000):
        text = {'time': 1642189820904, 'quality': 'GOOD', 'name': 'Inches', 'value': {'value': 0.0, 'baseType': 'NUMBER'}}, {'time': 1642189820904, 'quality': 'GOOD', 'name': 'Volts', 'value': {'value': 1.06, 'baseType': 'NUMBER'}}, {'time': 1642189820904, 'quality': 'GOOD', 'name': 'Test_Analog_Real', 'value': {'value': 435.0, 'baseType': 'NUMBER'}}, {'time': 1642189820904, 'quality': 'GOOD', 'name': '_IO_EM_AI_01', 'value': {'value': 434, 'baseType': 'NUMBER'}}
        sql_as_text = json.dumps(text)
        records.append((sql_as_text, False))

    cur.executemany(insert_query, records)
    db.commit()

    query = '''select ROWID,data,twx from sanitrend where twx = false LIMIT 128'''
    cur.execute(query)
    records2 = cur.fetchall()
    sql = ''' DELETE FROM sanitrend where ROWID=? '''
    
    for row in records2:
        # test_recs = json.loads(row[1])
        # print(test_recs)
        id = row[0];
        cur.execute(sql, (id,))
    db.commit()

end = time.perf_counter()
totaltime = end - start
print(f'Total Time: {totaltime} seconds')
