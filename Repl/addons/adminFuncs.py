from pyrogram import Client, filters, enums
import BotConfig
import os
from Sqlite import Exec, ExecS, SaveDB
from datetime import datetime, timedelta


'''===========EDITABLES==========='''

preFix = BotConfig.PREFIX
GROUPS = filters.chat(BotConfig.ALLOWED_GROUPS)

'''-------------------------------'''

command = lambda cmd: filters.command(cmd, prefixes = preFix)

def DelFiles(files_to_del: list):
  for x in files_to_del:
    if os.path.exists(x):
      os.remove(x)


# /confirm UniqueID AMOUNT [DAYS]
@Client.on_message(GROUPS & command(["confirm", F"confirm{BotConfig.BOT_UNAME}"]))
async def Confirm(app, msg):
  HELP = F"{preFix}confirm UniqueID AMOUNT [DAYS]"
  sender = await app.get_chat_member(msg.chat.id, msg.from_user.id)
  Plan = False
  try:
    if sender.status in [enums.ChatMemberStatus.OWNER, enums.ChatMemberStatus.ADMINISTRATOR]:
      if len(msg.text.split())>1:
        args = msg.text.split(maxsplit=1)[~0]
        args = args.split()
        if 2<=len(args)<=3:
          if len(args)==2:
            IDGID, Amount = args
          elif len(args)==3:
            IDGID, Amount, Plan = args
          if int(Amount)<0: raise Exception ("Only positive values are allowed for amount")
          userExist = Exec(F"select count(*) from TempUsers where IDGID='{IDGID}'")[0][0]
          if userExist:
            if not Plan: Plan = Exec(F"select Plan from TempUsers where IDGID='{IDGID}'")[0][0]
            if int(Plan)<1: raise Exception ("Only non-zero positive number of days are allowed as values for subscription plans")
            SID, GID, MsgID = Exec(F"select ID, GID, MsgID from TempUsers where IDGID='{IDGID}'")[0]
            Remaining = Plan
            GroupName = msg.chat.title
            dt = datetime.now()
            StartDate, EndDate = dt.strftime('%d-%b-%Y'), (dt + timedelta(days=int(Plan))).strftime('%d-%b-%Y')
  
            ExecS(F"update TempUsers set Amount='{Amount}', Plan='{Plan}' where IDGID='{IDGID}'")
            ExecS(F"insert or replace into Users(ID, Username, Name) select ID, Username, Name from TempUsers where IDGID='{IDGID}'")
            PID = Exec(F"""insert into Subs(SID, GID, Plan, Remaining, Amount, GroupName, StartDate, EndDate) values(
            '{SID}',
            '{GID}',
            '{Plan}',
            '{Remaining}',
            '{Amount}',
            '{GroupName}',
            '{StartDate}',
            '{EndDate}'
            ) returning PID""")[0][0]
            SaveDB()
            Name, Username = Exec(F"select Name, Username from Users where ID={SID}")[0]
            await app.delete_messages(GID, MsgID)
            ExecS(F"delete from TempUsers where IDGID='{IDGID}'")
            
            await app.restrict_chat_member(
              chat_id=GID,
              user_id=SID,
              permissions=msg.chat.permissions
            )
            
            return await msg.reply(F"""
Subscription confirmed successfully!
SubscriptionID: `{PID}`
UserID: `{SID}`
Name: {Name}
Username: {Username if Username else '`NULL`'}
Plan: {Plan} Days
Amount: ₹ {Amount}
From: {StartDate}
To: {EndDate}
Group: {GroupName}
Confirmed by: [{msg.from_user.first_name}{msg.from_user.last_name if msg.from_user.last_name else ''}](tg://user?id={msg.from_user.id})
""", quote=1)

          else: raise Exception ("Invalid UniqueID")
        else: raise Exception
      else: raise Exception
  except Exception as e: return await msg.reply((F"--**Error:**--\n{e}\n\n" if len(str(e)) else "") + F"--**Usage**--\n`{HELP}`", quote=1)
#*---------------------------------------------------------------------


# /cancel UniqueID
@Client.on_message(GROUPS & command(["cancel", F"cancel{BotConfig.BOT_UNAME}"]))
async def Cancel(app, msg):
  HELP = F"{preFix}cancel UniqueID"
  sender = await app.get_chat_member(msg.chat.id, msg.from_user.id)
  try:
    if sender.status in [enums.ChatMemberStatus.OWNER, enums.ChatMemberStatus.ADMINISTRATOR]:
      if len(msg.text.split())>1:
        IDGID = msg.text.partition(msg.text.split()[0])[-1].strip()
        if Exec(F"Select count(*) from TempUsers where IDGID='{IDGID}'")[0][0]:
          GID, MsgID, Name, ID = Exec(F"Select GID, MsgID, Name, ID from TempUsers where IDGID='{IDGID}'")[0]
          await app.delete_messages(GID, MsgID)
          ExecS(F"delete from TempUsers where IDGID='{IDGID}'")
          await app.ban_chat_member(GID, ID)
          await app.unban_chat_member(GID, ID)
          return await msg.reply(F"Subscription cancelled and [{Name}](tg://user?id={ID}) has been kicked!", quote=1)
        else: raise Exception ("Invalid UniqueID")
      else: raise Exception
  except Exception as e: return await msg.reply((F"--**Error:**--\n{e}\n\n" if len(str(e)) else "") + F"--**Usage**--\n`{HELP}`", quote=1)
#*---------------------------------------------------------------------


# /extend SubscriptionID AdditionalDays
@Client.on_message(GROUPS & command(["extend", F"extend{BotConfig.BOT_UNAME}"]))
async def Extend(app, msg):
  HELP = F"{preFix}extend SubscriptionID AdditionalDays"
  sender = await app.get_chat_member(msg.chat.id, msg.from_user.id)
  try:
    if sender.status in [enums.ChatMemberStatus.OWNER, enums.ChatMemberStatus.ADMINISTRATOR]:
      # Arguments Provided
      if len(msg.text.split())>1:
        args = msg.text.split(maxsplit=1)[~0]
        args = args.split()
        if len(args)==2:
          PID, Additional = args
          Additional = int(Additional)
          if Exec(F"select count(*) from Subs where PID='{PID}' and Kicked=0")[0][0]:
            Plan, Remaining, StartDate, EndDate = Exec(F"select Plan, Remaining, StartDate, EndDate from Subs where PID='{PID}'")[0]
            Plan += Additional
            Remaining += Additional
            SD = datetime.strptime(StartDate, "%d-%b-%Y")
            ED = datetime.strptime(EndDate, "%d-%b-%Y") + timedelta(days=Additional)
            if ED>SD:
              EndDate = ED.strftime('%d-%b-%Y')
              ExecS(F"update Subs set Plan='{Plan}', Remaining='{Remaining}', EndDate='{EndDate}' where PID='{PID}'")
              return await msg.reply(F"Validy for SubscriptionID {PID} has been extended by {Additional} days!\nExtended Plan: {Plan} Days\nRemaining: {Remaining} Days\nStart Date: {StartDate}\nEnd Date: {EndDate}", quote=1)
            else: raise Exception ("Invalid value for additional days")
          else: raise Exception ("Invalid or expired SubscriptionID")
        else: raise Exception
      else: raise Exception
  except Exception as e: return await msg.reply((F"--**Error:**--\n{e}\n\n" if len(str(e)) else "") + F"--**Usage**--\n`{HELP}`", quote=1)
#*---------------------------------------------------------------------


# /terminate SubscriptionID
@Client.on_message(GROUPS & command(["terminate", F"terminate{BotConfig.BOT_UNAME}"]))
async def Delete(app, msg):
  HELP = F"{preFix}terminate SubscriptionID"
  sender = await app.get_chat_member(msg.chat.id, msg.from_user.id)
  try:
    if sender.status in [enums.ChatMemberStatus.OWNER, enums.ChatMemberStatus.ADMINISTRATOR]:
      if len(msg.text.split())>1:
        PID = msg.text.partition(msg.text.split()[0])[-1].strip()
        if Exec(F"select count(*) from Subs where PID='{PID}' and Kicked='0'")[0][0]:
          ID, GID, GroupName = Exec(F"select SID, GID, GroupName from Subs where PID='{PID}'")[0]
          Name = Exec(F"select Name from Users where ID='{ID}'")[0][0]
          await app.ban_chat_member(GID, ID)
          await app.unban_chat_member(GID, ID)
          ExecS(F"update Subs set Status='Expired', Kicked='1' where PID='{PID}'")
          return await msg.reply(F"SubscriptionID {PID} has been terminated and [{Name}](tg://user?id={ID}) has been kicked from {GroupName}!", quote=1)
        else: raise Exception ("Invalid or expired SubscriptionID")
      else: raise Exception
  except Exception as e: return await msg.reply((F"--**Error:**--\n{e}\n\n" if len(str(e)) else "") + F"--**Usage**--\n`{HELP}`", quote=1)
#*---------------------------------------------------------------------