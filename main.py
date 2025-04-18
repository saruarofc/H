import os
import logging
from pytube import YouTube
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Enable logging
logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")  # Set this in Koyeb or .env

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Send me a YouTube link and I’ll download the video for you.")

# Handle YouTube links
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    try:
        await update.message.reply_text("Downloading... Please wait.")
        yt = YouTube(url)
        stream = yt.streams.get_highest_resolution()
        file_path = stream.download(filename="video.mp4")
        
        with open(file_path, 'rb') as video:
            await update.message.reply_video(video)
        
        os.remove(file_path)  # Clean up
    except Exception as e:
        logging.error(e)
        await update.message.reply_text("Failed to download video. Please make sure the link is correct.")

# Main app
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
