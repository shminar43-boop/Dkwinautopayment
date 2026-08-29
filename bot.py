import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters

# ==================== কনফিগারেশন ====================
BOT_TOKEN = "8887502071:AAE20aePqQgR8FdQ8HqgNH2RHfXaY7SM0Ho"
ADMIN_ID = 6776006196
PAYMENT_NUMBER = "01870156643"  # বিকাশ / নগদ নম্বর
SUPPORT_USERNAME = "Minaradmin"  # সাপোর্ট ইউজারনেম
# ====================================================

# /start কমান্ড হ্যান্ডলার
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_id = user.id
    
    msg = (
        f"💎 **— OFFICIAL PAYMENT PORTAL —**\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 **গ্রাহক:** {user.full_name}\n"
        f"🆔 **ইউজার আইডি:** `{user_id}`\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📲 **পেমেন্ট সম্পূর্ণ করতে বা তথ্য জমা দিতে নিচের বাটনে ক্লিক করুন।**"
    )
    
    keyboard = [
        [InlineKeyboardButton("💳 Make Payment / Send TrxID", callback_data="req_pay")],
        [
            InlineKeyboardButton("📞 Help & Support", url=f"https://t.me/{SUPPORT_USERNAME}"),
            InlineKeyboardButton("🔄 Refresh Portal", callback_data="refresh")
        ]
    ]
    
    await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

# বাটন ক্লিক হ্যান্ডলার
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "req_pay":
        context.user_data['waiting_for_trx'] = True
        
        pay_instruction = (
            f"📥 **— PAYMENT INSTRUCTIONS —**\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🔹 **পেমেন্ট মেথড:** bKash / Nagad (Personal)\n"
            f"📱 **এজেন্ট/ব্যক্তিগত নম্বর:** `{PAYMENT_NUMBER}`\n"
            f"📌 **টাইপ:** Send Money\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📝 **কিভাবে জমা দিবেন:**\n"
            f"উপরে দেওয়া নম্বরে পেমেন্ট সম্পূর্ণ করে আপনার **মোবাইল নম্বর** এবং **TrxID** বা টাকার পরিমাণ এক মেসেজে লিখে পাঠান।\n\n"
            f"💡 *উদাহরণ:* `01711223344 TrxID: A1B2C3D4 Amount: 500`"
        )
        
        keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="back_home")]]
        await query.edit_message_text(pay_instruction, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif query.data == "back_home":
        user = query.from_user
        user_id = user.id
        
        msg = (
            f"💎 **— OFFICIAL PAYMENT PORTAL —**\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 **গ্রাহক:** {user.full_name}\n"
            f"🆔 **ইউজার আইডি:** `{user_id}`\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📲 **পেমেন্ট সম্পূর্ণ করতে বা তথ্য জমা দিতে নিচের বাটনে ক্লিক করুন।**"
        )
        
        keyboard = [
            [InlineKeyboardButton("💳 Make Payment / Send TrxID", callback_data="req_pay")],
            [
                InlineKeyboardButton("📞 Help & Support", url=f"https://t.me/{SUPPORT_USERNAME}"),
                InlineKeyboardButton("🔄 Refresh Portal", callback_data="refresh")
            ]
        ]
        await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif query.data == "refresh":
        await query.answer("পোর্টাল রিফ্রেশ করা হয়েছে!", show_alert=True)

    elif query.data.startswith("approve_"):
        user_id = int(query.data.split("_")[1])
        
        await context.bot.send_message(
            chat_id=user_id, 
            text=(
                f"✅ **PAYMENT RECEIVED & CONFIRMED!**\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"আপনার পেমেন্ট সফলভাবে গ্রহণ ও অনুমোদন করা হয়েছে।\n\n"
                f"ধন্যবাদ আমাদের সেবা গ্রহণ করার জন্য! 🤝"
            ),
            parse_mode="Markdown"
        )
        await query.edit_message_text(f"✅ Payment Approved for User ID: {user_id}")

    elif query.data.startswith("reject_"):
        user_id = int(query.data.split("_")[1])
        await context.bot.send_message(
            chat_id=user_id, 
            text=(
                f"❌ **PAYMENT VERIFICATION FAILED!**\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"আপনার প্রদানকৃত TrxID বা পেমেন্ট তথ্যটি মেলেনি।\n"
                f"অনুগ্রহ করে সঠিক তথ্য দিয়ে পুনরায় চেষ্টা করুন অথবা সাপোর্টে যোগাযোগ করুন।"
            ),
            parse_mode="Markdown"
        )
        await query.edit_message_text(f"❌ Payment Rejected for User ID: {user_id}")

# ইউজারের ট্রানজেকশন তথ্য রিসিভ করা
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    text = update.message.text

    if context.user_data.get('waiting_for_trx'):
        context.user_data['waiting_for_trx'] = False
        
        admin_keyboard = [
            [
                InlineKeyboardButton("✅ Confirm Payment", callback_data=f"approve_{user.id}"),
                InlineKeyboardButton("❌ Reject Payment", callback_data=f"reject_{user.id}")
            ]
        ]
        
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=(
                f"🔔 **NEW PAYMENT SUBMISSION**\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"👤 **গ্রাহক:** {user.full_name} (@{user.username})\n"
                f"🆔 **ID:** `{user.id}`\n"
                f"📄 **পেমেন্ট তথ্য:** `{text}`\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━"
            ),
            reply_markup=InlineKeyboardMarkup(admin_keyboard),
            parse_mode="Markdown"
        )
        
        await update.message.reply_text(
            "⏳ **আপনার পেমেন্ট তথ্য জমা নেওয়া হয়েছে!**\nএজেন্ট ভেরিফাই করে খুব দ্রুত পেমেন্ট কনফার্ম করে দিবে।",
            parse_mode="Markdown"
        )

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Payment Portal Bot is running...")
    app.run_polling()                f"🗓️ **নতুন মেয়াদ:** `{new_expiry.strftime('%d %b, %Y')}` (৩০ দিন)\n\n"
                f"আমাদের সাথে থাকার জন্য ধন্যবাদ! 🤝"
            ),
            parse_mode="Markdown"
        )
        await query.edit_message_text(f"✅ Approved User ID: {user_id}")

    elif query.data.startswith("reject_"):
        user_id = int(query.data.split("_")[1])
        await context.bot.send_message(
            chat_id=user_id, 
            text=(
                f"❌ **PAYMENT REJECTED!**\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"আপনার প্রদানকৃত TrxID বা তথ্যটি সঠিক নয়।\n"
                f"অনুগ্রহ করে সঠিক তথ্য দিয়ে পুনরায় চেষ্টা করুন অথবা সাপোর্টে যোগাযোগ করুন।"
            ),
            parse_mode="Markdown"
        )
        await query.edit_message_text(f"❌ Rejected User ID: {user_id}")

# ইউজারের ট্রানজেকশন তথ্য রিসিভ করা
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    text = update.message.text

    if context.user_data.get('waiting_for_trx'):
        context.user_data['waiting_for_trx'] = False
        
        admin_keyboard = [
            [
                InlineKeyboardButton("✅ Approve (30 Days)", callback_data=f"approve_{user.id}"),
                InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user.id}")
            ]
        ]
        
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=(
                f"🔔 **NEW PAYMENT REQUEST**\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"👤 **ইউজার:** {user.full_name} (@{user.username})\n"
                f"🆔 **ID:** `{user.id}`\n"
                f"📄 **তথ্য:** `{text}`\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━"
            ),
            reply_markup=InlineKeyboardMarkup(admin_keyboard),
            parse_mode="Markdown"
        )
        
        await update.message.reply_text(
            "⏳ **আপনার পেমেন্ট তথ্য জমা নেওয়া হয়েছে!**\nঅ্যাডমিন ভেরিফাই করে দ্রুততম সময়ের মধ্যে আপনার সার্ভিস রিনিউ করে দিবে।",
            parse_mode="Markdown"
        )

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Bot is running with updated Admin Config...")
    app.run_polling()
