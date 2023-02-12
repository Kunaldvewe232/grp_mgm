from pyrogram import Client, filters
from pyrogram.types import (
  InlineKeyboardButton, 
  InlineKeyboardMarkup
)
import BotConfig
from Sqlite import Exec, ExecS


'''===========EDITABLES==========='''

preFix = BotConfig.PREFIX
WELCOME_MESSAGE = """
[{fname}](tg://user?id={uid}) joined the chat!
ID: `{uid}`
First Name: {fname}
Last Name: {lname}
Username: {uname}

{note}
"""

'''-------------------------------'''


command = lambda cmd: filters.command(cmd, prefixes = preFix)


# /start [UniqueID]
@Client.on_message(filters.private & command(["start", F"start{BotConfig.BOT_UNAME}"]))
async def Start(app, msg):
  newMember = msg.from_user
  ExecS(F"insert or replace into Broadcast values('{newMember.id}')")
  memberUName = F"@{newMember.username}" if newMember.username else ""
  if len(msg.text.split())>1:
    IDGID = msg.text.partition(msg.text.split()[0])[~0].strip()
    ID = int(IDGID.split("-")[0])
    GID = int(IDGID.split("-")[~0])*~0
    if Exec(F"select count(*) from TempUsers where IDGID='{IDGID}'")[0][0] and ID==newMember.id:
      # Cleanup the previous message
      MsgID = Exec(F"select MsgID from TempUsers where IDGID='{IDGID}'")[0][0]
      await app.delete_messages(GID, MsgID)
      await msg.reply("Bot started successfully!", quote=1)
      plansBtns = [
        [
          InlineKeyboardButton('15 Days', callback_data=F'plan_15_{ID}'),
          InlineKeyboardButton('30 Days', callback_data=F'plan_30_{ID}'),
        ],
        [InlineKeyboardButton('Custom Plan', callback_data=F'plan_0_{ID}')],
        [InlineKeyboardButton('Approve Member', callback_data=F'appr_{ID}')],
        [InlineKeyboardButton('Delete', callback_data=F'kick_{ID}')]
      ]
      plans = InlineKeyboardMarkup(plansBtns)
      await app.send_message(GID,
        WELCOME_MESSAGE.format(
          uid=ID,
          fname=newMember.first_name,
          lname=newMember.last_name if newMember.last_name else "`NULL`",
          uname=memberUName if memberUName else "`NULL`",
          note="Select the subscription plan:"
        ), 
        reply_markup=plans
      )
    else: await msg.reply(F"Hello {newMember.first_name} If  You Face Any Issue Join Our Premium Suppport Group [Click Here](https://t.me/AKImaxPremium).!", quote=1, disable_web_page_preview=1)
  else: await msg.reply(F"Hello {newMember.first_name} If  You Face Any Issue Join Our Premium Suppport Group [Click Here](https://t.me/AKImaxPremium).!", quote=1, disable_web_page_preview=1)