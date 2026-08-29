import logging
import asyncio
import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ChatAction
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters

# ==================== কনফিগারেশন ====================
BOT_TOKEN = "8887502071:AAE20aePqQgR8FdQ8HqgNH2RHfXaY7SM0Ho"
ADMIN_ID = 6776006196  # আপনার অ্যাডমিন আইডি
PAYMENT_NUMBER = "01870156643"  # বিকাশ / নগদ নম্বর
SUPPORT_USERNAME = "Minaradmin"  # সাপোর্ট ইউজারনেম

# অ্যানিমেটেড ব্যানার লিংক
ANIMATED_BANNER_URL = "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExM3h2aTNld2N5OHAzcnRsbWVhdjFwdmdwNDNldzZ3d2R6bWZ4czE3biZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3oKIPnAiaMCws8nOsE/giphy.gif"
USER_DB_FILE = "users.json"
# ====================================================

# ইউজার আইডি সেভ করার ফাংশন
def load_users():
    if os.path.exists(USER_DB_FILE):
        try:
            with open(USER_DB_FILE, "r") as f:
                return set(json.load(f))
        except Exception:
            return set()
    return set()

def save_user(user_id):
    users = load_users()
    if user_id not in users:
        users.add(user_id)
        with open(USER_DB_FILE, "w") as f:
            json.dump(list(users), f)

# /start কমান্ড হ্যান্ডলার
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    chat_id = update.effective_chat.id
    
    # ইউজার আইডি সংরক্ষণ
    save_user(user.id)

    # টাইপিং অ্যানিমেশন এফেক্ট
    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    await asyncio.sleep(0.4)
    
    msg = (
        f"✨ **— OFFICIAL VIP PAYMENT PORTAL —** ✨\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 **গ্রাহক:** {user.full_name}\n"
        f"🆔 **আইডি:** `{user.id}`\n"
        f"⚡ **সিস্টেম স্ট্যাটাস:** 🟢 24/7 Active\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📲 *পেমেন্ট করতে বা লেনদেনের তথ্য পাঠাতে নিচের বাটনে চাপ দিন।* 👋"
    )
    
    keyboard = [
        [InlineKeyboardButton("💳 Make Payment / Send TrxID", callback_data="req_pay")],
        [
            InlineKeyboardButton("💬 Help & Support", url=f"https://t.me/{SUPPORT_USERNAME}"),
            InlineKeyboardButton("🔄 Live Refresh", callback_data="refresh")
        ]
    ]
    
    try:
        await update.message.reply_animation(
            animation=ANIMATED_BANNER_URL,
            caption=msg,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
    except Exception:
        await update.message.reply_text(
            text=msg,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

# অ্যাডমিন প্যানেল কমান্ড (/admin)
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("⛔ এই কমান্ডটি কেবল অ্যাডমিন ব্যবহার করতে পারবেন।")
        return

    users = load_users()
    msg = (
        f"👑 **— ADMIN CONTROL PANEL —**\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📊 **মোট রেজিস্টার্ড কাস্টমার:** `{len(users)}` জন\n"
        f"⚡ **বট স্ট্যাটাস:** 🟢 Online & Running\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📢 **সব ইউজারকে মেসেজ পাঠাতে ব্যবহার করুন:**\n"
        f"`/broadcast আপনার নোটিশের লেখা`\n\n"
        f"💡 *উদাহরণ:* `/broadcast আজ আমাদের অফার চলছে!`"
    )
    
    keyboard = [
        [InlineKeyboardButton("📊 Total Users Stats", callback_data="admin_stats")],
        [InlineKeyboardButton("🔄 Refresh Admin Panel", callback_data="admin_refresh")]
    ]
    
    await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

# ব্রডকাস্ট কমান্ড (/broadcast <মেসেজ>)
async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("⛔ এই কমান্ডটি কেবল অ্যাডমিন ব্যবহার করতে পারবেন।")
        return

    if not context.args and not update.message.reply_to_message:
        await update.message.reply_text(
            "⚠️ **মেসেজ লিখুন!**\n\n"
            "ব্যবহারের নিয়ম:\n"
            "`/broadcast আপনার মেসেজের লেখা`\n\n"
            "অথবা কোনো মেসেজে Reply করে `/broadcast` লিখুন।",
            parse_mode="Markdown"
        )
        return

    users = load_users()
    if not users:
        await update.message.reply_text("❌ কোনো ইউজার পাওয়া যায়নি।")
        return

    # রিপ্লাই করা মেসেজ নাকি টেক্সট মেসেজ তা চেক করা
    broadcast_text = " ".join(context.args) if context.args else None
    reply_to_msg = update.message.reply_to_message

    status_msg = await update.message.reply_text(f"⏳ **{len(users)} জন ইউজারের কাছে মেসেজ পাঠানো শুরু হচ্ছে...**", parse_mode="Markdown")
    
    success_count = 0
    failed_count = 0

    for uid in users:
        try:
            if reply_to_msg:
                await reply_to_msg.copy(chat_id=uid)
            else:
                await context.bot.send_message(
                    chat_id=uid,
                    text=f"📢 **— ANNOUNCEMENT —**\n━━━━━━━━━━━━━━━━━━━━━━━\n\n{broadcast_text}",
                    parse_mode="Markdown"
                )
            success_count += 1
            await asyncio.sleep(0.05)  # Telegram API Limit এড়াতে ছোট বিরতি
        except Exception:
            failed_count += 1

    await status_msg.edit_text(
        f"✅ **BROADCAST COMPLETED!**\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🟢 **সফলভাবে পাঠানো হয়েছে:** `{success_count}` জন\n"
        f"🔴 **ব্যর্থ (বট ব্লক করেছে):** `{failed_count}` জন\n"
        f"📊 **মোট কাস্টমার:** `{len(users)}` জন",
        parse_mode="Markdown"
    )

# ইউজার সংখ্যা দেখার কমান্ড (/stats)
async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    users = load_users()
    await update.message.reply_text(f"📊 **মোট কাস্টমার সংখ্যা:** `{len(users)}` জন", parse_mode="Markdown")

# বাটন ক্লিক হ্যান্ডলার
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "req_pay":
        context.user_data['waiting_for_trx'] = True
        
        loading_frames = [
            "⏳ *পেমেন্ট পোর্টাল লোড হচ্ছে...*\n`[▒▒▒▒▒▒▒▒▒▒] 0%`",
            "⚡ *পেমেন্ট নির্দেশিকা তৈরি হচ্ছে...*\n`[█████▒▒▒▒▒] 50%`",
            "✨ *পোর্টাল রেডি!*\n`[██████████] 100%`"
        ]
        
        for frame in loading_frames:
            try:
                await query.edit_message_caption(caption=frame, parse_mode="Markdown")
                await asyncio.sleep(0.15)
            except Exception:
                pass
        
        pay_instruction = (
            f"📥 **— INLINE PAYMENT INSTRUCTIONS —**\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💎 **পেমেন্ট মেথড:** bKash / Nagad (Personal)\n"
            f"📱 **এজেন্ট/ব্যক্তিগত নম্বর:** `{PAYMENT_NUMBER}`\n"
            f"🚀 **টাইপ:** Send Money\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📝 **কিভাবে জমা দিবেন:**\n"
            f"উপরে দেওয়া নম্বরে পেমেন্ট সম্পূর্ণ করে আপনার **মোবাইল নম্বর** এবং **TrxID** বা টাকার পরিমাণ এক মেসেজে লিখে পাঠান।\n\n"
            f"💡 *উদাহরণ:* `01711223344 TrxID: A1B2C3D4 Amount: 500`"
        )
        
        keyboard = [[InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_home")]]
        await query.edit_message_caption(caption=pay_instruction, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif query.data == "back_home":
        user = query.from_user
        
        msg = (
            f"✨ **— OFFICIAL VIP PAYMENT PORTAL —** ✨\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 **গ্রাহক:** {user.full_name}\n"
            f"🆔 **আইডি:** `{user.id}`\n"
            f"⚡ **সিস্টেম স্ট্যাটাস:** 🟢 24/7 Active\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📲 *পেমেন্ট করতে বা লেনদেনের তথ্য পাঠাতে নিচের বাটনে চাপ দিন।*"
        )
        
        keyboard = [
            [InlineKeyboardButton("💳 Make Payment / Send TrxID", callback_data="req_pay")],
            [
                InlineKeyboardButton("💬 Help & Support", url=f"https://t.me/{SUPPORT_USERNAME}"),
                InlineKeyboardButton("🔄 Live Refresh", callback_data="refresh")
            ]
        ]
        await query.edit_message_caption(caption=msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif query.data == "refresh":
        await query.answer("✨ পোর্টাল তথ্য রিয়েল-টাইমে আপডেট করা হয়েছে!", show_alert=True)

    elif query.data == "admin_stats":
        users = load_users()
        await query.answer(f"📊 মোট ইউজার: {len(users)} জন", show_alert=True)

    elif query.data == "admin_refresh":
        await query.answer("অ্যাডমিন ড্যাশবোর্ড আপডেট করা হয়েছে!", show_alert=True)

    elif query.data.startswith("approve_"):
        user_id = int(query.data.split("_")[1])
        await context.bot.send_message(
            chat_id=user_id, 
            text=(
                f"🎉 **PAYMENT APPROVED & CONFIRMED!** 🟢\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"✨ আপনার পেমেন্ট সফলভাবে যাচাই করে ভেরিফাই করা হয়েছে।\n\n"
                f"🤝 আমাদের সাথে থাকার জন্য ধন্যবাদ!"
            ),
            parse_mode="Markdown"
        )
        await query.edit_message_text(f"✅ Payment Approved for User ID: {user_id}")

    elif query.data.startswith("reject_"):
        user_id = int(query.data.split("_")[1])
        await context.bot.send_message(
            chat_id=user_id, 
            text=(
                f"❌ **PAYMENT VERIFICATION FAILED!** 🔴\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"আপনার প্রদানকৃত TrxID বা পেমেন্ট তথ্যটি পাওয়া যায়নি।\n"
                f"অনুগ্রহ করে সঠিক তথ্য দিয়ে আবার চেষ্টা করুন অথবা সাপোর্টে বার্তা দিন।"
            ),
            parse_mode="Markdown"
        )
        await query.edit_message_text(f"❌ Payment Rejected for User ID: {user_id}")

# ইউজারের ট্রানজেকশন তথ্য সাবমিট করা
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    text = update.message.text
    chat_id = update.effective_chat.id
    
    save_user(user.id)

    if context.user_data.get('waiting_for_trx'):
        context.user_data['waiting_for_trx'] = False
        
        await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
        status_msg = await update.message.reply_text("⏳ *ভেরিফিকেশনের জন্য সার্ভারে ডেটা প্রসেস হচ্ছে...*", parse_mode="Markdown")
        await asyncio.sleep(1.0)
        
        admin_keyboard = [
            [
                InlineKeyboardButton("✅ Confirm Payment", callback_data=f"approve_{user.id}"),
                InlineKeyboardButton("❌ Reject Payment", callback_data=f"reject_{user.id}")
            ]
        ]
        
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=(
                f"🚨 **NEW PAYMENT SUBMISSION** 🚨\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"👤 **গ্রাহক:** {user.full_name} (@{user.username})\n"
                f"🆔 **ID:** `{user.id}`\n"
                f"📄 **পেমেন্ট ডেটা:** `{text}`\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━"
            ),
            reply_markup=InlineKeyboardMarkup(admin_keyboard),
            parse_mode="Markdown"
        )
        
        await status_msg.edit_text(
            "🚀 **আপনার পেমেন্ট তথ্য সফলভাবে জমা নেওয়া হয়েছে!**\n\n"
            "⏳ *এজেন্ট টিম ভেরিফাই করে দ্রুততম সময়ে নিশ্চিত করবে।*",
            parse_mode="Markdown"
        )

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(CommandHandler("broadcast", broadcast_command))
    app.add_handler(CommandHandler("stats", stats_command))
    
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Bot with Admin Panel & Broadcast System is running...")
    app.run_polling()
