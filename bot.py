import os
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import sqlite3
from datetime import datetime

# Setup logging
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
    
    # Add yourself as admin - YAHAN APNA USER_ID DALEN
    YOUR_USER_ID = 1614927658  # CHANGE THIS TO YOUR ACTUAL USER ID
    cursor.execute('INSERT OR IGNORE INTO admins (user_id) VALUES (?)', (YOUR_USER_ID,))
    
    conn.commit()
    conn.close()

def start(update: Update, context: CallbackContext):
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    # Save user to database
    conn = sqlite3.connect('bot_business.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT OR REPLACE INTO users 
        (user_id, username, first_name, last_name, chat_id, join_date, is_approved)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (user.id, user.username, user.first_name, user.last_name, chat_id, datetime.now(), True))
    
    conn.commit()
    conn.close()
    
    update.message.reply_text(f"""
🎉 **Welcome to Bot Business, {user.first_name}!** 

✅ **You are automatically approved!**

🤖 **Available Commands:**
/start - Start bot
/myinfo - Your information
/help - Help menu

💬 You can start using the bot immediately!
    """, parse_mode='Markdown')

def myinfo(update: Update, context: CallbackContext):
    user = update.effective_user
    
    conn = sqlite3.connect('bot_business.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT join_date, total_messages FROM users WHERE user_id = ?', (user.id,))
    user_data = cursor.fetchone()
    conn.close()
    
    join_date = user_data[0] if user_data else "N/A"
    total_messages = user_data[1] if user_data else 0
    
    update.message.reply_text(f"""
👤 **User Information:**

🆔 User ID: `{user.id}`
👤 Name: {user.first_name} {user.last_name or ''}
📛 Username: @{user.username or 'N/A'}
💬 Chat ID: `{update.effective_chat.id}`
✅ Status: Auto Approved
📅 Join Date: {join_date}
💬 Total Messages: {total_messages}
    """, parse_mode='Markdown')

def help_command(update: Update, context: CallbackContext):
    update.message.reply_text("""
🤖 **Bot Business Help**

📝 **User Commands:**
/start - Start the bot
/myinfo - Your information
/help - This help message

🔧 **Admin Commands:**
/activeusers - Show active users
/broadcast - Send message to all users

💡 **Features:**
✅ Auto approval system
📊 User tracking
📢 Broadcast messages
👥 Group management
    """)

def main():
    # Initialize database
    init_db()
    
    # Get token from environment
    TOKEN = os.getenv('BOT_TOKEN')
    
    if not TOKEN:
        logger.error("❌ BOT_TOKEN environment variable not set!")
        return
    
    logger.info(f"✅ Token found: {TOKEN[:10]}...")
    
    try:
        updater = Updater(TOKEN, use_context=True)
        dispatcher = updater.dispatcher
        
        # Add command handlers
        dispatcher.add_handler(CommandHandler("start", start))
        dispatcher.add_handler(CommandHandler("myinfo", myinfo))
        dispatcher.add_handler(CommandHandler("help", help_command))
        
        # Start bot
        logger.info("🤖 Starting Bot Business...")
        updater.start_polling()
        logger.info("✅ Bot started successfully!")
        updater.idle()
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")

if __name__ == '__main__':
    main()
