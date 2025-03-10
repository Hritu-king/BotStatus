# (c) @xditya
# This file is a part of https://github.com/xditya/BotStatus

import pytz
import logging
import asyncio
import contextlib
from time import sleep
from datetime import timezone, datetime as dt
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.errors.rpcerrorlist import (
    MessageNotModifiedError,
    FloodWaitError,
    AuthKeyDuplicatedError,
)
from decouple import config
from telethon.sessions import StringSession
from telethon import TelegramClient

logging.basicConfig(
    format="[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s", level=logging.INFO
)

try:
    appid = config("APP_ID" , 29616312)
    apihash = config("API_HASH" , "dd1a05ab4c47a5a037cc067cf4bded27")
    session = config("SESSION" , "1BVtsOMMBu0RMh0aCWzTa2JpntwHSjksPOC1O-g4W7UTN98t3Xz4ZlUa9wFVSvPrvQ_vf_pGrmhMMMzpIqz6vwWbkymUH54vFybqbmiElXn1dE6PpPI2Rq-5eoulNX4QFGD39bICusqcsiDHdtt0bcJ_ZL3KYg5bC7TXDxQb_ZaafFEeIFxSVG-WTLE_Xil4t46LTBbGlZZppVKKtF03nRIzYDjNpoxFtUm0cOEWOTd_N52S29orMLJY8n9UNPSBh9iT6B0LIhT-oGDG0o1QTi8QZaD0Ba3NJZCSBdjhaQjyfPMJqdcmm9Lv1HHCckj-Fs9FPVrOboFToyRSUWWF1m1_fRAcWMjU=")
    chnl_id = config("CHANNEL_ID" , -1001785446911 , cast=int)
    msg_id = config("MESSAGE_ID" , 10 , cast=int)
    botlist = config("BOTS" , "videoXcompressorBot adv_file_storeBot Mention_All_RoBot Stylish_text0Bot")
    bots = botlist.split()
    session_name = str(session)
    user_bot = TelegramClient(StringSession(session_name), appid, apihash)
    logging.info("\n\nStarted.\nVisit @private_bots!")
except Exception as e:
    logging.info(f"ERROR\n{e}")


async def BotzHub():
    async with user_bot:
        while True:
            logging.info("[INFO] starting to check uptime..")
            with contextlib.suppress(MessageNotModifiedError):
                await user_bot.edit_message(
                    int(chnl_id),
                    msg_id,
                    "**@private_bots Bots Stats.**\n\n`Performing a periodic check...`",
                )
            c = 0
            edit_text = "**@private_bots Bots Stats.**\n\n"
            for bot in bots:
                try:
                    logging.info(f"[INFO] checking @{bot}")
                    sent_time = dt.now(timezone.utc)
                    snt = await user_bot.send_message(bot, "/start")
                    await asyncio.sleep(10)

                    history = await user_bot(
                        GetHistoryRequest(
                            peer=bot,
                            offset_id=0,
                            offset_date=None,
                            add_offset=0,
                            limit=1,
                            max_id=0,
                            min_id=0,
                            hash=0,
                        )
                    )

                    msg = history.messages[0].id

                    if snt.id == msg:
                        logging.info("@%s is down.", bot)
                        edit_text += f"@{bot} - ❌ Died\n\n"
                    elif snt.id + 1 == msg:
                        resp_msg = await user_bot.get_messages(bot, ids=msg)
                        time_diff = (resp_msg.date - sent_time).total_seconds() * 100
                        edit_text += f"@{bot} - ✅ Alive [__{round(time_diff, 3)}ms__]\n\n"
                    await user_bot.send_read_acknowledge(bot)
                    c += 1
                except FloodWaitError as f:
                    logging.info("Floodwait!\n\nSleeping for %s...", f.seconds)
                    sleep(f.seconds + 10)
            await user_bot.edit_message(int(chnl_id), int(msg_id), edit_text)
            k = pytz.timezone("Asia/Kolkata")
            month = dt.now(k).strftime("%B")
            day = dt.now(k).strftime("%d")
            year = dt.now(k).strftime("%Y")
            t = dt.now(k).strftime("%H:%M:%S")
            edit_text += f"\n**Last Checked:** \n`{t} - {day} {month} {year} [IST]`\n\n__Bots status are auto-updated every 2 hours__"
            await user_bot.edit_message(int(chnl_id), int(msg_id), edit_text)
            logging.info("Checks since last restart - %s", c)
            logging.info("Sleeping for 2 hours.")  # we use workflows here.
            if c != 0:
                break


try:
    user_bot.loop.run_until_complete(BotzHub())
    user_bot.disconnect()  # try prevent AuthKeyDuplicatedError
except AuthKeyDuplicatedError:
    logging.warning("Session expired. Create a new one.")

logging.info("\nProcess Completed Successfully!")
