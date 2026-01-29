from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)
from PIL import Image
import os

# 🔑 PASTE YOUR NEW TOKEN HERE
BOT_TOKEN = "8463517091:AAF34S4bkJrAq96-VLStneMkMg5o1PjY7Jo"

user_images = {}
TEMP_DIR = "temp"
os.makedirs(TEMP_DIR, exist_ok=True)


# 🔘 BUTTON MENU
def main_menu():
    keyboard = [
        [InlineKeyboardButton("📄 Create PDF", callback_data="make_pdf")],
        [InlineKeyboardButton("🧹 Clear Images", callback_data="clear_images")],
        [InlineKeyboardButton("ℹ️ Help", callback_data="help")]
    ]
    return InlineKeyboardMarkup(keyboard)


# 🚀 START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to PNG → PDF Bot\n\n"
        "📸 Send images\n"
        "👇 Use buttons below",
        reply_markup=main_menu()
    )


# 📸 IMAGE HANDLER
async def image_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id

    if chat_id not in user_images:
        user_images[chat_id] = []

    photo = update.message.photo[-1]
    file = await photo.get_file()

    image_path = f"{TEMP_DIR}/{chat_id}_{photo.file_id}.jpg"
    await file.download_to_drive(image_path)

    user_images[chat_id].append(image_path)
    await update.message.reply_text("✅ Image received", reply_markup=main_menu())


# 🔘 BUTTON HANDLER
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    chat_id = query.message.chat_id

    if query.data == "make_pdf":
        if chat_id not in user_images or not user_images[chat_id]:
            await query.message.reply_text("❌ No images received")
            return

        images = [Image.open(img).convert("RGB") for img in user_images[chat_id]]
        pdf_path = f"{TEMP_DIR}/{chat_id}.pdf"

        images[0].save(pdf_path, save_all=True, append_images=images[1:])
        await query.message.reply_document(open(pdf_path, "rb"))

        for img in user_images[chat_id]:
            os.remove(img)
        os.remove(pdf_path)
        user_images.pop(chat_id)

    elif query.data == "clear_images":
        if chat_id in user_images:
            for img in user_images[chat_id]:
                os.remove(img)
            user_images.pop(chat_id)

        await query.message.reply_text("🧹 Images cleared", reply_markup=main_menu())

    elif query.data == "help":
        await query.message.reply_text(
            "📌 How to use:\n\n"
            "1️⃣ Send images 📸\n"
            "2️⃣ Tap 📄 Create PDF\n"
            "3️⃣ Get PDF 📄",
            reply_markup=main_menu()
        )


# ⚙️ APP SETUP
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.PHOTO, image_handler))
app.add_handler(CallbackQueryHandler(button_handler))

app.run_polling()
