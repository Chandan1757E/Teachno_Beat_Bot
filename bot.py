import logging
import sqlite3
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler
from telegram.parsemode import ParseMode
import time

# Bot Configuration
BOT_TOKEN = "6990761692:AAHI_E2l00AJxr9ue4mRKjG5uetPBXKp0rk"
CHANNEL_LINK = "https://t.me/Techno_Beats_Redirect"
OWNER_ID = 1614927658
OWNER_USERNAME = "@Chandan1757E"
CHANNEL_NAME = "Techno Beat's"

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Database setup
def init_db():
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            is_banned INTEGER DEFAULT 0,
            is_muted INTEGER DEFAULT 0,
            warnings INTEGER DEFAULT 0,
            join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Groups table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS groups (
            chat_id INTEGER PRIMARY KEY,
            title TEXT,
            welcome_message TEXT,
            leave_message TEXT,
            filter_links INTEGER DEFAULT 1,
            filter_sexual INTEGER DEFAULT 1
        )
    ''')
    
    # Broadcast messages table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS broadcast_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message_text TEXT,
            sent_by INTEGER,
            sent_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

init_db()

# Emoji configurations
EMOJIS = {
    'welcome': '👋',
    'leave': '😢',
    'warning': '⚠️',
    'success': '✅',
    'error': '❌',
    'info': 'ℹ️',
    'user': '👤',
    'group': '👥',
    'channel': '📢',
    'admin': '👑',
    'settings': '⚙️',
    'ban': '🔨',
    'mute': '🔇',
    'unban': '🔓',
    'unmute': '🔊',
    'broadcast': '📡',
    'filter': '🛡️'
}

# Welcome and Leave Messages
WELCOME_MESSAGE = f"""
{EMOJIS['welcome']} *Welcome to Our Family!* {EMOJIS['welcome']}

🎉 *Congratulations!* You have successfully joined *{CHANNEL_NAME}*!

{EMOJIS['success']} *What you'll get here:*
• 📱 Latest Technology Updates
• 🔧 Android Tips & Tricks
• 💡 Useful Tech Guides
• 🚀 Productivity Hacks
• 🔒 Security Tips

🌟 *We're excited to have you!* 
Get ready for amazing content that will enhance your digital experience!

{EMOJIS['info']} *Note:* If you face any issues, contact {OWNER_USERNAME}
"""

LEAVE_MESSAGE = f"""
{EMOJIS['leave']} *We're Sad to See You Go!* {EMOJIS['leave']}

😔 *You have left* *{CHANNEL_NAME}*

{EMOJIS['info']} *We're sorry if:*
• You faced any issues
• Content wasn't as expected
• There were too many messages

💭 *Your feedback matters!* 
If you have any concerns or suggestions, please contact {OWNER_USERNAME}

We hope to see you again soon! 🌟
"""

def add_user_to_db(user):
    """Add user to database"""
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO users (user_id, username, first_name, last_name)
        VALUES (?, ?, ?, ?)
    ''', (user.id, user.username, user.first_name, user.last_name))
    conn.commit()
    conn.close()

def start(update: Update, context: CallbackContext):
    user = update.effective_user
    add_user_to_db(user)
    
    keyboard = [
        [InlineKeyboardButton(f"{EMOJIS['channel']} Join Channel", url=CHANNEL_LINK)],
        [InlineKeyboardButton(f"{EMOJIS['info']} User Info", callback_data='user_info'),
         InlineKeyboardButton(f"{EMOJIS['admin']} Admin Panel", callback_data='admin_panel')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = f"""
{EMOJIS['welcome']} *Hello {user.first_name}!* {EMOJIS['welcome']}

🤖 *Welcome to Techno Beat's Bot!*

{EMOJIS['success']} *Features Available:*
• 📊 User Management
• 🛡️ Content Filtering
• 📢 Broadcasting
• 👋 Welcome Messages
• 😢 Leave Messages
• 🔧 And much more!

Use buttons below to navigate:
    """
    
    update.message.reply_text(
        welcome_text,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )

def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    
    if query.data == 'user_info':
        user = query.from_user
        user_info = f"""
{EMOJIS['user']} *User Information* {EMOJIS['user']}

*🆔 User ID:* `{user.id}`
*👤 Name:* {user.first_name}
*📛 Username:* @{user.username if user.username else 'N/A'}
*🔗 Profile Link:* [Click Here](tg://user?id={user.id})

{EMOJIS['info']} *Bot Features:*
• Get your chat ID
• User management
• Content filtering
• Broadcast messages
        """
        query.edit_message_text(
            user_info,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(f"{EMOJIS['settings']} Back", callback_data='back_start')]])
        )
    
    elif query.data == 'admin_panel':
        if query.from_user.id == OWNER_ID:
            keyboard = [
                [InlineKeyboardButton(f"{EMOJIS['broadcast']} Broadcast", callback_data='broadcast'),
                 InlineKeyboardButton(f"{EMOJIS['user']} User List", callback_data='user_list')],
                [InlineKeyboardButton(f"{EMOJIS['settings']} Settings", callback_data='settings'),
                 InlineKeyboardButton(f"{EMOJIS['info']} Bot Info", callback_data='bot_info')],
                [InlineKeyboardButton(f"{EMOJIS['settings']} Back", callback_data='back_start')]
            ]
            admin_text = f"""
{EMOJIS['admin']} *Admin Panel* {EMOJIS['admin']}

*Available Commands:*
• 📊 User statistics
• 📢 Broadcast messages
• 🛡️ Content filtering
• 👥 Group management
• ⚙️ Bot settings

Select an option:
            """
            query.edit_message_text(
                admin_text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            query.edit_message_text(
                f"{EMOJIS['error']} *Access Denied!* {EMOJIS['error']}\n\nYou are not authorized to access admin panel.",
                parse_mode=ParseMode.MARKDOWN
            )
    
    elif query.data == 'back_start':
        context.bot.send_message(
            chat_id=query.message.chat_id,
            text="Returning to main menu..."
        )
        start(update, context)

def get_chat_id(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    update.message.reply_text(
        f"{EMOJIS['info']} *Chat ID:* `{chat_id}`",
        parse_mode=ParseMode.MARKDOWN
    )

def user_list(update: Update, context: CallbackContext):
    if update.effective_user.id != OWNER_ID:
        update.message.reply_text(f"{EMOJIS['error']} Access Denied!")
        return
    
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]
    
    cursor.execute("SELECT user_id, username, first_name FROM users LIMIT 50")
    users = cursor.fetchall()
    conn.close()
    
    user_list_text = f"{EMOJIS['user']} *Active Users List* {EMOJIS['user']}\n\n"
    user_list_text += f"*Total Users:* {total_users}\n\n"
    
    for user_id, username, first_name in users:
        user_info = f"• {first_name} (@{username if username else 'N/A'}) - `{user_id}`\n"
        user_list_text += user_info
    
    if total_users > 50:
        user_list_text += f"\n{EMOJIS['info']} *Showing first 50 users*"
    
    update.message.reply_text(
        user_list_text,
        parse_mode=ParseMode.MARKDOWN
    )

def broadcast_message(update: Update, context: CallbackContext):
    if update.effective_user.id != OWNER_ID:
        update.message.reply_text(f"{EMOJIS['error']} Access Denied!")
        return
    
    if not context.args:
        update.message.reply_text(
            f"{EMOJIS['info']} Usage: /broadcast <message>"
        )
        return
    
    message = ' '.join(context.args)
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users")
    users = cursor.fetchall()
    conn.close()
    
    success = 0
    failed = 0
    
    for user_id, in users:
        try:
            context.bot.send_message(
                chat_id=user_id,
                text=f"{EMOJIS['broadcast']} *Broadcast Message* {EMOJIS['broadcast']}\n\n{message}",
                parse_mode=ParseMode.MARKDOWN
            )
            success += 1
        except Exception as e:
            failed += 1
        time.sleep(0.1)
    
    update.message.reply_text(
        f"{EMOJIS['success']} *Broadcast Completed!*\n\n✅ Success: {success}\n❌ Failed: {failed}",
        parse_mode=ParseMode.MARKDOWN
    )

def handle_new_chat_members(update: Update, context: CallbackContext):
    for member in update.message.new_chat_members:
        add_user_to_db(member)
        
        if member.id == context.bot.id:
            # Bot added to group/channel
            chat = update.effective_chat
            conn = sqlite3.connect('bot_database.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO groups (chat_id, title, welcome_message, leave_message)
                VALUES (?, ?, ?, ?)
            ''', (chat.id, chat.title, WELCOME_MESSAGE, LEAVE_MESSAGE))
            conn.commit()
            conn.close()
            
            update.message.reply_text(
                f"{EMOJIS['success']} *Thanks for adding me!* {EMOJIS['success']}\n\n"
                f"I'm now ready to manage this {chat.type}!\n\n"
                f"Use /settings to configure welcome/leave messages."
            )
        else:
            # Regular user joined
            chat_title = update.effective_chat.title
            welcome_msg = WELCOME_MESSAGE.replace(CHANNEL_NAME, chat_title)
            
            update.message.reply_text(
                welcome_msg,
                parse_mode=ParseMode.MARKDOWN
            )

def handle_left_chat_member(update: Update, context: CallbackContext):
    if update.message.left_chat_member:
        chat_title = update.effective_chat.title
        leave_msg = LEAVE_MESSAGE.replace(CHANNEL_NAME, chat_title)
        
        update.message.reply_text(
            leave_msg,
            parse_mode=ParseMode.MARKDOWN
        )

def message_filter(update: Update, context: CallbackContext):
    if not update.message or update.message.chat.type == 'private':
        return
    
    message_text = update.message.text or update.message.caption or ''
    user_id = update.message.from_user.id
    chat_id = update.message.chat.id
    
    # Check if user is admin
    try:
        chat_member = context.bot.get_chat_member(chat_id, user_id)
        if chat_member.status in ['administrator', 'creator']:
            return
    except:
        return
    
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT filter_links, filter_sexual FROM groups WHERE chat_id = ?", (chat_id,))
    group_settings = cursor.fetchone()
    
    if not group_settings:
        conn.close()
        return
    
    filter_links, filter_sexual = group_settings
    
    # Link filter
    if filter_links and re.search(r'https?://|t\.me/|www\.', message_text, re.IGNORECASE):
        try:
            update.message.delete()
            update.message.reply_text(
                f"{EMOJIS['warning']} *Links are not allowed here!* {EMOJIS['warning']}",
                reply_to_message_id=update.message.message_id
            )
        except Exception as e:
            logger.error(f"Error deleting message: {e}")
        finally:
            conn.close()
            return
    
    # Sexual content filter
    sexual_keywords = ['porn', 'xxx', 'adult', 'nsfw', 'sex', 'nude', 'naked']
    if filter_sexual and any(keyword in message_text.lower() for keyword in sexual_keywords):
        try:
            update.message.delete()
            update.message.reply_text(
                f"{EMOJIS['warning']} *Inappropriate content detected!* {EMOJIS['warning']}",
                reply_to_message_id=update.message.message_id
            )
        except Exception as e:
            logger.error(f"Error deleting message: {e}")
    
    conn.close()

def settings_command(update: Update, context: CallbackContext):
    if update.effective_chat.type == 'private':
        update.message.reply_text(
            f"{EMOJIS['settings']} *Settings Menu* {EMOJIS['settings']}\n\n"
            "This command works in groups/channels only."
        )
        return
    
    keyboard = [
        [InlineKeyboardButton(f"{EMOJIS['filter']} Toggle Link Filter", callback_data='toggle_links'),
         InlineKeyboardButton(f"{EMOJIS['filter']} Toggle Content Filter", callback_data='toggle_content')],
        [InlineKeyboardButton(f"{EMOJIS['settings']} Set Welcome Message", callback_data='set_welcome'),
         InlineKeyboardButton(f"{EMOJIS['settings']} Set Leave Message", callback_data='set_leave')]
    ]
    
    update.message.reply_text(
        f"{EMOJIS['settings']} *Group Settings* {EMOJIS['settings']}\n\n"
        "Configure your group settings:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN
    )

def main():
    # Create the Updater and pass it your bot's token
    updater = Updater(BOT_TOKEN, use_context=True)
    
    # Get the dispatcher to register handlers
    dp = updater.dispatcher
    
    # Add handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("chatid", get_chat_id))
    dp.add_handler(CommandHandler("userlist", user_list))
    dp.add_handler(CommandHandler("broadcast", broadcast_message))
    dp.add_handler(CommandHandler("settings", settings_command))
    
    dp.add_handler(CallbackQueryHandler(button_handler))
    
    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, handle_new_chat_members))
    dp.add_handler(MessageHandler(Filters.status_update.left_chat_member, handle_left_chat_member))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, message_filter))
    
    # Start the Bot
    updater.start_polling()
    
    # Run the bot until you press Ctrl-C
    updater.idle()

if __name__ == '__main__':
    main()
