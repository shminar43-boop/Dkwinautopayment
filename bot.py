import logging
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters

# ==================== কনফিগারেশন (আপনার তথ্য দিন) ====================
BOT_TOKEN = "8887502071:AAE20aePqQgR8FdQ8HqgNH2RHfXaY7SM0Ho"  # BotFather থেকে পাওয়া টোকেন বসান
ADMIN_ID = 6776006196  # @userinfobot থেকে পাওয়া আপনার আইডি বসান
# ====================================================================

# ডাটাবেজ (মেমোরি)
users_db = {}

# /start কমান্ড হ্যান্ডলার
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    
    # নতুন ইউজারের তথ্য তৈরি
    if user_id not in users_db:
        users_db[user_id] = {"expiry": datetime.now(), "status": "expired"}
        
    user_info = users_db[user_id]
    expiry_str = user_info['expiry'].strftime('%Y-%m-%d') if user_info['status'] == "active" else "মেয়াদ নেই"
    
    msg = (
        f"👋 **স্বাগতম আমাদের এজেন্ট সার্ভিসে!**\n\n"
        f"📌 আপনার বর্তমান মেয়াদ: **{expiry_str}**\n"
        f"📌 স্ট্যাটাস: **{user_info['status'].upper()}**\n\n"
        f"পেমেন্ট রিনিউ বা অ্যাকাউন্ট Revive করতে নিচের বাটনে চাপ দিন।"
    )
    
    keyboard = [[InlineKeyboardButton("💳 Pay & Revive Subscription", callback_data="req_pay")]]
    await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

# বাটন ক্লিক হ্যান্ডলার
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "req_pay":
        context.user_data['waiting_for_trx'] = True
        pay_instruction = (
            "📲 **পেমেন্ট নির্দেশিকা:**\n\n"
            "১. আমাদের bKash/Nagad Personal নম্বরে পেমেন্ট করুন: `01870156643` (Send Money)\n"
            "২. পেমেন্ট শেষে আপনার **মোবাইল নম্বর** এবং **TrxID** লিখে একসাথে মেসেজ পাঠান।\n\n"
            "উদাহরণ: `01711223344 TrxID: A1B2C3D4`"
        )
        await query.edit_message_text(pay_instruction, parse_mode="Markdown")

    elif query.data.startswith("approve_"):
        user_id = int(query.data.split("_")[1])
        current_expiry = users_db.get(user_id, {}).get("expiry", datetime.now())
        
        # বর্তমান মেয়াদ শেষ হয়ে থাকলে আজ থেকে ৩০ দিন, আর মেয়াদ থাকলে আগের মেয়াদের সাথে ৩০ দিন যোগ
        new_expiry = max(datetime.now(), current_expiry) + timedelta(days=30)
        users_db[user_id] = {"expiry": new_expiry, "status": "active"}
        
        # কাস্টমারকে সফল মেসেজ পাঠানো
        await context.bot.send_message(
            chat_id=user_id, 
            text=f"🎉 **আপনার পেমেন্ট অনুমোদন করা হয়েছে!**\n\nনতুন মেয়াদের শেষ তারিখ: **{new_expiry.strftime('%Y-%m-%d')}**",
            parse_mode="Markdown"
        )
        await query.edit_message_text(f"✅ Approved User ID: {user_id}")

    elif query.data.startswith("reject_"):
        user_id = int(query.data.split("_")[1])
        await context.bot.send_message(
            chat_id=user_id, 
            text="❌ **আপনার পেমেন্ট তথ্য সঠিক নয়।** অনুগ্রহ করে সঠিক TrxID সহ আবার চেষ্টা করুন।"
        )
        await query.edit_message_text(f"❌ Rejected User ID: {user_id}")

# ইউজারের ট্রানজেকশন তথ্য রিসিভ করা
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    text = update.message.text

    if context.user_data.get('waiting_for_trx'):
        context.user_data['waiting_for_trx'] = False
        
        # এজেন্টের (আপনার) কাছে অনুমোদনের জন্য মেসেজ পাঠানো
        admin_keyboard = [
            [
                InlineKeyboardButton("✅ Approve (30 Days)", callback_data=f"approve_{user.id}"),
                InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user.id}")
            ]
        ]
        
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"📥 **নতুন পেমেন্ট রিকোয়েস্ট!**\n\nইউজার: @{user.username} (ID: `{user.id}`)\nতথ্য: {text}",
            reply_markup=InlineKeyboardMarkup(admin_keyboard),
            parse_mode="Markdown"
        )
        
        await update.message.reply_text("✅ আপনার পেমেন্ট তথ্য জমা নেওয়া হয়েছে। এজেন্ট ভেরিফাই করে অনুমোদন দিলেই মেয়াদ আপডেট হয়ে যাবে।")

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Bot is running successfully...")
    app.run_polling()