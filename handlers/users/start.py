from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from loader import dp, user_db, bot
import logging
from data.config import ADMINS


CHANNEL_USERNAME = "@kino_bot_rasmiy_kanal"
BOT_USERNAME = "@kinotatuztatbot"  # The bot username to check

async def check_subscription(user_id: int, username: str) -> bool:
    """Check if the user is subscribed to the channel or bot."""
    try:
        member = await bot.get_chat_member(username, user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        logging.error(f"Error checking subscription: {e}")
        return False


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    user_id = message.from_user.id
    is_channel_subscribed = await check_subscription(user_id, CHANNEL_USERNAME)
    is_bot_subscribed = await check_subscription(user_id, BOT_USERNAME)

    # Check if the user is subscribed to either the channel or the bot
    if is_channel_subscribed or is_bot_subscribed:
        telegram_id = message.from_user.id
        username = message.from_user.username
        first_name = message.from_user.first_name
        last_name = message.from_user.last_name if message.from_user.last_name else "No last name"

        # Add user to the database if not already added
        if not user_db.select_user(telegram_id=telegram_id):
            user_db.add_user(telegram_id=telegram_id, username=username)
            logging.info(f"New user added: telegram_id:{telegram_id}, username: {username}, full_name: {first_name} {last_name}")

            count = user_db.count_users()

            # Notify admins about the new user
            for admin in ADMINS:
                await dp.bot.send_message(
                    admin,
                    f"Telegram ID: {telegram_id}\n"
                    f"Username : {username}\n"
                    f"Toliq ismi :{message.from_user.full_name}\n"
                    f"Foydalanuvchi bazaga qo'shildi\n\n"
                    f"Bazada <b>{count}</b>  ta foydalanuvchi bor"
                )
            await message.answer(f"Salom, {first_name} {last_name}! Siz yangi foydalanuvchisiz!")
        else:
            await message.answer(f"Salom, {first_name} {last_name}! Siz allaqachon foydalanuvchisiz!")
    else:
        # If the user isn't subscribed to the required channels or bot
        keyboard = InlineKeyboardMarkup().add(
            InlineKeyboardButton("🔔 Kanalga obuna bo‘lish", url=f"https://t.me/{CHANNEL_USERNAME[1:]}"),
            InlineKeyboardButton("🔔 Botga obuna bo‘lish", url=f"https://t.me/{BOT_USERNAME[1:]}")
        )
        await message.answer("⚠️ Botdan foydalanish uchun avval kanalimizga va botimizga obuna bo‘lishingiz kerak!", reply_markup=keyboard)
