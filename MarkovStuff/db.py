import psycopg2
import Parser as parser


def buildDatabase(conn):
    cur = conn.cursor()
    cur.execute('create table if not exists records (\
id serial PRIMARY KEY,\
recordId text,\
rawtext text,\
body text);')

    cur.execute('create table if not exists tagsets (\
id serial PRIMARY KEY,\
name text);')

    cur.execute('create table if not exists tags (\
id serial PRIMARY KEY,\
set_id SERIAL REFERENCES tagsets,\
value text);')

    cur.execute('create table if not exists tagindex (\
id serial PRIMARY KEY,\
tag_id SERIAL REFERENCES tags,\
record_id SERIAL REFERENCES records,\
index int);')

    cur.execute('create table if not exists markovNode (\
id serial PRIMARY KEY,\
set_id SERIAL REFERENCES tagsets,\
value text);')

    conn.commit()

def tearDown(conn):
    cur = conn.cursor()
    cur.execute('DROP TABLE tagindex;')
    conn.commit()

    cur.execute('DROP TABLE markovNode;')
    conn.commit()

    cur.execute('DROP TABLE tags;')
    conn.commit()

    cur.execute('DROP TABLE tagsets;')
    conn.commit()

def clearData(conn):
    cur = conn.cursor()
    cur.execute('DELETE FROM records;')
    conn.commit()

def getConnection():
    #return psycopg2.connect(database="sampledata", user="myuser", password="secret")
    return psycopg2.connect(database="pathology", user="myuser", password="secret")

def saveDataToDB(conn,data):
    cur = conn.cursor()
    l = len(data.rows)
    i = 0
    while i < l:
        j = min(i+100,l)
        args_str = ','.join([cur.mogrify("(%s,%s)",[x.data[-1],x.mainData]).decode() for x in data.rows[i:j]])
        cur.execute("INSERT INTO records (rawtext,body) VALUES " + args_str)
        conn.commit()
        i = j

def loadDataFromDB(conn,query=None,orderBy=None,limit=None):
    res = parser.DataSet()
    cur = conn.cursor()
    sql = 'SELECT body FROM records'
    if query != None:
        sql += " WHERE " + query
    if orderBy != None:
        sql += ' ORDER BY ' + orderBy
    if limit != None:
        sql += ' LIMIT ' + str(limit)
    cur.execute(sql + ';')
    row = cur.fetchone()
    while row:
        r = parser.DataRow()
        r.setData(list(row))
        res.addRow(r)
        row = cur.fetchone()
    return res

def loadMarkoveModel(conn):
    pass

def makeSampleData():
    conn = getConnection()
    clearData(conn)
    d = parser.dummyDataSet(4,100000,
                        ['Test1','Sample Test','The other test','Hidden test 2','Hidden IGG'],
                        ['POSITVE','Non Negative','NA','Example','Mostky ok','NEGATIVE'])
    
    print('load ok')
    saveDataToDB(conn,d)

#conn = getConnection()

#clearData(conn)

#d = parser.dummyDataSet(4,100000,['Test1','Sample Test','The other test','Hidden test 2','Hidden IGG'],['POSITVE','Non Negative','NA','Example','Mostky ok','NEGATIVE'])
    
#print('load ok')
#d = parser.loadFile('small.csv',(lambda x:x.formatRow()))

#r = loadDataFromDB(conn,query="id > 600000",limit=100000)

#saveDataToDB(conn,d)

