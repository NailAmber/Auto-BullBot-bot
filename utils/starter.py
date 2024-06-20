from utils.bull import BullBot
from utils.altooshka import AltooshkaBot
from asyncio import sleep
from random import uniform
from data import config
from utils.core import logger
import asyncio
from aiohttp.client_exceptions import ContentTypeError


async def start(thread: int, session_name: str, phone_number: str, proxy: [str, None]):
    bull = await BullBot.create(session_name=session_name, phone_number=phone_number, thread=thread, proxy=proxy)
    account = session_name + '.session'

    await sleep(uniform(*config.DELAYS['ACCOUNT']))

    while True:
        try:
            while not await bull.click_start_button():
                await sleep(uniform(5, 8))
                
            await bull.login()

            await sleep(30)

        except ContentTypeError as e:
            logger.error(f"Bull | Thread {thread} | {account} | Error: {e}")
            await asyncio.sleep(120)

        except Exception as e:
            logger.error(f"Bull | Thread {thread} | {account} | Error: {e}")

async def altooshkaStart(thread: int, session_name: str, phone_number: str, proxy: [str, None]):
    altooshka = await AltooshkaBot.create(session_name=session_name, phone_number=phone_number, thread=thread, proxy=proxy)
    account = session_name + '.session'

    await sleep(uniform(*config.DELAYS['ACCOUNT']))

    while True:
        try:
            await altooshka.check_bot_chat()
            await sleep(5)
            
            await altooshka.login()

            await sleep(30)

        except ContentTypeError as e:
            logger.error(f"Altooshka | Thread {thread} | {account} | Error: {e}")
            await asyncio.sleep(120)

        except Exception as e:
            logger.error(f"Altooshka | Thread {thread} | {account} | Error: {e}")