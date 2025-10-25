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

# Unique Emoji configurations
EMOJIS = {
    'welcome': '🎊',
    'leave': '👋',
    'warning': '🚨',
    'success': '✅',
    'error': '❌',
    'info': '💡',
    'user': '👤',
    'group': '👥',
    'channel': '📢',
    'admin': '⚡',
    'settings': '🔧',
    'ban': '🔨',
    'mute': '🔇',
    'unban': '🔓',
    'unmute': '🎤',
    'broadcast': '📡',
    'filter': '🛡️',
    'list': '📜',
    'back': '↩️',
    'link': '🔗',
    'content': '📵',
    'message': '💬',
    'stats': '📊',
    'help': '❓',
    'family': '👨‍👩‍👧‍👦',
    'technology': '📱',
    'android': '🤖',
    'tips': '💡',
    'security': '🔒',
    'productivity': '🚀',
    'guide': '📚'
}

# Welcome and Leave Messages
WELCOME_MESSAGE = f"""
{EMOJIS['welcome']} *Welcome to Our {EMOJIS['family']} Family!* {EMOJIS['welcome']}

{EMOJIS['success']} *Congratulations!* You have successfully joined *{CHANNEL_NAME}*!

{EMOJIS['technology']} *What you'll get here:*
• {EMOJIS['android']} Android Tips & Tricks
• {EMOJIS['technology']} Latest Technology Updates  
• {EMOJIS['guide']} Useful Tech Guides
• {EMOJIS['productivity']} Productivity Hacks
• {EMOJIS['security']} Security Tips

{EMOJIS['success']} *We're excited to have you!* 
Get ready for amazing content that will enhance your digital experience!

{EMOJIS['info']} *Note:* If you face any issues, contact {OWNER_USERNAME}
"""

LEAVE_MESSAGE = f"""
{EMOJIS['leave']} *We're Sad to See You Go!* {EMOJIS['leave']}

{EMOJIS['error']} *You have left* *{CHANNEL_NAME}*

{EMOJIS['info']} *We're sorry if:*
• You faced any issues
• Content wasn't as expected  
• There were too many messages

{EMOJIS['message']} *Your feedback matters!* 
If you have any concerns or suggestions, please contact {OWNER_USERNAME}

We hope to see you again soon! {EMOJIS['success']}
"""

def add_user_to_db(user):
    """Add user to database"""
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO users (user_id, username, first_name, last_name)
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
         InlineKeyboardButton(f"{EMOJIS['admin']} Admin Panel", callback_data='admin_panel')],
        [InlineKeyboardButton(f"{EMOJIS['list']} Commands List", callback_data='commands_list')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = f"""
{EMOJIS['welcome']} *Hello {user.first_name}!* {EMOJIS['welcome']}

{EMOJIS['technology']} *Welcome to Techno Beat's Bot!*

{EMOJIS['success']} *Features Available:*
• {EMOJIS['user']} User Management
• {EMOJIS['filter']} Content Filtering  
• {EMOJIS['broadcast']} Broadcasting
• {EMOJIS['welcome']} Welcome Messages
• {EMOJIS['leave']} Leave Messages
• {EMOJIS['settings']} And much more!

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

{EMOJIS['info']} *User ID:* `{user.id}`
{EMOJIS['user']} *Name:* {user.first_name}
{EMOJIS['channel']} *Username:* @{user.username if user.username else 'N/A'}
{EMOJIS['link']} *Profile Link:* [Click Here](tg://user?id={user.id})

{EMOJIS['settings']} *Bot Features:*
• Get your chat ID
• User management
• Content filtering
• Broadcast messages
        """
        query.edit_message_text(
            user_info,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(f"{EMOJIS['back']} Back", callback_data='back_start')]])
        )
    
    elif query.data == 'admin_panel':
        if query.from_user.id == OWNER_ID:
            keyboard = [
                [InlineKeyboardButton(f"{EMOJIS['broadcast']} Broadcast", callback_data='broadcast'),
                 InlineKeyboardButton(f"{EMOJIS['user']} User List", callback_data='user_list')],
                [InlineKeyboardButton(f"{EMOJIS['settings']} Group Settings", callback_data='group_settings'),
                 InlineKeyboardButton(f"{EMOJIS['stats']} Bot Stats", callback_data='bot_stats')],
                [InlineKeyboardButton(f"{EMOJIS['back']} Back", callback_data='back_start')]
            ]
            admin_text = f"""
{EMOJIS['admin']} *Admin Panel* {EMOJIS['admin']}

{EMOJIS['settings']} *Available Commands:*
• {EMOJIS['stats']} User statistics
• {EMOJIS['broadcast']} Broadcast messages
• {EMOJIS['filter']} Content filtering
• {EMOJIS['group']} Group management
• {EMOJIS['settings']} Bot settings

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
    
    elif query.data == 'commands_list':
        commands_text = f"""
{EMOJIS['list']} *Available Commands* {EMOJIS['list']}

{EMOJIS['user']} *User Commands:*
• /start - {EMOJIS['welcome']} Start the bot
• /chatid - {EMOJIS['info']} Get chat ID  
• /help - {EMOJIS['help']} Show help message

{EMOJIS['admin']} *Admin Commands:*
• /userlist - {EMOJIS['user']} Show user list
• /broadcast - {EMOJIS['broadcast']} Broadcast message
• /stats - {EMOJIS['stats']} Bot statistics

{EMOJIS['settings']} *Group Commands:*
• /settings - {EMOJIS['settings']} Group settings
• /setwelcome - {EMOJIS['welcome']} Set welcome message
• /setleave - {EMOJIS['leave']} Set leave message

{EMOJIS['filter']} *Filter Commands:*
• /filterlinks - {EMOJIS['link']} Toggle link filter
• /filtercontent - {EMOJIS['content']} Toggle content filter
        """
        query.edit_message_text(
            commands_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(f"{EMOJIS['back']} Back", callback_data='back_start')]])
        )
    
    elif query.data == 'group_settings':
        if query.from_user.id == OWNER_ID:
            keyboard = [
                [InlineKeyboardButton(f"{EMOJIS['welcome']} Set Welcome", callback_data='set_welcome'),
                 InlineKeyboardButton(f"{EMOJIS['leave']} Set Leave", callback_data='set_leave')],
                [InlineKeyboardButton(f"{EMOJIS['link']} Link Filter", callback_data='toggle_links'),
                 InlineKeyboardButton(f"{EMOJIS['content']} Content Filter", callback_data='toggle_content')],
                [InlineKeyboardButton(f"{EMOJIS['back']} Back", callback_data='admin_panel')]
            ]
            settings_text = f"""
{EMOJIS['settings']} *Group Settings* {EMOJIS['settings']}

Configure your group settings:

{EMOJIS['welcome']} *Welcome Message:* Customize welcome message
{EMOJIS['leave']} *Leave Message:* Customize leave message  
{EMOJIS['link']} *Link Filter:* Block/Allow links
{EMOJIS['content']} *Content Filter:* Block inappropriate content

Select an option to configure:
            """
            query.edit_message_text(
                settings_text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode=ParseMode.MARKDOWN
            )
    
    elif query.data == 'set_welcome':
        query.edit_message_text(
            f"{EMOJIS['welcome']} *Set Welcome Message* {EMOJIS['welcome']}\n\n"
            "Use command: /setwelcome <your message>\n\n"
            "Example: /setwelcome Hello {name}! Welcome to {group}!\n\n"
            "Variables: {name} - User name, {group} - Group name",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(f"{EMOJIS['back']} Back", callback_data='group_settings')]])
        )
    
    elif query.data == 'set_leave':
        query.edit_message_text(
            f"{EMOJIS['leave']} *Set Leave Message* {EMOJIS['leave']}\n\n"
            "Use command: /setleave <your message>\n\n"
            "Example: /setleave Goodbye {name}! We'll miss you!\n\n"
            "Variables: {name} - User name, {group} - Group name",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(f"{EMOJIS['back']} Back", callback_data='group_settings')]])
        )
    
    elif query.data == 'toggle_links':
        query.edit_message_text(
            f"{EMOJIS['link']} *Link Filter Settings* {EMOJIS['link']}\n\n"
            "Use command: /filterlinks on/off\n\n"
            "Example: /filterlinks on - to enable link filtering\n"
            "Example: /filterlinks off - to disable link filtering",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(f"{EMOJIS['back']} Back", callback_data='group_settings')]])
        )
    
    elif query.data == 'toggle_content':
        query.edit_message_text(
            f"{EMOJIS['content']} *Content Filter Settings* {EMOJIS['content']}\n\n"
            "Use command: /filtercontent on/off\n\n"
            "Example: /filtercontent on - to enable content filtering\n"
            "Example: /filtercontent off - to disable content filtering",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(f"{EMOJIS['back']} Back", callback_data='group_settings')]])
        )
    
    elif query.data == 'back_start':
        start_from_query(update, context)

def start_from_query(update: Update, context: CallbackContext):
    query = update.callback_query
    user = query.from_user
    
    keyboard = [
        [InlineKeyboardButton(f"{EMOJIS['channel']} Join Channel", url=CHANNEL_LINK)],
        [InlineKeyboardButton(f"{EMOJIS['info']} User Info", callback_data='user_info'),
         InlineKeyboardButton(f"{EMOJIS['admin']} Admin Panel", callback_data='admin_panel')],
        [InlineKeyboardButton(f"{EMOJIS['list']} Commands List", callback_data='commands_list')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = f"""
{EMOJIS['welcome']} *Hello {user.first_name}!* {EMOJIS['welcome']}

{EMOJIS['technology']} *Welcome to Techno Beat's Bot!*

{EMOJIS['success']} *Features Available:*
• {EMOJIS['user']} User Management
• {EMOJIS['filter']} Content Filtering  
• {EMOJIS['broadcast']} Broadcasting
• {EMOJIS['welcome']} Welcome Messages
• {EMOJIS['leave']} Leave Messages
• {EMOJIS['settings']} And much more!

Use buttons below to navigate:
    """
    
    query.edit_message_text(
        welcome_text,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )

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
    user_list_text += f"{EMOJIS['stats']} *Total Users:* {total_users}\n\n"
    
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
        f"{EMOJIS['success']} *Broadcast Completed!*\n\n{EMOJIS['success']} Success: {success}\n{EMOJIS['error']} Failed: {failed}",
        parse_mode=ParseMode.MARKDOWN
    )

def list_commands(update: Update, context: CallbackContext):
    commands_text = f"""
{EMOJIS['list']} *🤖 Bot Commands List* {EMOJIS['list']}

{EMOJIS['user']} *👤 User Commands:*
• /start {EMOJIS['welcome']} - Start the bot
• /chatid {EMOJIS['info']} - Get chat ID  
• /help {EMOJIS['help']} - Show help message
• /list {EMOJIS['list']} - Show all commands

{EMOJIS['admin']} *⚡ Admin Commands:*
• /userlist {EMOJIS['user']} - Show user list
• /broadcast {EMOJIS['broadcast']} - Broadcast message
• /stats {EMOJIS['stats']} - Bot statistics

{EMOJIS['settings']} *🔧 Group Commands:*
• /settings {EMOJIS['settings']} - Group settings
• /setwelcome {EMOJIS['welcome']} - Set welcome message
• /setleave {EMOJIS['leave']} - Set leave message

{EMOJIS['filter']} *🛡️ Filter Commands:*
• /filterlinks {EMOJIS['link']} - Toggle link filter
• /filtercontent {EMOJIS['content']} - Toggle content filter

{EMOJIS['info']} *Simply type / to see all available commands!*
    """
    
    update.message.reply_text(
        commands_text,
        parse_mode=ParseMode.MARKDOWN
    )

def set_welcome(update: Update, context: CallbackContext):
    if update.effective_chat.type == 'private':
        update.message.reply_text(f"{EMOJIS['error']} This command works in groups only!")
        return
    
    if not context.args:
        update.message.reply_text(
            f"{EMOJIS['info']} Usage: /setwelcome <your welcome message>\n\n"
            "Variables: {{name}} - User name, {{group}} - Group name\n"
            f"Example: /setwelcome Hello {{name}}! {EMOJIS['welcome']} Welcome to {{group}}!"
        )
        return
    
    welcome_msg = ' '.join(context.args)
    chat_id = update.effective_chat.id
    
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO groups (chat_id, title, welcome_message)
        VALUES (?, ?, ?)
    ''', (chat_id, update.effective_chat.title, welcome_msg))
    conn.commit()
    conn.close()
    
    update.message.reply_text(
        f"{EMOJIS['success']} *Welcome message set successfully!* {EMOJIS['success']}\n\n"
        f"Preview: {welcome_msg}",
        parse_mode=ParseMode.MARKDOWN
    )

def set_leave(update: Update, context: CallbackContext):
    if update.effective_chat.type == 'private':
        update.message.reply_text(f"{EMOJIS['error']} This command works in groups only!")
        return
    
    if not context.args:
        update.message.reply_text(
            f"{EMOJIS['info']} Usage: /setleave <your leave message>\n\n"
            "Variables: {{name}} - User name, {{group}} - Group name\n"
            f"Example: /setleave Goodbye {{name}}! {EMOJIS['leave']} We'll miss you!"
        )
        return
    
    leave_msg = ' '.join(context.args)
    chat_id = update.effective_chat.id
    
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO groups (chat_id, title, leave_message)
        VALUES (?, ?, ?)
    ''', (chat_id, update.effective_chat.title, leave_msg))
    conn.commit()
    conn.close()
    
    update.message.reply_text(
        f"{EMOJIS['success']} *Leave message set successfully!* {EMOJIS['success']}\n\n"
        f"Preview: {leave_msg}",
        parse_mode=ParseMode.MARKDOWN
    )

def filter_links(update: Update, context: CallbackContext):
    if update.effective_chat.type == 'private':
        update.message.reply_text(f"{EMOJIS['error']} This command works in groups only!")
        return
    
    if not context.args:
        # Show current status
        conn = sqlite3.connect('bot_database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT filter_links FROM groups WHERE chat_id = ?", (update.effective_chat.id,))
        result = cursor.fetchone()
        status = "on" if (result and result[0] == 1) else "on" if not result else "off"
        conn.close()
        
        update.message.reply_text(
            f"{EMOJIS['link']} *Link Filter Status:* {status.upper()}\n\n"
            f"Usage: /filterlinks on/off\n"
            f"Example: /filterlinks on - {EMOJIS['success']} Enable link filtering\n"
            f"Example: /filterlinks off - {EMOJIS['error']} Disable link filtering"
        )
        return
    
    action = context.args[0].lower()
    chat_id = update.effective_chat.id
    
    if action in ['on', 'enable', 'yes', '1']:
        filter_value = 1
        status_msg = f"{EMOJIS['success']} Link filtering enabled!"
    elif action in ['off', 'disable', 'no', '0']:
        filter_value = 0
        status_msg = f"{EMOJIS['error']} Link filtering disabled!"
    else:
        update.message.reply_text(f"{EMOJIS['error']} Invalid option! Use 'on' or 'off'")
        return
    
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO groups (chat_id, title, filter_links)
        VALUES (?, ?, ?)
    ''', (chat_id, update.effective_chat.title, filter_value))
    conn.commit()
    conn.close()
    
    update.message.reply_text(status_msg)

def filter_content(update: Update, context: CallbackContext):
    if update.effective_chat.type == 'private':
        update.message.reply_text(f"{EMOJIS['error']} This command works in groups only!")
        return
    
    if not context.args:
        # Show current status
        conn = sqlite3.connect('bot_database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT filter_sexual FROM groups WHERE chat_id = ?", (update.effective_chat.id,))
        result = cursor.fetchone()
        status = "on" if (result and result[0] == 1) else "on" if not result else "off"
        conn.close()
        
        update.message.reply_text(
            f"{EMOJIS['content']} *Content Filter Status:* {status.upper()}\n\n"
            f"Usage: /filtercontent on/off\n"
            f"Example: /filtercontent on - {EMOJIS['success']} Enable content filtering\n"
            f"Example: /filtercontent off - {EMOJIS['error']} Disable content filtering"
        )
        return
    
    action = context.args[0].lower()
    chat_id = update.effective_chat.id
    
    if action in ['on', 'enable', 'yes', '1']:
        filter_value = 1
        status_msg = f"{EMOJIS['success']} Content filtering enabled!"
    elif action in ['off', 'disable', 'no', '0']:
        filter_value = 0
        status_msg = f"{EMOJIS['error']} Content filtering disabled!"
    else:
        update.message.reply_text(f"{EMOJIS['error']} Invalid option! Use 'on' or 'off'")
        return
    
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO groups (chat_id, title, filter_sexual)
        VALUES (?, ?, ?)
    ''', (chat_id, update.effective_chat.title, filter_value))
    conn.commit()
    conn.close()
    
    update.message.reply_text(status_msg)

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
            # Regular user joined - get custom welcome message
            chat_id = update.effective_chat.id
            conn = sqlite3.connect('bot_database.db')
            cursor = conn.cursor()
            cursor.execute("SELECT welcome_message FROM groups WHERE chat_id = ?", (chat_id,))
            result = cursor.fetchone()
            conn.close()
            
            if result and result[0]:
                welcome_msg = result[0].replace('{name}', member.first_name).replace('{group}', update.effective_chat.title)
            else:
                welcome_msg = WELCOME_MESSAGE.replace(CHANNEL_NAME, update.effective_chat.title)
                welcome_msg = welcome_msg.replace('{name}', member.first_name)
            
            update.message.reply_text(
                welcome_msg,
                parse_mode=ParseMode.MARKDOWN
            )

def handle_left_chat_member(update: Update, context: CallbackContext):
    if update.message.left_chat_member:
        # Get custom leave message
        chat_id = update.effective_chat.id
        conn = sqlite3.connect('bot_database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT leave_message FROM groups WHERE chat_id = ?", (chat_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0]:
            leave_msg = result[0].replace('{name}', update.message.left_chat_member.first_name).replace('{group}', update.effective_chat.title)
        else:
            leave_msg = LEAVE_MESSAGE.replace(CHANNEL_NAME, update.effective_chat.title)
            leave_msg = leave_msg.replace('{name}', update.message.left_chat_member.first_name)
        
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
    if filter_links == 1 and re.search(r'https?://|t\.me/|www\.', message_text, re.IGNORECASE):
        try:
            update.message.delete()
            warning_msg = f"{EMOJIS['warning']} *Links are not allowed here!* {EMOJIS['warning']}"
            context.bot.send_message(
                chat_id=chat_id,
                text=warning_msg,
                reply_to_message_id=update.message.message_id
            )
        except Exception as e:
            logger.error(f"Error deleting message: {e}")
        finally:
            conn.close()
            return
    
    # Sexual content filter
    sexual_keywords = ['porn', 'xxx', 'adult', 'nsfw', 'sex', 'nude', 'naked', 'porno']
    if filter_sexual == 1 and any(keyword in message_text.lower() for keyword in sexual_keywords):
        try:
            update.message.delete()
            warning_msg = f"{EMOJIS['warning']} *Inappropriate content detected!* {EMOJIS['warning']}"
            context.bot.send_message(
                chat_id=chat_id,
                text=warning_msg,
                reply_to_message_id=update.message.message_id
            )
        except Exception as e:
            logger.error(f"Error deleting message: {e}")
    
    conn.close()

def help_command(update: Update, context: CallbackContext):
    help_text = f"""
{EMOJIS['help']} *Need Help?* {EMOJIS['help']}

{EMOJIS['info']} *Quick Guide:*
• Use /start to begin
• Use /list to see all commands
• Use /settings for group configuration

{EMOJIS['message']} *For Support:*
Contact {OWNER_USERNAME} for any issues or questions.

{EMOJIS['technology']} *About This Bot:*
This bot helps manage your groups with advanced features like welcome messages, content filtering, and user management.
    """
    
    update.message.reply_text(
        help_text,
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
    dp.add_handler(CommandHandler("settings", list_commands))  # Redirect to list
    dp.add_handler(CommandHandler("list", list_commands))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("setwelcome", set_welcome))
    dp.add_handler(CommandHandler("setleave", set_leave))
    dp.add_handler(CommandHandler("filterlinks", filter_links))
    dp.add_handler(CommandHandler("filtercontent", filter_content))
    
    dp.add_handler(CallbackQueryHandler(button_handler))
    
    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, handle_new_chat_members))
    dp.add_handler(MessageHandler(Filters.status_update.left_chat_member, handle_left_chat_member))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, message_filter))
    
    # Start the Bot
    print("Bot is running...")
    updater.start_polling()
    
    # Run the bot until you press Ctrl-C
    updater.idle()

if __name__ == '__main__':
    main()
