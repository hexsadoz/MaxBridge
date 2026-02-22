import asyncio, os, logging
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F 
from aiogram.types import Message
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from pymax import MaxClient, Message
from pymax.static.enum import MarkupType


logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
load_dotenv()

max_chat_id = os.getenv("max_chat_id")
tg_chat_id = os.getenv("tg_chat_id")
bot_token = os.getenv("bot_token")
phone = os.getenv("phone")

bot = Bot(token=bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML), proxy="https://t.me/proxy?server=83.166.254.26&port=443&secret=dd6b3fb02424dbac55fef2da67c8c949")
dp = Dispatcher()

client = MaxClient(
    phone=phone,
    work_dir="cache",
    reconnect=True,
)

@client.on_start
async def on_start() -> None:
    logging.info("MAX: Websocket connection started")

@client.on_message()
async def on_max_message(msg: Message):
    try:
        user = await client.get_user(msg.sender)
        name = user.names[0].first_name 
        if user.id == client.me.id or msg.chat_id != max_chat_id:
           return
        logging.info(f"MAX - {name}: {msg.text}")
        await bot.send_message(
            chat_id=int(tg_chat_id),
            text=f"<b>{name}:</b> {msg.text}",
        )
    except Exception as e:
        logging.error(f"MAX: Error {e}")

@dp.message(F.chat.id == int(tg_chat_id))
async def on_tg_message(msg: Message):
    try:
        if msg.from_user.is_bot:
            return
        logging.info(f"TG - {msg.from_user.first_name}: {msg.text}")
        await client.send_message(
            chat_id=max_chat_id,
            text=f"{msg.from_user.first_name}: {msg.text}",
        )
    except Exception as e:
        logging.error(f"TG: Error {e}")

async def main():
    await asyncio.gather(
        client.start(),
        dp.start_polling(bot)
    )

if __name__ == "__main__":
    asyncio.run(main())