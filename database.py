import sqlite3, csv
from pprint import pprint

sqlite_file = "database.db"
conn = sqlite3.connect(sqlite_file)
cur = conn.cursor()

# Populate nodes table
cur.execute('''DROP TABLE IF EXISTS nodes''')
conn.commit()
cur.execute('''CREATE TABLE nodes(id INTEGER PRIMARY KEY, lat REAL, lon REAL, user TEXT, uid INTEGER, version INTEGER, changeset INTEGER, timestamp DATETIME)''')
conn.commit()

with open('nodes.csv', 'rb') as fin:
    dr = csv.DictReader(fin)
    to_db = [(i['id'].decode('utf-8'), i['lat'].decode('utf-8'), i['lon'].decode('utf-8'), i['user'].decode('utf-8'), i['uid'].decode('utf-8'), 
              i['version'].decode('utf-8'), i['changeset'].decode('utf-8'), i['timestamp'].decode('utf-8')) for i in dr]

cur.executemany('INSERT INTO nodes(id, lat, lon, user, uid, version, changeset, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?);', to_db)
conn.commit()

# Populate nodes_tags table
cur.execute('''DROP TABLE IF EXISTS nodes_tags''')
conn.commit()
cur.execute('''CREATE TABLE nodes_tags(id INTEGER, key TEXT, value TEXT, type TEXT, FOREIGN KEY (id) REFERENCES nodes(id))''')
conn.commit()

with open('nodes_tags.csv', 'rb') as fin:
    dr = csv.DictReader(fin)
    to_db = [(i['id'].decode('utf-8'), i['key'].decode('utf-8'), i['value'].decode('utf-8'), i['type'].decode('utf-8')) for i in dr]

cur.executemany('INSERT INTO nodes_tags(id, key, value, type) VALUES (?, ?, ?, ?);', to_db)
conn.commit()

# Populate ways table
cur.execute('''DROP TABLE IF EXISTS ways''')
conn.commit()
cur.execute('''CREATE TABLE ways(id INTEGER PRIMARY KEY, user TEXT, uid INTEGER, version INTEGER, changeset INTEGER, timestamp DATETIME)''')
conn.commit()

with open('ways.csv', 'rb') as fin:
    dr = csv.DictReader(fin)
    to_db = [(i['id'].decode('utf-8'), i['user'].decode('utf-8'), i['uid'].decode('utf-8'), i['version'].decode('utf-8'), i['changeset'].decode('utf-8'), 
              i['timestamp'].decode('utf-8')) for i in dr]

cur.executemany('INSERT INTO ways(id, user, uid, version, changeset, timestamp) VALUES (?, ?, ?, ?, ?, ?);', to_db)
conn.commit()

# Populate waysnodes table
cur.execute('''DROP TABLE IF EXISTS waysnodes''')
conn.commit()
cur.execute('''CREATE TABLE waysnodes(id INTEGER, node_id INTEGER, position INTEGER, FOREIGN KEY(id) REFERENCES nodes(id))''')
conn.commit()

with open('ways_nodes.csv', 'rb') as fin:
    dr = csv.DictReader(fin)
    to_db = [(i['id'].decode('utf-8'), i['node_id'].decode('utf-8'), i['position'].decode('utf-8')) for i in dr]

cur.executemany('INSERT INTO waysnodes(id, node_id, position) VALUES (?, ?, ?);', to_db)
conn.commit()

# Populate waystags table
cur.execute('''DROP TABLE IF EXISTS waystags''')
conn.commit()
cur.execute('''CREATE TABLE waystags(id INTEGER, key TEXT, value TEXT, type TEXT, FOREIGN KEY(id) REFERENCES ways(id))''')
conn.commit()

with open('ways_tags.csv', 'rb') as fin:
    dr = csv.DictReader(fin)
    to_db = [(i['id'].decode('utf-8'), i['key'].decode('utf-8'), i['value'].decode('utf-8'), i['type'].decode('utf-8')) for i in dr]

cur.executemany('INSERT INTO waystags(id, key, value, type) VALUES (?, ?, ?, ?);', to_db)
conn.commit()

conn.close()

