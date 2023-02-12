from pyrogram import Client, filters
import BotConfig
import os
from Sqlite import Exec
from tabulate import tabulate


'''===========EDITABLES==========='''

preFix = BotConfig.PREFIX

'''-------------------------------'''

command = lambda cmd: filters.command(cmd, prefixes = preFix)

def DelFiles(files_to_del: list):
  for x in files_to_del:
    if os.path.exists(x):
      os.remove(x)


# /myinfo
@Client.on_message(filters.private & command(["myinfo", F"myinfo{BotConfig.BOT_UNAME}"]))
async def MyInfo(app, msg):
  ID = msg.from_user.id
  try:
    if Exec(F"select count(*) from Users where ID='{ID}'")[0][0]:
      Name, Username, Subs = Exec(F"select Name, Username, count(PID) from Users, Subs where ID='{ID}' and SID='{ID}'")[0]
      Active = Exec(F"select count(*) from Subs where SID='{ID}' and Kicked='0'")[0][0]
      Expired = Exec(F"select count(*) from Subs where SID='{ID}' and Kicked='1'")[0][0]
      data = [('SubscriptionID', 'Plan', 'Remaining', 'Amount', 'GroupName', 'StartDate', 'EndDate', 'Status')]
      data += Exec(F"select PID, Plan, Remaining, Amount, GroupName, StartDate, EndDate, Status from Users, Subs where ID='{ID}' and SID='{ID}'")
      with open("MyInfo.html","w", encoding='utf-8') as sy:
        sy.write("""<head><style>table,th,td{font-size:20px;border:solid white 1px;border-collapse:collapse;background:#111920;padding:2px;}body{font-family:'Consolas';background:#0B1016;color:white}td{text-align:center !important;vertical-align:middle !important;}</style></head><center>\n"""+F"{tabulate(data, headers='firstrow', tablefmt='html')}\n</center>")
        sy.close()
      await msg.reply_document(document = "MyInfo.html", caption=F"ID: `{ID}`\nName: {Name}\nUsername: {Username if Username else '`NULL`'}\nSubscriptions owned: {Subs}\nActive: {Active}\nExpired: {Expired}", quote=1)
      DelFiles(["MyInfo.html"])
    else: await msg.reply("No info found for you. Make sure to subscribe first.", quote=1)
  except Exception as e: return await msg.reply(F"--**Error:**--\n{e}", quote=1)
#*---------------------------------------------------------------------