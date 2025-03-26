import telegram
from telegram.ext import Application, MessageHandler, filters
import google.generativeai as genai
from dotenv import load_dotenv
import os
from PyPDF2 import PdfReader

# Load secrets from .env file
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Set up Gemini API
genai.configure(api_key=GOOGLE_API_KEY)

# Function to handle text messages
async def handle_text(update: telegram.Update, context):
    user_message = update.message.text
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(user_message)
        await update.message.reply_text(response.text.strip())
    except Exception as e:
        await update.message.reply_text("Oops, something went wrong. Try again!")

# Function to handle document uploads (like a CV)
async def handle_document(update: telegram.Update, context):
    document = update.message.document
    file_name = document.file_name
    try:
        # Download the file
        file = await document.get_file()
        file_path = f"downloaded_{file_name}"
        await file.download_to_drive(file_path)
        
        # Extract text if it’s a PDF
        if file_name.endswith(".pdf"):
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""  # Handle empty pages
            model = genai.GenerativeModel("gemini-1.5-flash")
            prompt = f"Here’s my CV text:\n{text}\nPlease summarize it or suggest edits."
            response = model.generate_content(prompt)
            await update.message.reply_text(response.text.strip())
        else:
            await update.message.reply_text(f"Got your CV: {file_name}! I can only process PDFs for now.")
    except Exception as e:
        await update.message.reply_text(f"Error with your CV: {str(e)}")

# Function to handle image uploads
async def handle_image(update: telegram.Update, context):
    photo = update.message.photo[-1]  # Get the highest resolution image
    file_name = f"image_{photo.file_id}.jpg"
    try:
        # Download the image
        file = await photo.get_file()
        file_path = f"downloaded_{file_name}"
        await file.download_to_drive(file_path)
        
        # Placeholder response (Gemini 1.5 Flash can’t analyze images)
        await update.message.reply_text(f"Got your image: {file_name}! I can’t describe it yet. What do you want me to do?")
    except Exception as e:
        await update.message.reply_text(f"Error with your image: {str(e)}")

# Set up the bot
application = Application.builder().token(TELEGRAM_TOKEN).build()

# Add handlers
application.add_handler(MessageHandler(filters.TEXT, handle_text))          # For text
application.add_handler(MessageHandler(filters.Document.ALL, handle_document))  # For documents
application.add_handler(MessageHandler(filters.PHOTO, handle_image))        # For images

# Start the bot
print("Bot is running...")
application.run_polling()