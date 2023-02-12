from pyrogram import Client, filters, enums
from pyrogram.types import (
  InlineKeyboardButton, 
  InlineKeyboardMarkup, 
  ChatPermissions
)
import BotConfig
from Sqlite import Exec, ExecS


'''===========EDITABLES==========='''

GROUPS = filters.chat(BotConfig.ALLOWED_GROUPS)
WELCOME_MESSAGE = """
[{fname}](tg://user?id={uid}) joined the chat!
ID: `{uid}`
First Name: {fname}
Last Name: {lname}
Username: {uname}

{note}
"""

'''-------------------------------'''


@Client.on_message(filters.new_chat_members & GROUPS)
async def welcome(app, msg):
  for newMember in msg.new_chat_members:
    proceedable = False
    memberID = newMember.id
    memberUName = F"@{newMember.username}" if newMember.username else ""
    memberName = newMember.first_name + (newMember.last_name if newMember.last_name else "")

    if not newMember.is_bot:
      userInDB = Exec(F"select count(*) from Users where ID={memberID}")[0][0]
      if userInDB:
        ActivePlans = Exec(F"select count(*) from Subs where SID={memberID} and GID={msg.chat.id} and Kicked='0'")[0][0]
        if ActivePlans:
          return await msg.reply(
            WELCOME_MESSAGE.format(
              uid=memberID,
              fname=newMember.first_name,
              lname=newMember.last_name if newMember.last_name else "`NULL`",
              uname=memberUName if memberUName else "`NULL`",
              note=F"{newMember.first_name} is already having {ActivePlans} active plan(s) for this group."
            )
          )
        else: proceedable = True
      else: proceedable = True
    
    
    if proceedable:
      await app.restrict_chat_member(
        chat_id=msg.chat.id,
        user_id=memberID,
        permissions=ChatPermissions()
      )

      StartBtn = [[InlineKeyboardButton('Start the bot', url=F'https://t.me/{BotConfig.BOT_UNAME[-~0:]}?start={memberID}{msg.chat.id}')]]
      StartMkp = InlineKeyboardMarkup(StartBtn)
      rep = await msg.reply(F"Hello [{memberName}](tg://user?id={memberID})! Welcome to {msg.chat.title}.\n\nPlease start the bot using the button below.", reply_markup=StartMkp)

      ExecS(F"""insert or replace into TempUsers values(
        '{memberID}{msg.chat.id}',
        '{memberID}',
        '{memberUName}',
        '{memberName}',
        '-1',
        '-1',
        '{msg.chat.id}',
        '{rep.id}'
      )""")

async def delq(app, query):
  await app.delete_messages(query.message.chat.id, query.message.id)

@Client.on_callback_query()
async def botCallbacksGroup(app, query):
  chatID = query.message.chat.id
  clickerID = query.from_user.id
  clicker = await app.get_chat_member(chatID, clickerID)
  memberID = int(query.data.split("_")[~0])
  
  if clicker.status in [enums.ChatMemberStatus.OWNER, enums.ChatMemberStatus.ADMINISTRATOR]:

    if query.data.startswith("appr_"):
      if clicker.status in [enums.ChatMemberStatus.OWNER]:
        await app.restrict_chat_member(
          chat_id=chatID,
          user_id=memberID,
          permissions=query.message.chat.permissions
        )
        ExecS(F"delete from TempUsers WHERE IDGID='{memberID}{chatID}'")
        await query.edit_message_text(F"New member approved!\n[Member ID](tg://user?id={memberID}): `{memberID}`\n[Admin ID](tg://user?id={clickerID}): `{clickerID}`")
        await query.answer("Member approved!")

    
    if query.data.startswith("kick_"):
      await app.ban_chat_member(chatID, memberID)
      await query.answer("Message deleted and member kicked!")
      await app.unban_chat_member(chatID, memberID)
      await delq(app, query)
      ExecS(F"delete from TempUsers WHERE IDGID='{memberID}{chatID}'")

    if query.data.startswith("plan_"):
      plan = int(query.data.split("_")[-~0])
      IDGID = F"{memberID}{chatID}"
      await delq(app, query)
      rep = await app.send_message(chatID, F"Subscription plan selected for new member!\n[Member ID](tg://user?id={memberID}): `{memberID}`\nPlan: {str(plan)+' Days' if plan else 'Custom'}\n[Admin ID](tg://user?id={clickerID}): `{clickerID}`\n\nTo confirm:\n`/confirm {IDGID}` AMOUNT{' DAYS' if not plan else ''}\n\nTo cancel:\n`/cancel {IDGID}`")
      ExecS(F"update TempUsers set Plan='{plan}', MsgID='{rep.id}' where IDGID='{IDGID}'")

  else: await query.answer("This button is not for you. Kindly ask an admin instead.", show_alert=1)