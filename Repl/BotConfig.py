BOT_TOKEN = "5747136730:AAF0OvBU0F9wlG2E8qDVqnl5opLsbziWTmY"
BOT_UNAME = "@AKSubscriptionBot"
ALLOWED_GROUPS = [-1001749128708, -1001847114095] # Bot will only work in allowed groups
OWNER_ID = [1105331049] # User IDs added here will be able to access all owner commands
BACKUP_CHAT = -1001604903105 # For uploading daily database backups

PREFIX = "/" # Command prefix, leave it as is

# Result for the /help command
HELP = """--**Owner Commands**-- (Only works in Bot PM):
/help - This help message
/total - Total number of subscribers
/user *UserID | *Username - Information of a specific user
/users - Users table of the database
/subs - Subs table of the database
/broadcast <- Reply to a message

--**Admin Commands**-- (Only works in GROUPS specified in Config file)
/confirm *UniqueID *AMOUNT [DAYS] - Confirms a new subscription
/cancel *UniqueID - Cancels a new subscription
/extend *SubscriptionID *AdditionalDays - Extends a plan validity
/terminate *SubscriptionID - Terminates an active subscription plan

--**User Commands**-- (Only works in Bot PM)
/myinfo - User's information"""
