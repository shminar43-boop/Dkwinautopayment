import logging
import asyncio
import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.constants import ChatAction
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters

# ==================== Configuration ====================
BOT_TOKEN = "8887502071:AAE20aePqQgR8FdQ8HqgNH2RHfXaY7SM0Ho"
ADMIN_ID = 6776006196  # Admin Telegram ID
PAYMENT_NUMBER = "01870156643"  # bKash / Nagad Personal Number
SUPPORT_USERNAME = "Minaradmin"  # Support Username

# Animated banner GIF URL
ANIMATED_BANNER_URL = "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExM3h2aTNld2N5OHAzcnRsbWVhdjFwdmdwNDNldzZ3d2R6bWZ4czE3biZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3oKIPnAiaMCws8nOsE/giphy.gif"
USER_DB_FILE = "users.json"
# ====================================================

# User Database Load & Save Function
def load_users():
    if os.path.exists(USER_DB_FILE):
        try:
            with open(USER_DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_user(user):
    users = load_users()
    user_id_str = str(user.id)
    users[user_id_str] = {
        "name": user.full_name,
        "username": f"@{user.username}" if user.username else "No Username"
    }
    with open(USER_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

# Telegram Bot Auto Command Menu Setup
async def post_init(application):
    await application.bot.set_my_commands([
        BotCommand("start", "🏠 মূল মেনু খুলুন"),
        BotCommand("admin", "⚙️ এডমিন প্যানেল"),
        BotCommand("users", "👥 কাস্টমার লিস্ট"),
        BotCommand("broadcast", "📢 ব্রডকাস্ট মেসেজ"),
        BotCommand("send", "✉️ ডাইরেক্ট মেসেজ"),
        BotCommand("stats", "📊 পরিসংখ্যান")
    ])

# /start Command Handler (Professional UI)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    chat_id = update.effective_chat.id
    
    save_user(user)

    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    await asyncio.sleep(0.2)
    
    msg = (
        f"┌───────────────┐\n"
        f"  💎 **VIP AUTO PAYMENT PORTAL** 💎\n"
        f"└───────────────┘\n\n"
        f"👤 **গ্রাহকের তথ্য:**\n"
        f" ┣ 📛 **নাম:** `{user.full_name}`\n"
        f" ┣ 🆔 **আইডি:** `{user.id}`\n"
        f" ┗ ⚡ **সার্ভার স্ট্যাটাস:** 🟢 `২৪/৭ অনলাইন`\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📢 **বিজ্ঞপ্তি:** আপনার যেকোনো সার্ভিস রিনিউ বা সাবস্ক্রিপশনের জন্য নিচের বাটন থেকে লেনদেন সম্পন্ন করুন।\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━"
    )
    
    keyboard = [
        [InlineKeyboardButton("💳 পেমেন্ট করুন / TrxID জমা দিন", callback_data="req_pay")],
        [
            InlineKeyboardButton("👨‍💻 লাইভ সাপোর্ট", url=f"https://t.me/{SUPPORT_USERNAME}"),
            InlineKeyboardButton("🔄 পেজ রিফ্রেশ", callback_data="refresh")
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

# Admin Panel Command (/admin)
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("⛔ **অ্যাক্সেস সংরক্ষিত:** এই কমান্ডটি শুধুমাত্র এডমিনের জন্য।")
        return

    users = load_users()
    msg = (
        f"⚡ **ADMIN DASHBOARD** ⚡\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📈 **মোট কাস্টমার:** `{len(users)}` জন\n"
        f"🟢 **বট সিস্টেম:** `স্বাভাবিক`\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🛠 **দ্রুত অ্যাকশন কমান্ড:**\n"
        f"┣ `/users` ➔ কাস্টমার লিস্ট দেখুন\n"
        f"┣ `/stats` ➔ ইউজার পরিসংখ্যান\n"
        f"┣ `/broadcast` ➔ সবাইকে মেসেজ পাঠান\n"
        f"┗ `/send` ➔ একজনকে মেসেজ পাঠান\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━"
    )
    
    keyboard = [
        [InlineKeyboardButton("📋 কাস্টমার তালিকা", callback_data="admin_user_list")],
        [
            InlineKeyboardButton("📢 ব্রডকাস্ট হেল্প", callback_data="guide_broadcast"),
            InlineKeyboardButton("✉️ ডাইরেক্ট মেসেজ হেল্প", callback_data="guide_send")
        ],
        [
            InlineKeyboardButton("📊 লাইভ স্ট্যাটস", callback_data="admin_stats"),
            InlineKeyboardButton("🔄 রিফ্রেশ", callback_data="admin_refresh")
        ]
    ]
    
    await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

# User List Show Command (/users)
async def list_users_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("⛔ এই কমান্ডটি শুধুমাত্র এডমিনের জন্য।")
        return

    users = load_users()
    if not users:
        await update.message.reply_text("❌ কোনো কাস্টমারের তথ্য পাওয়া যায়নি।")
        return

    user_list_text = f"👥 **কাস্টমার তালিকা ({len(users)} জন):**\n━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    count = 1
    for uid, udata in users.items():
        name = udata.get("name", "Unknown")
        uname = udata.get("username", "No Username")
        user_list_text += (
            f"`{count}.` 👤 **{name}** ({uname})\n"
            f"   ┗ 🆔 `{uid}` ➔ Send: `/send {uid} `\n\n"
        )
        count += 1

    if len(user_list_text) > 4000:
        for x in range(0, len(user_list_text), 4000):
            await update.message.reply_text(user_list_text[x:x+4000], parse_mode="Markdown")
    else:
        await update.message.reply_text(user_list_text, parse_mode="Markdown")

# Single User Message Command (/send <user_id> <message>)
async def send_single_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("⛔ এই কমান্ডটি শুধুমাত্র এডমিনের জন্য।")
        return

    if len(context.args) < 2:
        await update.message.reply_text(
            "⚠️ **ব্যবহারের নিয়ম:**\n\n"
            "`/send <user_id> <মেসেজ>`\n\n"
            "💡 **উদাহরণ:**\n"
            "`/send 7433409654 আপনার পেমেন্ট ভেরিফাইড হয়েছে!`",
            parse_mode="Markdown"
        )
        return

    target_user_id = context.args[0]
    message_text = " ".join(context.args[1:])

    try:
        await context.bot.send_message(
            chat_id=int(target_user_id),
            text=(
                f"📩 **অফিশিয়াল এডমিন বার্তা**\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"{message_text}\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"👨‍💻 হেল্পলাইন: @{SUPPORT_USERNAME}"
            ),
            parse_mode="Markdown"
        )
        await update.message.reply_text(
            f"✅ **মেসেজ সফলভাবে পাঠানো হয়েছে!**\n\n"
            f"👤 **প্রাপক আইডি:** `{target_user_id}`\n"
            f"💬 **মেসেজ:** {message_text}",
            parse_mode="Markdown"
        )
    except Exception as e:
        await update.message.reply_text(
            f"❌ **এরর:** মেসেজ পাঠানো সম্ভব হয়নি। (ইউজার বট ব্লক করে থাকতে পারে)\n`{e}`",
            parse_mode="Markdown"
        )

# Broadcast Command (/broadcast <message>)
async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("⛔ এই কমান্ডটি শুধুমাত্র এডমিনের জন্য।")
        return

    if not context.args and not update.message.reply_to_message:
        await update.message.reply_text(
            "⚠️ **ব্যবহারের নিয়ম:**\n\n"
            "`/broadcast <মেসেজ>`\n\n"
            "💡 **উদাহরণ:**\n"
            "`/broadcast আজকের অফার চালু হয়েছে!`",
            parse_mode="Markdown"
        )
        return

    users = load_users()
    if not users:
        await update.message.reply_text("❌ কোনো কাস্টমার পাওয়া যায়নি।")
        return

    broadcast_text = " ".join(context.args) if context.args else None
    reply_to_msg = update.message.reply_to_message

    status_msg = await update.message.reply_text(f"⏳ **{len(users)} জন ইউজারের কাছে মেসেজ পাঠানো শুরু হচ্ছে...**", parse_mode="Markdown")
    
    success_count = 0
    failed_count = 0

    for uid in users.keys():
        try:
            if reply_to_msg:
                await reply_to_msg.copy(chat_id=int(uid))
            else:
                await context.bot.send_message(
                    chat_id=int(uid),
                    text=f"📢 **বিশেষ বিজ্ঞপ্তি**\n━━━━━━━━━━━━━━━━━━━━━━━\n\n{broadcast_text}",
                    parse_mode="Markdown"
                )
            success_count += 1
            await asyncio.sleep(0.05)
        except Exception:
            failed_count += 1

    await status_msg.edit_text(
        f"✅ **ব্রডকাস্ট সম্পন্ন হয়েছে!**\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🟢 **সফল:** `{success_count}` জন\n"
        f"🔴 **ব্যর্থ:** `{failed_count}` জন\n"
        f"📊 **মোট কাস্টমার:** `{len(users)}` জন",
        parse_mode="Markdown"
    )

# User stats command (/stats)
async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    users = load_users()
    await update.message.reply_text(f"📊 **মোট রেজিস্টার্ড কাস্টমার:** `{len(users)}` জন", parse_mode="Markdown")

# Button Click Handler (Animated & Dynamic UI)
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "req_pay":
        context.user_data['waiting_for_trx'] = True
        
        loading_frames = [
            "⏳ *পেমেন্ট গেটওয়ে লোড হচ্ছে...*\n`[■□□□□□□□□□] 10%`",
            "⚡ *নিরাপদ কানেকশন তৈরি হচ্ছে...*\n`[█████□□□□□] 50%`",
            "✨ *প্রসেসিং সম্পন্ন!*\n`[██████████] 100%`"
        ]
        
        for frame in loading_frames:
            try:
                await query.edit_message_caption(caption=frame, parse_mode="Markdown")
                await asyncio.sleep(0.1)
            except Exception:
                pass
        
        pay_instruction = (
            f"💳 **পেমেন্ট নির্দেশিকা**\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🔹 **পেমেন্ট মেথড:** bKash / Nagad (Personal)\n"
            f"📱 **নম্বর:** `{PAYMENT_NUMBER}`\n"
            f"⚡ **টাইপ:** Send Money\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📝 **জমা দেওয়ার নিয়ম:**\n"
            f"উপরে দেওয়া নম্বরে টাকা পাঠিয়ে আপনার **মোবাইল নম্বর** এবং **TrxID** বা টাকার পরিমাণ এক মেসেজে লিখে রিপ্লাই দিন।\n\n"
            f"💡 **উদাহরণ:**\n`01711223344 TrxID: A1B2C3D4 Amount: 500`"
        )
        
        keyboard = [[InlineKeyboardButton("🔙 মূল মেনুতে ফিরুন", callback_data="back_home")]]
        await query.edit_message_caption(caption=pay_instruction, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif query.data == "back_home":
        user = query.from_user
        
        msg = (
            f"┌───────────────┐\n"
            f"  💎 **VIP AUTO PAYMENT PORTAL** 💎\n"
            f"└───────────────┘\n\n"
            f"👤 **গ্রাহকের তথ্য:**\n"
            f" ┣ 📛 **নাম:** `{user.full_name}`\n"
            f" ┣ 🆔 **আইডি:** `{user.id}`\n"
            f" ┗ ⚡ **সার্ভার স্ট্যাটাস:** 🟢 `২৪/৭ অনলাইন`\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📢 **বিজ্ঞপ্তি:** আপনার যেকোনো সার্ভিস রিনিউ বা সাবস্ক্রিপশনের জন্য নিচের বাটন থেকে লেনদেন সম্পন্ন করুন।\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━"
        )
        
        keyboard = [
            [InlineKeyboardButton("💳 পেমেন্ট করুন / TrxID জমা দিন", callback_data="req_pay")],
            [
                InlineKeyboardButton("👨‍💻 লাইভ সাপোর্ট", url=f"https://t.me/{SUPPORT_USERNAME}"),
                InlineKeyboardButton("🔄 পেজ রিফ্রেশ", callback_data="refresh")
            ]
        ]
        await query.edit_message_caption(caption=msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif query.data == "refresh":
        await query.answer("✨ সিস্টেম রিফ্রেশ সম্পন্ন হয়েছে!", show_alert=True)

    elif query.data == "admin_user_list":
        users = load_users()
        if not users:
            await query.answer("কোনো কাস্টমারের তথ্য নেই", show_alert=True)
            return

        user_list_text = f"👥 **কাস্টমার তালিকা ({len(users)} জন):**\n━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        count = 1
        for uid, udata in users.items():
            name = udata.get("name", "Unknown")
            uname = udata.get("username", "No Username")
            user_list_text += (
                f"`{count}.` 👤 **{name}** ({uname})\n"
                f"   ┗ 🆔 `{uid}` ➔ Send: `/send {uid} `\n\n"
            )
            count += 1
            
        await context.bot.send_message(chat_id=query.from_user.id, text=user_list_text, parse_mode="Markdown")

    elif query.data == "guide_broadcast":
        guide_text = (
            "📢 **ব্রডকাস্ট গাইড**\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            "সব ইউজারকে একসাথে মেসেজ পাঠাতে টাইপ করুন:\n\n"
            "`/broadcast আজ বিশেষ অফার চলছে!`"
        )
        await context.bot.send_message(chat_id=query.from_user.id, text=guide_text, parse_mode="Markdown")

    elif query.data == "guide_send":
        guide_text = (
            "✉️ **ডাইরেক্ট মেসেজ গাইড**\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            "একজনকে মেসেজ দিতে টাইপ করুন:\n\n"
            "`/send 7433409654 আপনার সার্ভিস একটিভ হয়েছে!`"
        )
        await context.bot.send_message(chat_id=query.from_user.id, text=guide_text, parse_mode="Markdown")

    elif query.data == "admin_stats":
        users = load_users()
        await query.answer(f"📈 মোট রেজিস্টার্ড কাস্টমার: {len(users)} জন", show_alert=True)

    elif query.data == "admin_refresh":
        await query.answer("ড্যাশবোর্ড রিফ্রেশ করা হয়েছে!", show_alert=True)

    elif query.data.startswith("approve_"):
        user_id = int(query.data.split("_")[1])
        await context.bot.send_message(
            chat_id=user_id, 
            text=(
                f"🎉 **পেমেন্ট অনুমোদিত হয়েছে!** 🟢\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"আপনার লেনদেন সফলভাবে ভেরিফাই করা হয়েছে। আপনার সার্ভিস সক্রিয় করা হলো।\n\n"
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
                f"❌ **পেমেন্ট বাতিল হয়েছে!** 🔴\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"আপনার প্রদত্ত TrxID বা তথ্যে ভুল পাওয়া গেছে।\n"
                f"অনুগ্রহ করে সঠিকভাবে পেমেন্ট করে আবার চেষ্টা করুন অথবা সাপোর্টে যোগাযোগ করুন।"
            ),
            parse_mode="Markdown"
        )
        await query.edit_message_text(f"❌ Payment Rejected for User ID: {user_id}")

# Handle Incoming Messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    text = update.message.text
    chat_id = update.effective_chat.id
    
    save_user(user)

    if context.user_data.get('waiting_for_trx'):
        context.user_data['waiting_for_trx'] = False
        
        await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
        status_msg = await update.message.reply_text("⏳ *আপনার পেমেন্ট তথ্য প্রসেসিং হচ্ছে...*", parse_mode="Markdown")
        await asyncio.sleep(0.8)
        
        admin_keyboard = [
            [
                InlineKeyboardButton("✅ অনুমোদন করুন", callback_data=f"approve_{user.id}"),
                InlineKeyboardButton("❌ বাতিল করুন", callback_data=f"reject_{user.id}")
            ]
        ]
        
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=(
                f"🚨 **নতুন পেমেন্ট রিকোয়েস্ট** 🚨\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"👤 **কাস্টমার:** {user.full_name} (@{user.username})\n"
                f"🆔 **আইডি:** `{user.id}`\n"
                f"📄 **পেমেন্ট তথ্য:** `{text}`\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━"
            ),
            reply_markup=InlineKeyboardMarkup(admin_keyboard),
            parse_mode="Markdown"
        )
        
        await status_msg.edit_text(
            "🚀 **আপনার তথ্য জমা নেওয়া হয়েছে!**\n\n"
            "⏳ *এডমিন প্যানেল থেকে ভেরিফাই করে দ্রুত কনফার্ম করা হবে।*",
            parse_mode="Markdown"
        )

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).post_init(post_init).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(CommandHandler("users", list_users_command))
    app.add_handler(CommandHandler("broadcast", broadcast_command))
    app.add_handler(CommandHandler("send", send_single_user))
    app.add_handler(CommandHandler("stats", stats_command))
    
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Professional UI Auto Payment Bot is running...")
    app.run_polling()
