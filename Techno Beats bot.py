import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import sqlite3
from datetime import datetime, timedelta
import os

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Database setup
def init_db():
    conn = sqlite3.connect('bot_business.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            chat_id INTEGER,
            join_date TIMESTAMP,
            is_approved BOOLEAN DEFAULT TRUE,
            last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            total_messages INTEGER DEFAULT 0
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            user_id INTEGER PRIMARY KEY,
            username TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_activity (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            activity_type TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Add yourself as admin (YOUR_USER_ID daalein)
    cursor.execute('INSERT OR IGNORE INTO admins (user_id) VALUES (?)', (123456789,))
    
    conn.commit()
    conn.close()

# Auto approve user
def auto_approve_user(user, chat_id):
    conn = sqlite3.connect('bot_business.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT OR REPLACE INTO users 
        (user_id, username, first_name, last_name, chat_id, join_date, is_approved)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (user.id, user.username, user.first_name, user.last_name, chat_id, datetime.now(), True))
    
    conn.commit()
    conn.close()
    return True

# Start command
def start(update: Update, context: CallbackContext):
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    # Auto approve user
    auto_approve_user(user, chat_id)
    
    welcome_text = f"""
    🎉 **Welcome to Bot Business, {user.first_name}!** 🎉

    ✅ **You are automatically approved!**
    
    🤖 **Available Commands:**
    /myinfo - Your information
    /help - Help menu
    
    💬 You can start using the bot immediately!
    """
    update.message.reply_text(welcome_text, parse_mode='Markdown')

# User info
def user_info(update: Update, context: CallbackContext):
    user = update.effective_user
    
    conn = sqlite3.connect('bot_business.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT join_date, total_messages FROM users WHERE user_id = ?', (user.id,))
    user_data = cursor.fetchone()
    conn.close()
    
    join_date = user_data[0] if user_data else "N/A"
    total_messages = user_data[1] if user_data else 0
    
    info_text = f"""
    👤 **User Information:**

    🆔 User ID: `{user.id}`
    👤 Name: {user.first_name} {user.last_name or ''}
    📛 Username: @{user.username or 'N/A'}
    💬 Chat ID: `{update.effective_chat.id}`
    ✅ Status: Auto Approved
    📅 Join Date: {join_date}
    💬 Total Messages: {total_messages}
    """
    update.message.reply_text(info_text, parse_mode='Markdown')

# Track messages
def track_message(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    conn = sqlite3.connect('bot_business.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE users 
        SET last_active = ?, total_messages = total_messages + 1 
        WHERE user_id = ?
    ''', (datetime.now(), user_id))
    
    conn.commit()
    conn.close()

# Broadcast message
def broadcast(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        update.message.reply_text("❌ Admin access required!")
        return
    
    if not context.args:
        update.message.reply_text("Usage: /broadcast <message>")
        return
    
    message = ' '.join(context.args)
    conn = sqlite3.connect('bot_business.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT chat_id FROM users')
    users = cursor.fetchall()
    conn.close()
    
    success_count = 0
    for user in users:
        try:
            context.bot.send_message(chat_id=user[0], text=f"📢 Broadcast:\n\n{message}")
            success_count += 1
        except Exception as e:
            logger.error(f"Failed to send to {user[0]}: {e}")
    
    update.message.reply_text(f"📢 Broadcast sent to {success_count} users!")

# Active users
def active_users(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        update.message.reply_text("❌ Admin access required!")
        return
    
    conn = sqlite3.connect('bot_business.db')
    cursor = conn.cursor()
    
    time_threshold = datetime.now() - timedelta(hours=24)
    cursor.execute('''
        SELECT user_id, username, first_name, last_active, total_messages 
        FROM users 
        WHERE last_active > ?
        ORDER BY last_active DESC
    ''', (time_threshold,))
    
    active_users = cursor.fetchall()
    conn.close()
    
    if not active_users:
        update.message.reply_text("❌ No active users in last 24 hours!")
        return
    
    response = "👥 **Active Users (Last 24 hours)**\n\n"
    for idx, user in enumerate(active_users, 1):
        user_id, username, first_name, last_active, total_messages = user
        response += f"{idx}. **{first_name}**"
        if username:
            response += f" (@{username})"
        response += f" - {total_messages} msgs\n"
    
    update.message.reply_text(response, parse_mode='Markdown')

# Admin check
def is_admin(user_id):
    conn = sqlite3.connect('bot_business.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM admins WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

# Main function
def main():
    # Initialize database
    init_db()
    
    # Get token from environment variable
    TOKEN = os.getenv('BOT_TOKEN')
    if not TOKEN:
        print("❌ BOT_TOKEN environment variable not set!")
        return
    
    # Create updater
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    
    # Add handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("myinfo", user_info))
    dispatcher.add_handler(CommandHandler("broadcast", broadcast))
    dispatcher.add_handler(CommandHandler("activeusers", active_users))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, track_message))
    
    # Start bot
    updater.start_polling()
    print("🤖 Bot Business is running...")
    updater.idle()

if __name__ == '__main__':
    main()