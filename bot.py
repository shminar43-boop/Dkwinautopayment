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
        BotCommand("start", "Start payment bot & main menu"),
        BotCommand("admin", "Open Admin Control Panel"),
        BotCommand("users", "Show registered user list"),
        BotCommand("broadcast", "Send message to all users"),
        BotCommand("send", "Send message to single user"),
        BotCommand("stats", "Show user statistics")
    ])

# /start Command Handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    chat_id = update.effective_chat.id
    
    save_user(user)

    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    await asyncio.sleep(0.3)
    
    msg = (
        f"✨ **— OFFICIAL VIP PAYMENT PORTAL —** ✨\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 **Grahok:** {user.full_name}\n"
        f"🆔 **ID:** `{user.id}`\n"
        f"⚡ **Status:** 🟢 24/7 Active\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📲 *Payment korte ba TrxID pathate nicher botone chap din.* 👋"
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

# Admin Panel Command (/admin)
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("⛔ Ei command shudhu admin bebohar korte parben.")
        return

    users = load_users()
    msg = (
        f"👑 **— ADMIN CONTROL PANEL —**\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📊 **Total Registered Users:** `{len(users)}` jon\n"
        f"⚡ **Bot Status:** 🟢 Online & Running\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"⚡ **QUICK COMMANDS (Tap to use):**\n"
        f"• /users - Registered user list\n"
        f"• /stats - User count summary\n"
        f"• /broadcast - Send message to all users\n"
        f"• /send - Send message to a specific user\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💡 *Nicher buton gulo babohar kore dynamic action nin:* "
    )
    
    keyboard = [
        [InlineKeyboardButton("📋 Registered User List", callback_data="admin_user_list")],
        [
            InlineKeyboardButton("📢 Broadcast Guide", callback_data="guide_broadcast"),
            InlineKeyboardButton("👤 Single Send Guide", callback_data="guide_send")
        ],
        [
            InlineKeyboardButton("📊 Total Stats", callback_data="admin_stats"),
            InlineKeyboardButton("🔄 Refresh Panel", callback_data="admin_refresh")
        ]
    ]
    
    await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

# User List Show Command (/users)
async def list_users_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("⛔ Ei command shudhu admin bebohar korte parben.")
        return

    users = load_users()
    if not users:
        await update.message.reply_text("❌ Kono user record-e paowa jayni.")
        return

    user_list_text = f"📋 **— ALL REGISTERED USERS ({len(users)}) —**\n━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    count = 1
    for uid, udata in users.items():
        name = udata.get("name", "Unknown")
        uname = udata.get("username", "No Username")
        user_list_text += (
            f"{count}. 👤 **{name}** ({uname})\n"
            f"   🆔 ID: `{uid}`\n"
            f"   👉 Send Msg: `/send {uid} `\n\n"
        )
        count += 1

    user_list_text += "━━━━━━━━━━━━━━━━━━━━━━━\n💡 *Single user ke message dite click tap `/send <id> <msg>`*"

    if len(user_list_text) > 4000:
        for x in range(0, len(user_list_text), 4000):
            await update.message.reply_text(user_list_text[x:x+4000], parse_mode="Markdown")
    else:
        await update.message.reply_text(user_list_text, parse_mode="Markdown")

# Single User Message Command (/send <user_id> <message>)
async def send_single_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("⛔ Ei command shudhu admin bebohar korte parben.")
        return

    if len(context.args) < 2:
        await update.message.reply_text(
            "⚠️ **Beboharer Niyom:**\n\n"
            "`/send <user_id> <apnar_message>`\n\n"
            "💡 *Tap to copy example:*\n"
            "`/send 7433409654 Apnar payment verified!`",
            parse_mode="Markdown"
        )
        return

    target_user_id = context.args[0]
    message_text = " ".join(context.args[1:])

    try:
        await context.bot.send_message(
            chat_id=int(target_user_id),
            text=(
                f"📩 **— NOTICE FROM ADMIN —**\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"{message_text}\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"📞 Support: @{SUPPORT_USERNAME}"
            ),
            parse_mode="Markdown"
        )
        await update.message.reply_text(
            f"✅ **Message pathano hoyeche!**\n\n"
            f"👤 **User ID:** `{target_user_id}`\n"
            f"📄 **Message:** {message_text}",
            parse_mode="Markdown"
        )
    except Exception as e:
        await update.message.reply_text(
            f"❌ **Error:** Message pathano jayni. User bot block korethakte pare.\nDetails: `{e}`",
            parse_mode="Markdown"
        )

# Broadcast Command (/broadcast <message>)
async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("⛔ Ei command shudhu admin bebohar korte parben.")
        return

    if not context.args and not update.message.reply_to_message:
        await update.message.reply_text(
            "⚠️ **Beboharer Niyom:**\n\n"
            "`/broadcast Apnar notice`\n\n"
            "💡 *Tap to copy example:*\n"
            "`/broadcast Ajke sob transaction veti-krito hoyeche!`",
            parse_mode="Markdown"
        )
        return

    users = load_users()
    if not users:
        await update.message.reply_text("❌ Kono user paowa jayni.")
        return

    broadcast_text = " ".join(context.args) if context.args else None
    reply_to_msg = update.message.reply_to_message

    status_msg = await update.message.reply_text(f"⏳ **{len(users)} jon user er kache message pathano shuru hocche...**", parse_mode="Markdown")
    
    success_count = 0
    failed_count = 0

    for uid in users.keys():
        try:
            if reply_to_msg:
                await reply_to_msg.copy(chat_id=int(uid))
            else:
                await context.bot.send_message(
                    chat_id=int(uid),
                    text=f"📢 **— ANNOUNCEMENT —**\n━━━━━━━━━━━━━━━━━━━━━━━\n\n{broadcast_text}",
                    parse_mode="Markdown"
                )
            success_count += 1
            await asyncio.sleep(0.05)
        except Exception:
            failed_count += 1

    await status_msg.edit_text(
        f"✅ **BROADCAST COMPLETED!**\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🟢 **Sotikbhabe Giyeshe:** `{success_count}` jon\n"
        f"🔴 **Failed (Block):** `{failed_count}` jon\n"
        f"📊 **Total Users:** `{len(users)}` jon",
        parse_mode="Markdown"
    )

# User stats command (/stats)
async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    users = load_users()
    await update.message.reply_text(f"📊 **Total Registered Users:** `{len(users)}` jon", parse_mode="Markdown")

# Button Click Handler
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "req_pay":
        context.user_data['waiting_for_trx'] = True
        
        loading_frames = [
            "⏳ *Payment portal load hocche...*\n`[▒▒▒▒▒▒▒▒▒▒] 0%`",
            "⚡ *Payment nirdeshika toiri hocche...*\n`[█████▒▒▒▒▒] 50%`",
            "✨ *Portal Ready!*\n`[██████████] 100%`"
        ]
        
        for frame in loading_frames:
            try:
                await query.edit_message_caption(caption=frame, parse_mode="Markdown")
                await asyncio.sleep(0.12)
            except Exception:
                pass
        
        pay_instruction = (
            f"📥 **— INLINE PAYMENT INSTRUCTIONS —**\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💎 **Payment Method:** bKash / Nagad (Personal)\n"
            f"📱 **Agent / Personal Number:** `{PAYMENT_NUMBER}`\n"
            f"🚀 **Type:** Send Money\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📝 **Kivabe joma diben:**\n"
            f"Upore dewa number e payment shomponno kore apnar **mobile number** ebong **TrxID** ba takar poriman ek message e likhe pathan.\n\n"
            f"💡 *Udaharun:* `01711223344 TrxID: A1B2C3D4 Amount: 500`"
        )
        
        keyboard = [[InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_home")]]
        await query.edit_message_caption(caption=pay_instruction, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif query.data == "back_home":
        user = query.from_user
        
        msg = (
            f"✨ **— OFFICIAL VIP PAYMENT PORTAL —** ✨\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 **Grahok:** {user.full_name}\n"
            f"🆔 **ID:** `{user.id}`\n"
            f"⚡ **Status:** 🟢 24/7 Active\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📲 *Payment korte ba TrxID pathate nicher botone chap din.*"
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
        await query.answer("✨ Portal update kora hoyeche!", show_alert=True)

    elif query.data == "admin_user_list":
        users = load_users()
        if not users:
            await query.answer("Kono registered user nai", show_alert=True)
            return

        user_list_text = f"📋 **— ALL REGISTERED USERS ({len(users)}) —**\n━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        count = 1
        for uid, udata in users.items():
            name = udata.get("name", "Unknown")
            uname = udata.get("username", "No Username")
            user_list_text += (
                f"{count}. 👤 **{name}** ({uname})\n"
                f"   🆔 ID: `{uid}`\n"
                f"   👉 Quick Msg: `/send {uid} `\n\n"
            )
            count += 1
            
        await context.bot.send_message(chat_id=query.from_user.id, text=user_list_text, parse_mode="Markdown")

    elif query.data == "guide_broadcast":
        guide_text = (
            "📢 **— BROADCAST GUIDE —**\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            "Sob user ke ekshate message dite nicher format e likhun (tap to copy):\n\n"
            "`/broadcast Ajke amader bot upgrade kora hoyeche!`"
        )
        await context.bot.send_message(chat_id=query.from_user.id, text=guide_text, parse_mode="Markdown")

    elif query.data == "guide_send":
        guide_text = (
            "👤 **— SINGLE SEND GUIDE —**\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            "Kono nirdishto user ke message dite nicher format e likhun (tap to copy):\n\n"
            "`/send 7433409654 Apnar payment verification success!`"
        )
        await context.bot.send_message(chat_id=query.from_user.id, text=guide_text, parse_mode="Markdown")

    elif query.data == "admin_stats":
        users = load_users()
        await query.answer(f"📊 Total Users: {len(users)} jon", show_alert=True)

    elif query.data == "admin_refresh":
        await query.answer("Admin Dashboard refreshed!", show_alert=True)

    elif query.data.startswith("approve_"):
        user_id = int(query.data.split("_")[1])
        await context.bot.send_message(
            chat_id=user_id, 
            text=(
                f"🎉 **PAYMENT APPROVED & CONFIRMED!** 🟢\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"✨ Apnar payment sothikbhabe janchai kore verify kora hoyeche.\n\n"
                f"🤝 Amader sathe thakar jonno dhonnobad!"
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
                f"Apnar prodattokrito TrxID ba payment tathyo paowa jayni.\n"
                f"Onugroho kore sothik tathyo diye abar chesta karun ba support e barta din."
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
        status_msg = await update.message.reply_text("⏳ *Verification er jonno server e data process hocche...*", parse_mode="Markdown")
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
                f"👤 **Grahok:** {user.full_name} (@{user.username})\n"
                f"🆔 **ID:** `{user.id}`\n"
                f"📄 **Payment Data:** `{text}`\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━"
            ),
            reply_markup=InlineKeyboardMarkup(admin_keyboard),
            parse_mode="Markdown"
        )
        
        await status_msg.edit_text(
            "🚀 **Apnar payment tathyo joma neowa hoyeche!**\n\n"
            "⏳ *Agent team verify kore druto nishchit korbe.*",
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
    
    print("Bot with Auto Command Menu & Admin Panel is running...")
    app.run_polling()
