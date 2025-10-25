import os
import sys

def kill_existing_bots():
    """Kill any existing Python processes"""
    try:
        if os.name == 'nt':  # Windows
            os.system('taskkill /f /im python.exe')
        else:  # Linux/Mac
            os.system('pkill -f python')
        print("✅ Existing bot instances terminated")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    kill_existing_bots()
    print("🚀 Now run your bot with: python bot.py")
