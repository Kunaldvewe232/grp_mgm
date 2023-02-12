from pyrogram import Client, filters
import BotConfig
import os
from Sqlite import Exec
from tabulate import tabulate
from asyncio import sleep as asleep
import requests
import json


'''===========EDITABLES==========='''

preFix = BotConfig.PREFIX
OWNER = filters.user(BotConfig.OWNER_ID)

'''-------------------------------'''

command = lambda cmd: filters.command(cmd, prefixes = preFix)

def DelFiles(files_to_del: list):
  for x in files_to_del:
    if os.path.exists(x):
      os.remove(x)


# /help
@Client.on_message(OWNER & filters.private & command(["help", F"help{BotConfig.BOT_UNAME}"]))
async def Help(_, msg):
  await msg.reply(BotConfig.HELP, quote=1)
#*---------------------------------------------------------------------


# /total
@Client.on_message(OWNER & filters.private & command(["total", F"total{BotConfig.BOT_UNAME}"]))
async def TotalS(_, msg):
    totalUsers = Exec("select count(*) from Users")[0][0]
    await msg.reply(F"Total subscribers: {totalUsers}", quote=1)
#*---------------------------------------------------------------------


# /user UserID
# /user Username
@Client.on_message(OWNER & filters.private & command(["user", F"user{BotConfig.BOT_UNAME}"]))
async def User(_, msg):
  HELP = F"""{preFix}user 1234567890
{preFix}user @username"""
  try:
      if len(msg.text.split())>1:
        targetUser = msg.text.partition(msg.text.split()[0])[-1].strip()
        if Exec(F"select count(*) from Users where {'ID=' if targetUser.isdigit() else 'Username like '}'{targetUser}'")[0][0]:
          ID, Username, Name = Exec(F"select * from Users where {'ID=' if targetUser.isdigit() else 'Username like'}'{targetUser}'")[0]
          Subs = Exec(F"select count(*) from Subs where SID='{ID}'")[0][0]
          Active = Exec(F"select count(*) from Subs where SID='{ID}' and Kicked='0'")[0][0]
          Expired = Exec(F"select count(*) from Subs where SID='{ID}' and Kicked='1'")[0][0]
        
        conn = sqlite3.connect("Subscribers.db", detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        db_df = pd.read_sql_query(F"select PID, Plan, Remaining, Amount, GroupName, StartDate, EndDate, Status from Subs where SID='{ID}'", conn)
        with open('User.csv', 'a') as file:
          file.write('SubscriptionID,Plan,Remaining,Amount,GroupName,StartDate,EndDate,Status\n')
          db_df.to_csv(file, header=False, index=False)
        await msg.reply_document(document = "User.csv", caption=F"ID: `{ID}`\nName: {Name}\nUsername: {Username if Username else '`NULL`'}\nSubscriptions owned: {Subs}\nActive: {Active}\nExpired: {Expired}", quote=1)
        DelFiles(["User.csv"])
        
      else: raise Exception
  except Exception as e: return await msg.reply((F"--**Error:**--\n{e}\n\n" if len(str(e)) else "") + F"--**Usage**--\n`{HELP}`", quote=1)
#*---------------------------------------------------------------------


# /users
@Client.on_message(OWNER & filters.private & command(["users", F"users{BotConfig.BOT_UNAME}"]))
async def Users(_, msg):
  try:
    conn = sqlite3.connect("Subscribers.db", detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    db_df = pd.read_sql_query("select * from (select ID, Name, Username, count(PID) from Users inner join Subs ON SID = ID group by ID)", conn)
    with open('Users.csv', 'a') as file:
      file.write('ID,Name,Username,Subscriptions\n')
      db_df.to_csv(file, header=False, index=False)
    await msg.reply_document(document = "Users.csv", quote=1)
    DelFiles(["Users.csv"])
  except Exception as e: return await msg.reply(F"--**Error:**--\n{e}", quote=1)
#*---------------------------------------------------------------------


# /subs
@Client.on_message(OWNER & filters.private & command(["subs", F"subs{BotConfig.BOT_UNAME}"]))
async def Subs(app, msg):
  try:
    conn = sqlite3.connect("Subscribers.db", detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    db_df = pd.read_sql_query("select PID, SID, Name, Username, Plan, Remaining, Amount, GroupName, StartDate, EndDate, Status from Users, Subs where Users.ID=Subs.SID", conn)
    with open('Subscriptions.csv', 'a') as file:
      file.write('SubscriptionID,UserID,Name,Username,Plan,Remaining,Amount,GroupName,StartDate,EndDate,Status\n')
      db_df.to_csv(file, header=False, index=False)
    await msg.reply_document(document = "Subscriptions.csv", quote=1)
    DelFiles(["Subscriptions.csv"])
  except Exception as e: return await msg.reply(F"--**Error:**--\n{e}", quote=1)
#*---------------------------------------------------------------------


# /broadcast <- Reply to a message
@Client.on_message(OWNER & filters.private & command(["broadcast", F"broadcast{BotConfig.BOT_UNAME}"]))
async def Broadcast(app, msg):
  if msg.reply_to_message:
    total, success, failed = (0,)*3
    msgObj = msg.reply_to_message
    users = Exec("select UserID from Broadcast")
    await msg.reply(F"Broadcasting your message to {len(users)} users...", quote=1)
    for count, user in enumerate(users, 1):
      total=count
      r=requests.get(F"https://api.telegram.org/bot{BotConfig.BOT_TOKEN}/copyMessage?chat_id={user[0]}&from_chat_id={msgObj.chat.id}&message_id={msgObj.id}")
      res=json.loads(r.content)
      if res.get("ok"): success+=1
      else: failed+=1
      if count%20==0: await asleep(10)
    await msg.reply(F"Tried broadcasting to {total} users.\nSuccess: {success} users\nFailed: {failed} users", quote=1)
  else: await msg.reply("You need to **reply to a message** with `/broadcast` command.", quote=1)
#*---------------------------------------------------------------------


# /add
@Client.on_message(OWNER & filters.private & command(["add", F"add{BotConfig.BOT_UNAME}"]))
async def Add(_, msg):
  HELP = F"""{preFix}add ID
Full Name
Username (with @ symbol)
StartDate ({datetime.now().strftime('%d-%b-%Y')})
Plan (Number of days)
Amount
GroupID
GroupName"""
  try:
    if len(msg.text.split(maxsplit=1)[1].splitlines()):
      ID, Name, Username, StartDate, Plan, Amount, GID, GroupName = msg.text.split(maxsplit=1)[1].splitlines()
      Stardate = datetime.strptime(StartDate, '%d-%b-%Y')
      Endate = Stardate + timedelta(days=int(Plan))
      Todate = datetime.strptime(datetime.now().strftime('%d-%b-%Y'), '%d-%b-%Y')
      if Endate>=Todate:
        Status = "Active"
        Remaining = (Endate-Todate).days
      else:
        Status = "Expired"
        Remaining = 0
      EndDate = Endate.strftime('%d-%b-%Y')
      Kicked = 0
  
      ExecS(F"insert or replace into Users values('{ID}', '{Username}', '{Name}')")
      PID = Exec(F"""insert into Subs(SID, GID, Plan, Remaining, Amount, GroupName, Status, StartDate, EndDate, Kicked) values(
      '{ID}',
      '{GID}',
      '{Plan}',
      '{Remaining}',
      '{Amount}',
      '{GroupName}',
      '{Status}',
      '{StartDate}',
      '{EndDate}',
      '{Kicked}'
      ) returning PID""")[0][0]
      SaveDB()
  
      return await msg.reply(F"""
Records added successfully!
SubscriptionID: `{PID}`
UserID: `{ID}`
Name: {Name}
Username: {Username if Username else '`NULL`'}
Plan: {Plan} Days
Amount: ₹ {Amount}
From: {StartDate}
To: {EndDate}
Group: {GroupName}
""", quote=1)
    
    else: raise Exception
  except Exception as e: return await msg.reply((F"--**Error:**--\n{e}\n\n" if len(str(e)) else "") + F"--**Usage**--\n`{HELP}`", quote=1)
#*---------------------------------------------------------------------