import sqlite3
import os

dbname = "Subscribers.db"

with open(F"{dbname[:-3]}.txt", "w", encoding='utf-8') as sy:sy.close()
os.rename(F"{dbname[:-3]}.txt", dbname)

connection = sqlite3.connect(dbname, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
cursor = connection.cursor()

createUserTable='''
CREATE TABLE IF NOT EXISTS
Users(ID INTEGER PRIMARY KEY,
Username TEXT,
Name TEXT)
'''
cursor.execute(createUserTable)

createTempUserTable='''
CREATE TABLE IF NOT EXISTS
TempUsers(IDGID TEXT PRIMARY KEY,
ID INTEGER,
Username TEXT,
Name TEXT,
Plan INTEGER,
Amount REAL DEFAULT 0.0,
GID INTEGER,
MsgID INTEGER)
'''
cursor.execute(createTempUserTable)

createSubsTable='''
CREATE TABLE IF NOT EXISTS
Subs(PID INTEGER PRIMARY KEY,
SID INTEGER,
GID INTEGER,
Plan INTEGER,
Remaining INTEGER,
Amount REAL,
GroupName TEXT,
Status DEFAULT 'Active',
StartDate TEXT,
EndDate TEXT,
Kicked INTEGER DEFAULT 0)
'''
cursor.execute(createSubsTable)

createBroadcastTable='''
CREATE TABLE IF NOT EXISTS
Broadcast(UserID INTEGER PRIMARY KEY)
'''
cursor.execute(createBroadcastTable)