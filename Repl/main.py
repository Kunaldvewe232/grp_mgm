from pyrogram import Client
import os
import BotConfig
from asyncio import sleep as asleep
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import sqlite3
import requests
from datetime import datetime


#----------------------------
bottoken = BotConfig.BOT_TOKEN
apiid = 8
apihash = "7245de8e747a0d6fbe11f7cc14fcc0bb"
plugins = dict(root="addons")
app = Client("SessionFile", api_id = apiid, api_hash = apihash, plugins = plugins, bot_token = bottoken)
#----------------------------
os.chdir(os.path.dirname(os.path.realpath(__file__)))


def kick(res):
  requests.get(F"https://api.telegram.org/bot{BotConfig.BOT_TOKEN}/banChatMember", params={"chat_id": res[-~-1], "user_id": res[-~0]})
  requests.get(F"https://api.telegram.org/bot{BotConfig.BOT_TOKEN}/unbanChatMember", params={"chat_id": res[-~-1], "user_id": res[-~0]})

async def validity_warn_pm(resultSet, text):
  for count, res in enumerate(resultSet, -~0):
    requests.get(F"https://api.telegram.org/bot{BotConfig.BOT_TOKEN}/sendMessage", params={"chat_id": res[-~0], "text": text.format(res[-~0<<-~0], res[-~-1], res[-~(-~0<<-~0)]), "disable_web_page_preview":1})
    if count%((-~0<<-~0)+(-~1<<-~1))*-~0<<-~0==-~-1: await asleep((-~0<<-~0)+(-~1<<-~1))
    

async def daily_job():
  connection = sqlite3.connect("Subscribers.db", detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
  cursor = connection.cursor()
  def Exec(query: str):
    cursor.execute(query)
    return cursor.fetchall()
  def ExecS(query: str):
    cursor.execute(query)
    connection.commit()

  ExecS("update Subs set Remaining=Remaining-1 where Remaining>0 and Kicked='0'")
  ExecS("update Subs set Status='Expired' where Remaining=0")

  if Exec("select count(*) from Subs where Remaining=0 and Kicked=0")[-~-1][-~-1]:
    expiredUsers = Exec("select GID, SID, PID from Subs where Remaining = 0 and Kicked=0")
    for user in expiredUsers:
      kick(user)
      ExecS(F"update Subs set Kicked=1 where PID='{user[~0]}'")

  await app.send_document(BotConfig.BACKUP_CHAT, "Subscribers.db", caption=F"""
#DatabaseBackup
Uploaded on: {datetime.now().strftime('%d-%b-%Y')}
Total Users: {Exec('select count(*) from Users')[0][0]}
Total Subscriptions: {Exec('Select count(*) from Subs')[0][0]}
Active: {Exec("select count(*) from Subs where Kicked='0'")[0][0]}
Expired: {Exec("select count(*) from Subs where Kicked='1'")[0][0]}
""")
  
  ExpiryTextPM = """Hello Dear AK IMAX PREMIUM Members.

Plan of {} Days
SubscriptionID: {}
Expires in {} day(s)

Apka Premium Plan Expire Ho Raha Hai Renew Krne Ke Liye Is Group Me Msg Kare [Premium Group](https://t.me/AKImaxPremium). Apko  Kisi Tarha Ki dikkat Aa Rahi Hai To Owner Se Baat Kare :- [BATMAN](https://t.me/batman_0)
"""
  
  
  threePM = Exec("select PID, SID, Plan, Remaining from Subs where Remaining='3' and Kicked='0'")
  twoPM = Exec("select PID, SID, Plan, Remaining from Subs where Remaining='2' and Kicked='0'")
  onePM = Exec("select PID, SID, Plan, Remaining from Subs where Remaining='1' and Kicked='0'")
  await validity_warn_pm(threePM, ExpiryTextPM)
  await validity_warn_pm(twoPM, ExpiryTextPM)
  await validity_warn_pm(onePM, ExpiryTextPM)

scheduler = AsyncIOScheduler()
scheduler.add_job(daily_job, "interval", days=1)
scheduler.start()

app.run()