import os
import logging
import subprocess
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters

# Set your Telegram Bot API token and webhook URL from environment variables
TOKEN = os.getenv('BOT_TOKEN')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')
UPLOAD_DIR = '/tmp/uploads/'  # temp folder to save PHP files

# Create upload directory if not exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app and Telegram Bot
app = Flask(__name__)
bot = Bot(TOKEN)

# Telegram command: /start
def start(update: Update, context) -> None:
    update.message.reply_text('Send me a PHP file and I will execute it.')

# Handle uploaded PHP files
def handle_document(update: Update, context) -> None:
    if update.message.document:
        file = update.message.document
        file_id = file.file_id
        file_name = file.file_name

        # Download file
        file_info = bot.get_file(file_id)
        file_path = os.path.join(UPLOAD_DIR, file_name)
        file_info.download(custom_path=file_path)

        update.message.reply_text(f'File "{file_name}" uploaded. Executing...')

        execute_php_file(file_name, update)

# Execute the PHP file and return output
def execute_php_file(file_name: str, update: Update) -> None:
    path = os.path.join(UPLOAD_DIR, file_name)
    try:
        result = subprocess.run(['php', path], capture_output=True, text=True, timeout=20)
        output = result.stdout if result.returncode == 0 else result.stderr
        update.message.reply_text(f'Result:\n{output[:4000]}')  # Telegram max msg size limit
    except subprocess.TimeoutExpired:
        update.message.reply_text("Error: Script timed out!")
    except Exception as e:
        update.message.reply_text(f"Execution failed:\n{str(e)}")
    finally:
        os.remove(path)

# Handle incoming webhook updates
@app.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return 'OK'

# Set webhook on Telegram
def set_webhook():
    if WEBHOOK_URL:
        bot.set_webhook(url=WEBHOOK_URL + '/webhook')
        print("Webhook set to:", WEBHOOK_URL + '/webhook')
    else:
        print("WEBHOOK_URL environment variable not set!")

# Init dispatcher and handlers
def main():
    global dispatcher
    from telegram.ext import Dispatcher
    dispatcher = Dispatcher(bot, None, workers=0, use_context=True)
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.document.mime_type("application/x-php"), handle_document))
    set_webhook()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))

if __name__ == '__main__':
    main()
