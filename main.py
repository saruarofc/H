import os
import logging
import subprocess
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Set your Telegram Bot API token here
TOKEN = 'YOUR_BOT_TOKEN'
CHAT_ID = 'USER_CHAT_ID'  # Optionally, specify a specific user chat_id to send messages to

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Directory to store the uploaded PHP files
UPLOAD_DIR = '/path/to/your/koyeb/app/storage/'

# Start command to test the bot is working
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Hello! Send me a PHP file and I will execute it.')

# Function to handle file uploads
def handle_document(update: Update, context: CallbackContext) -> None:
    # Check if the message contains a document (i.e., PHP file)
    if update.message.document:
        file = update.message.document
        file_id = file.file_id
        file_name = file.file_name
        
        # Get file info from Telegram API
        file_info = context.bot.get_file(file_id)
        file_path = file_info.file_path
        
        # Download the file to a local directory on the server (Koyeb)
        file_info.download(os.path.join(UPLOAD_DIR, file_name))

        # Send acknowledgment to the user
        update.message.reply_text(f'File "{file_name}" uploaded successfully!')

        # Execute the PHP file
        execute_php_file(file_name, update)

# Function to execute the uploaded PHP file
def execute_php_file(file_name: str, update: Update) -> None:
    php_file_path = os.path.join(UPLOAD_DIR, file_name)
    
    try:
        # Run the uploaded PHP file using PHP CLI
        result = subprocess.run(['php', php_file_path], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            # If execution is successful, send the output back
            output = result.stdout
        else:
            # If there's an error during execution
            output = f"Error during execution:\n{result.stderr}"

        # Send the output or error back to the user
        update.message.reply_text(f'Execution Output:\n{output}')
        
        # Optionally, delete the file after execution to save space
        os.remove(php_file_path)

    except subprocess.TimeoutExpired:
        # If the PHP script takes too long
        update.message.reply_text('Error: The PHP script took too long to execute!')
        os.remove(php_file_path)
    except Exception as e:
        update.message.reply_text(f"Error: {str(e)}")
        os.remove(php_file_path)

# Main function to start the bot
def main():
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    
    # Command handler for `/start`
    dispatcher.add_handler(CommandHandler("start", start))
    
    # Message handler to handle documents (PHP files)
    dispatcher.add_handler(MessageHandler(Filters.document.mime_type("application/x-php"), handle_document))
    
    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
