import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from .database import SessionLocal
from .crud import create_order, get_pending_orders, mark_all_bought
from .sessions import start_session, get_session, clear_session
from .schemas import OrderCreate
from sqlalchemy.exc import SQLAlchemyError

TOKEN = os.getenv("TELEGRAM_TOKEN")
is_open = True

async def order_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global is_open

    if not is_open:
        await update.message.reply_text("❌ ការកក់ត្រូវបានបិទ។ សូមទាក់ទងម្ចាស់ដើម្បីបើកឡើងវិញ។")
        return

    start_session(update.message.from_user.id)
    await update.message.reply_text("តែជ្រក់ហេ?\n\nសូមបញ្ចូលឈ្មោះផលិតផលដែលអ្នកចង់បញ្ជាទិញ។")

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message or not update.message.text:
        return

    user_id = update.message.from_user.id
    session = get_session(user_id)

    if not session:
        return

    # ===============================
    # STEP 1: PRODUCT
    # ===============================
    if session["step"] == "product":
        session["product"] = update.message.text.strip()
        session["step"] = "quantity"
        await update.message.reply_text("ចង់បានម៉ាន ប្រូប្រូ ស៊ីសស៊ីស")
        return

    # ===============================
    # STEP 2: QUANTITY
    # ===============================
    if session["step"] == "quantity":

        try:
            quantity = int(update.message.text)

            if quantity <= 0:
                raise ValueError()

        except ValueError:
            await update.message.reply_text("វាគ្មានអាណាកម្មង់ ០ ទេ")
            return

        session["quantity"] = quantity
        session["step"] = "buyer"

        await update.message.reply_text("ណាគេហ្នឹង?")
        return

    # ===============================
    # STEP 3: BUYER
    # ===============================
    if session["step"] == "buyer":

        db = SessionLocal()

        try:
            order_data = OrderCreate(
                chat_id=update.message.chat.id,
                user_id=user_id,
                product=session["product"],
                quantity=session["quantity"],
                buyer=update.message.text.strip(),
            )

            create_order(db, order_data)

        except SQLAlchemyError:
            await update.message.reply_text("មានបញ្ហាក្នុងការរក្សាទុកការបញ្ជាទិញ។ សូមព្យាយាមម្តងទៀត។")
            db.close()
            return

        db.close()
        clear_session(user_id)

        await update.message.reply_text(
            f"ដោយមួយទុកចំណាំ\n\n"
            f"🧋 {session['product']}\n"
            f"🔢 {session['quantity']}\n"
            f"👤 {update.message.text.strip()}"
        )

async def show_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = SessionLocal()
    orders = get_pending_orders(db)
    db.close()

    if not orders:
        await update.message.reply_text("អត់អ្នកផឹកសោះ")
        return

    msg = "កំពុងចាំនាក\n\n"
    summary = {}

    for o in orders:
        msg += f"{o.product} x{o.quantity} - {o.buyer}\n"
        summary[o.product] = summary.get(o.product, 0) + o.quantity

    msg += "\n📊 ចាំមើលគេប្រាប់\n"
    for k, v in summary.items():
        msg += f"{k}: {v}\n"

    await update.message.reply_text(msg)

async def bought_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = SessionLocal()
    mark_all_bought(db)
    db.close()
    await update.message.reply_text("ទិញហើយហៃ")

async def close_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global is_open
    is_open = False
    await update.message.reply_text("ឈប់កក់ហើយ។ សូមទាក់ទងម្ចាស់ដើម្បីបើកឡើងវិញ។")

async def open_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global is_open
    is_open = True
    await update.message.reply_text("បើកការកក់វិញហើយ។")

def build_application():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("order", order_command))
    app.add_handler(CommandHandler("show", show_command))
    app.add_handler(CommandHandler("bought", bought_command))
    app.add_handler(CommandHandler("close", close_command))
    app.add_handler(CommandHandler("open", open_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    return app