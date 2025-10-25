import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters, CallbackQueryHandler
import sqlite3
from datetime import datetime, timedelta

# Professional logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class TechnoBeatsBot:
    def __init__(self):
        self.owner_username = "@Chandan1757E"
        self.bot_username = "@TechnoBeatsBot"
        self.init_db()
    
    def init_db(self):
        conn = sqlite3.connect('techno_beats.db')
        cursor = conn.cursor()
        
        # Users table
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
        
        # Admins table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admins (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                added_date TIMESTAMP
            )
        ''')
        
        # User activity log
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_activity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                activity_type TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Channels table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS channels (
                channel_id INTEGER PRIMARY KEY,
                channel_name TEXT,
                added_date TIMESTAMP
            )
        ''')
        
        # Add main admin
        cursor.execute(
            'INSERT OR IGNORE INTO admins (user_id, username, added_date) VALUES (?, ?, ?)',
            (1614927658, 'Owner', datetime.now())
        )
        
        conn.commit()
        conn.close()
    
    def start(self, update: Update, context: CallbackContext):
        user = update.effective_user
        self.save_user(user, update.effective_chat.id)
        
        # Create contact button
        keyboard = [
            [InlineKeyboardButton("Contact Owner", url=f"https://t.me/{self.owner_username[1:]}")],
            [InlineKeyboardButton("Join Channel", url="https://t.me/your_channel_here")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        response = f"""
Welcome to Techno Beat's Official Bot

Hello {user.first_name},

Thank you for connecting with Techno Beat's. Our bot provides automated management for our channels and groups.

Available Commands:
/start - Initialize the bot
/myinfo - Display your information  
/help - Command assistance
/contact - Get owner contact details

Admin Commands:
/activeusers - View active users list
/allusers - Complete users database
/broadcast - Send message to all users
/stats - System statistics

For immediate assistance, use the contact button below.
        """
        update.message.reply_text(response, reply_markup=reply_markup)
    
    def contact_owner(self, update: Update, context: CallbackContext):
        keyboard = [
            [InlineKeyboardButton("Message Owner", url=f"https://t.me/{self.owner_username[1:]}")],
            [InlineKeyboardButton("Join Main Channel", url="https://t.me/your_channel_here")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        response = f"""
Contact Information

Owner: {self.owner_username}
Bot: {self.bot_username}

For business inquiries, collaborations, or technical support, please contact our owner directly.

We typically respond within 24 hours.

Click the button below to start a conversation.
        """
        update.message.reply_text(response, reply_markup=reply_markup)
    
    def myinfo(self, update: Update, context: CallbackContext):
        user = update.effective_user
        
        conn = sqlite3.connect('techno_beats.db')
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT join_date, total_messages FROM users WHERE user_id = ?', 
            (user.id,)
        )
        user_data = cursor.fetchone()
        conn.close()
        
        join_date = user_data[0] if user_data else "Not recorded"
        total_messages = user_data[1] if user_data else 0
        
        response = f"""
User Information

User ID: {user.id}
Name: {user.first_name} {user.last_name or ''}
Username: {f'@{user.username}' if user.username else 'Not set'}
Chat ID: {update.effective_chat.id}
Status: Verified
Registration: {join_date}
Messages Sent: {total_messages}

Techno Beat's Member
        """
        update.message.reply_text(response)
    
    def help_command(self, update: Update, context: CallbackContext):
        keyboard = [
            [InlineKeyboardButton("Contact Support", url=f"https://t.me/{self.owner_username[1:]}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        response = """
Techno Beat's Bot - Command Reference

User Commands:
/start - Initialize bot session
/myinfo - Display user profile
/help - Command information
/contact - Contact owner

Administrator Commands:
/activeusers - Recent active users (24h)
/allusers - Complete user database  
/broadcast - Global message distribution
/stats - System performance metrics

Channel Features:
• Automatic welcome messages
• Leave notification system
• Member tracking

For administrative access or channel management, contact the owner.
        """
        update.message.reply_text(response, reply_markup=reply_markup)
    
    def handle_new_chat_members(self, update: Update, context: CallbackContext):
        """Automatically send welcome message when users join channel/group"""
        for new_member in update.message.new_chat_members:
            if new_member.id != context.bot.id:  # Ignore bot itself
                chat_title = update.effective_chat.title
                
                welcome_message = f"""
Welcome to {chat_title}

Hello {new_member.first_name},

You have successfully joined {chat_title}. Thank you for becoming part of our community.

We regularly share updates, content, and announcements here. Please make sure to read the channel rules and guidelines.

If you have any questions or need assistance, feel free to contact our owner {self.owner_username}.

We're glad to have you with us!
                """
                
                try:
                    context.bot.send_message(
                        chat_id=new_member.id,
                        text=welcome_message
                    )
                except Exception as e:
                    logger.error(f"Could not send welcome message to {new_member.id}: {e}")
                    # Send in the group if DM fails
                    update.message.reply_text(
                        f"Welcome {new_member.first_name}! Please check your DM for important information."
                    )
    
    def handle_left_chat_member(self, update: Update, context: CallbackContext):
        """Automatically send message when users leave channel/group"""
        left_member = update.message.left_chat_member
        chat_title = update.effective_chat.title
        
        if left_member.id != context.bot.id:  # Ignore bot itself
            leave_message = f"""
Regarding Your Departure from {chat_title}

Hello {left_member.first_name},

We noticed you've left {chat_title}. We're sorry to see you go.

Could you share your reason for leaving? Your feedback helps us improve our community.

If you encountered any issues or have suggestions, please contact our owner {self.owner_username}. We'd appreciate the opportunity to address any concerns you might have.

Thank you for being part of our community, and we hope to welcome you back in the future.
            """
            
            try:
                context.bot.send_message(
                    chat_id=left_member.id,
                    text=leave_message
                )
            except Exception as e:
                logger.error(f"Could not send leave message to {left_member.id}: {e}")
    
    def active_users(self, update: Update, context: CallbackContext):
        if not self.is_admin(update.effective_user.id):
            update.message.reply_text("Administrator authorization required")
            return
        
        conn = sqlite3.connect('techno_beats.db')
        cursor = conn.cursor()
        
        time_threshold = datetime.now() - timedelta(hours=24)
        cursor.execute('''
            SELECT user_id, username, first_name, last_active, total_messages 
            FROM users 
            WHERE last_active > ? AND is_approved = TRUE
            ORDER BY last_active DESC
        ''', (time_threshold,))
        
        active_users = cursor.fetchall()
        conn.close()
        
        if not active_users:
            update.message.reply_text("No active users in the last 24 hours")
            return
        
        response = "Active Users - Last 24 Hours\n\n"
        
        for idx, user in enumerate(active_users, 1):
            user_id, username, first_name, last_active, total_messages = user
            last_active_time = datetime.strptime(last_active, '%Y-%m-%d %H:%M:%S.%f')
            hours_ago = int((datetime.now() - last_active_time).total_seconds() / 3600)
            
            response += f"{idx}. {first_name}"
            if username:
                response += f" (@{username})"
            response += f"\n   ID: {user_id} | Messages: {total_messages}"
            response += f"\n   Last active: {hours_ago} hours ago\n\n"
        
        update.message.reply_text(response)
    
    def all_users(self, update: Update, context: CallbackContext):
        if not self.is_admin(update.effective_user.id):
            update.message.reply_text("Administrator authorization required")
            return
        
        conn = sqlite3.connect('techno_beats.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT user_id, username, first_name, last_active, total_messages, is_approved 
            FROM users 
            ORDER BY last_active DESC
        ''')
        
        all_users = cursor.fetchall()
        conn.close()
        
        if not all_users:
            update.message.reply_text("No users in database")
            return
        
        total_users = len(all_users)
        approved_users = len([u for u in all_users if u[5]])
        
        response = f"User Database - Techno Beat's\n\n"
        response += f"Total Users: {total_users}\n"
        response += f"Verified Users: {approved_users}\n"
        response += f"Pending Verification: {total_users - approved_users}\n\n"
        
        for idx, user in enumerate(all_users[:15], 1):
            user_id, username, first_name, last_active, total_messages, is_approved = user
            status = "Verified" if is_approved else "Pending"
            
            response += f"{idx}. {first_name}"
            if username:
                response += f" (@{username})"
            response += f"\n   ID: {user_id} | Status: {status}"
            response += f" | Messages: {total_messages}\n\n"
        
        if total_users > 15:
            response += f"Displaying 15 of {total_users} users"
        
        update.message.reply_text(response)
    
    def broadcast(self, update: Update, context: CallbackContext):
        if not self.is_admin(update.effective_user.id):
            update.message.reply_text("Administrator authorization required")
            return
        
        if not context.args:
            update.message.reply_text("Usage: /broadcast <message>")
            return
        
        message = ' '.join(context.args)
        conn = sqlite3.connect('techno_beats.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT chat_id FROM users WHERE is_approved = TRUE')
        users = cursor.fetchall()
        conn.close()
        
        success_count = 0
        broadcast_message = f"Techno Beat's Announcement\n\n{message}\n\n- {self.owner_username}"
        
        for user in users:
            try:
                context.bot.send_message(chat_id=user[0], text=broadcast_message)
                success_count += 1
            except Exception as e:
                logger.error(f"Broadcast failed for {user[0]}: {e}")
        
        update.message.reply_text(f"Broadcast delivered to {success_count} users")
    
    def stats(self, update: Update, context: CallbackContext):
        if not self.is_admin(update.effective_user.id):
            update.message.reply_text("Administrator authorization required")
            return
        
        conn = sqlite3.connect('techno_beats.db')
        cursor = conn.cursor()
        
        # Total users
        cursor.execute('SELECT COUNT(*) FROM users')
        total_users = cursor.fetchone()[0]
        
        # Approved users
        cursor.execute('SELECT COUNT(*) FROM users WHERE is_approved = TRUE')
        approved_users = cursor.fetchone()[0]
        
        # Today's active users
        today = datetime.now().date()
        cursor.execute('SELECT COUNT(DISTINCT user_id) FROM user_activity WHERE DATE(timestamp) = ?', (today,))
        today_active = cursor.fetchone()[0]
        
        # Total messages
        cursor.execute('SELECT SUM(total_messages) FROM users')
        total_messages = cursor.fetchone()[0] or 0
        
        conn.close()
        
        response = f"""
Techno Beat's - System Statistics

User Metrics:
Total Users: {total_users}
Verified Users: {approved_users}
Pending Verification: {total_users - approved_users}

Activity Metrics:
Active Today: {today_active}
Total Messages: {total_messages}

Channel Management:
Automatic Welcome: Active
Leave Notifications: Active
Owner: {self.owner_username}

System Status: Operational
        """
        update.message.reply_text(response)
    
    def save_user(self, user, chat_id):
        conn = sqlite3.connect('techno_beats.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO users 
            (user_id, username, first_name, last_name, chat_id, join_date, is_approved)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user.id, user.username, user.first_name, user.last_name, chat_id, datetime.now(), True))
        
        conn.commit()
        conn.close()
    
    def track_activity(self, update: Update, context: CallbackContext):
        user_id = update.effective_user.id
        
        conn = sqlite3.connect('techno_beats.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE users 
            SET last_active = ?, total_messages = total_messages + 1 
            WHERE user_id = ?
        ''', (datetime.now(), user_id))
        
        cursor.execute('''
            INSERT INTO user_activity (user_id, activity_type) 
            VALUES (?, ?)
        ''', (user_id, "message"))
        
        conn.commit()
        conn.close()
    
    def is_admin(self, user_id):
        conn = sqlite3.connect('techno_beats.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM admins WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result is not None

def main():
    bot = TechnoBeatsBot()
    
    # Use your provided token
    TOKEN = "8280138743:AAH0YE-WfUv5yxKJHsbNaZynXy4MEnvWnjc"
    
    try:
        updater = Updater(TOKEN, use_context=True)
        dispatcher = updater.dispatcher
        
        # Command handlers
        dispatcher.add_handler(CommandHandler("start", bot.start))
        dispatcher.add_handler(CommandHandler("contact", bot.contact_owner))
        dispatcher.add_handler(CommandHandler("myinfo", bot.myinfo))
        dispatcher.add_handler(CommandHandler("help", bot.help_command))
        dispatcher.add_handler(CommandHandler("activeusers", bot.active_users))
        dispatcher.add_handler(CommandHandler("allusers", bot.all_users))
        dispatcher.add_handler(CommandHandler("broadcast", bot.broadcast))
        dispatcher.add_handler(CommandHandler("stats", bot.stats))
        
        # Message tracking
        dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, bot.track_activity))
        
        # Channel join/leave handlers
        dispatcher.add_handler(MessageHandler(Filters.status_update.new_chat_members, bot.handle_new_chat_members))
        dispatcher.add_handler(MessageHandler(Filters.status_update.left_chat_member, bot.handle_left_chat_member))
        
        logger.info("Techno Beat's Bot initializing...")
        updater.start_polling()
        logger.info("Techno Beat's Bot operational")
        updater.idle()
        
    except Exception as e:
        logger.error(f"System initialization failed: {e}")

if __name__ == '__main__':
    main()
