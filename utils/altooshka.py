import random
from utils.core import logger
from pyrogram import Client, raw 
from pyrogram.raw.functions.messages import RequestWebView
from urllib.parse import unquote, quote
import asyncio
import aiohttp
from fake_useragent import UserAgent
from random import uniform
from data import config
import json
import os
import time
from aiohttp_socks import ProxyConnector
from pyrogram.errors import PeerIdInvalid


class AltooshkaBot:
    def __init__(self, thread: int, session_name: str, phone_number: str, proxy: [str, None]):
        self.account = session_name + '.session'
        self.thread = thread
        self.proxy = f"{config.PROXY_TYPES['REQUESTS']}://{proxy}" if proxy is not None else None
        self.user_agent_file = "./sessions/user_agents.json"
        self.statistics_file = "./statistics/stats.json"
        self.ref_link_file = "./sessions/ref_links.json"
        

        if proxy:
            proxy = {
                "scheme": config.PROXY_TYPES['TG'],
                "hostname": proxy.split(":")[1].split("@")[1],
                "port": int(proxy.split(":")[2]),
                "username": proxy.split(":")[0],
                "password": proxy.split(":")[1].split("@")[0]
            }

        with open("./data/api_config.json", "r") as f:
            apis = json.load(f)
            phone_number = apis[phone_number]
            api_id = phone_number[0]
            api_hash = phone_number[1]


        self.client = Client(
            name=session_name,
            api_id=api_id,
            api_hash=api_hash,
            workdir=config.WORKDIR,
            proxy=proxy,
            lang_code="ru"
        )


    async def init_async(self, proxy):
        self.refferal_link = await self.get_ref_link()
        user_agent = await self.get_user_agent()
        headers = {'User-Agent': user_agent}
        connector = ProxyConnector.from_url(self.proxy) if proxy else aiohttp.TCPConnector(verify_ssl=False)
        self.session = aiohttp.ClientSession(headers=headers, trust_env=True, connector=connector, timeout=aiohttp.ClientTimeout(120))
        self.initialized = True


    @classmethod
    async def create(cls, thread: int, session_name: str, phone_number: str, proxy: [str, None]):
        instance = cls(session_name=session_name, phone_number=phone_number, thread=thread, proxy=proxy)
        await instance.init_async(proxy)
        return instance


    async def get_ref_link(self):
        ref_links = await self.load_ref_links()
        if self.account in ref_links:
            if "Altooshka" in ref_links[self.account]:
                return ref_links[self.account]["Altooshka"]
        else:
            return None


    async def load_ref_links(self):
        if os.path.exists(self.ref_link_file):
            with open(self.ref_link_file, "r") as f:
                return json.load(f)
        else:
            return {}
        
    
    async def save_ref_links(self, ref_links):
        os.makedirs(os.path.dirname(self.ref_link_file), exist_ok=True)
        with open(self.ref_link_file, "w") as f:
            json.dump(ref_links, f, indent=4)


    async def referrals_check(self, resp_json):
            if self.refferal_link is None:
                ref_links = await self.load_ref_links()
                if self.account not in ref_links:
                    ref_links[self.account] = {"Altooshka": resp_json["data"]["user"]["referralCode"]}
                else:
                    Altooshka_ref = ref_links[self.account] 
                    Altooshka_ref["Altooshka"] = resp_json["data"]["user"]["referralCode"]
                await self.save_ref_links(ref_links)


    async def get_user_agent(self):
        user_agents = await self.load_user_agents()
        if self.account in user_agents:
            return user_agents[self.account]
        else:
            new_user_agent = UserAgent(os='android').random
            user_agents[self.account] = new_user_agent
            await self.save_user_agents(user_agents)
            return new_user_agent
        

    async def load_user_agents(self):
        if os.path.exists(self.user_agent_file):
            with open(self.user_agent_file, "r") as f:
                return json.load(f)
        else:
            return {}
        

    async def save_user_agents(self, user_agents):
        os.makedirs(os.path.dirname(self.user_agent_file), exist_ok=True)
        with open(self.user_agent_file, "w") as f:
            json.dump(user_agents, f, indent=4)


    async def get_stats(self, query):
        resp = await self.session.get("https://api.altooshka.io/user/", params=query)
        resp_json = await resp.json()
        logger.info(f"Altooshka | Thread {self.thread} | {self.account} | Balance: {resp_json["data"]["user"]["gems"]}")
        stats = await self.load_stats()
        
        balance = resp_json["data"]["user"]["gems"]
        if self.account not in stats:
            stats[self.account] = {"Altooshka":balance}
        elif "Altooshka" not in stats[self.account]:
            stats[self.account]["Altooshka"] = balance
        else:
            stats[self.account]["Altooshka"] = balance
        await self.save_stats(stats)
        

    async def load_stats(self):
        if os.path.exists(self.statistics_file):
            with open(self.statistics_file, "r") as f:
                return json.load(f)
        else:
            return {}


    async def save_stats(self, stats):
        os.makedirs(os.path.dirname(self.statistics_file), exist_ok=True)
        with open(self.statistics_file, "w") as f:
            json.dump(stats, f, indent=4)


    async def make_tasks(self, ws, resp_json):
        completed_tasks = resp_json["arguments"][0]["o"]["completed"]
        for mission in resp_json["arguments"][0]["o"]["missions"]:
            if mission["id"] not in completed_tasks:
                print("mission id", mission["id"])
                if mission["id"] in [21, 22, 184, 187]:
                    await self.client.connect()
                    try:
                        await self.client.join_chat("HoldBull")
                        await asyncio.sleep(uniform(3,5))
                        await ws.send_str(json.dumps({"type": 6}) + '\x1e')
                        await self.client.join_chat("HoldBull_ru")
                        await asyncio.sleep(uniform(3,5))
                        await ws.send_str(json.dumps({"type": 6}) + '\x1e')
                        await asyncio.sleep(uniform(3,5))
                        
                    except Exception as e:
                        print("e = ", e)

                    await self.client.disconnect()

                mission_claim_message = {
                    "arguments":[self.my_id, mission["id"]],
                    "invocationId":"0",
                    "target":"Mission",
                    "type": 1
                }
                await ws.send_str(json.dumps(mission_claim_message) + '\x1e')
                await asyncio.sleep(uniform(5, 8))
    

    async def make_action1(self, query, sleep_time):
        while True:
            query = await self.check_relogin(query)
            if sleep_time < time.time():
                json_data = {"girl_id":1,"action_id":1}
                resp = await self.session.post("https://api.altooshka.io/girls/action", params=query, json=json_data)
                resp_json = await resp.json()
                logger.success(f"Altooshka | Thread {self.thread} | {self.account} | Action 1 performed")
                try:
                    sleep_time = resp_json["data"]["availableAt"] - time.time()
                except:
                    sleep_time = 60*60*3
                await self.get_stats(query)
            else:
                sleep_time = sleep_time - time.time()
            logger.info(f"Altooshka Thread {self.thread} | {self.account} | Action 1, Sleep {sleep_time}")
            await asyncio.sleep(sleep_time)

    async def make_action2(self, query, sleep_time):
        while True:
            query = await self.check_relogin(query)
            if sleep_time < time.time():
                await asyncio.sleep(5)
                json_data = {"girl_id":1,"action_id":2}
                resp = await self.session.post("https://api.altooshka.io/girls/action", params=query, json=json_data)
                resp_json = await resp.json()
                logger.success(f"Altooshka | Thread {self.thread} | {self.account} | Action 2 performed")
                try:
                    sleep_time = resp_json["data"]["availableAt"] - time.time()
                except:
                    sleep_time = 60*60*3
                await self.get_stats(query)
            else:
                sleep_time = sleep_time - time.time()
            logger.info(f"Altooshka Thread {self.thread} | {self.account} | Action 2, Sleep {sleep_time}")
            await asyncio.sleep(sleep_time)

    async def make_action3(self, query, sleep_time):
        while True:
            query = await self.check_relogin(query)
            if sleep_time < time.time():
                await asyncio.sleep(10)
                json_data = {"girl_id":1,"action_id":3}
                resp = await self.session.post("https://api.altooshka.io/girls/action", params=query, json=json_data)
                resp_json = await resp.json()
                logger.success(f"Altooshka | Thread {self.thread} | {self.account} | Action 3 performed")
                try:
                    sleep_time = resp_json["data"]["availableAt"] - time.time()
                except:
                    sleep_time = 60*60*3
                await self.get_stats(query)
            else:
                sleep_time = sleep_time - time.time()
            logger.info(f"Altooshka Thread {self.thread} | {self.account} | Action 3, Sleep {sleep_time}")
            await asyncio.sleep(sleep_time)

    async def make_action4(self, query, sleep_time):
        while True:
            query = await self.check_relogin(query)
            if sleep_time < time.time():
                json_data = {"girl_id":2,"action_id":8}
                resp = await self.session.post("https://api.altooshka.io/girls/action", params=query, json=json_data)
                resp_json = await resp.json()
                logger.success(f"Altooshka | Thread {self.thread} | {self.account} | Action 4 performed")
                try:
                    sleep_time = resp_json["data"]["availableAt"] - time.time()
                except:
                    sleep_time = 60*60*3
                await self.get_stats(query)
            else:
                sleep_time = sleep_time - time.time()
            logger.info(f"Altooshka Thread {self.thread} | {self.account} | Action 4, Sleep {sleep_time}")
            await asyncio.sleep(sleep_time)

    async def make_action5(self, query, sleep_time):
        while True:
            query = await self.check_relogin(query)
            if sleep_time < time.time():
                await asyncio.sleep(15)
                json_data = {"girl_id":2,"action_id":9}
                resp = await self.session.post("https://api.altooshka.io/girls/action", params=query, json=json_data)
                resp_json = await resp.json()
                logger.success(f"Altooshka | Thread {self.thread} | {self.account} | Action 5 performed")
                try:
                    sleep_time = resp_json["data"]["availableAt"] - time.time()
                except:
                    sleep_time = 60*60*3
                await self.get_stats(query)
            else:
                sleep_time = sleep_time - time.time()
            logger.info(f"Altooshka Thread {self.thread} | {self.account} | Action 5, Sleep {sleep_time}")
            await asyncio.sleep(sleep_time)

    async def make_action6(self, query, sleep_time):
        while True:
            query = await self.check_relogin(query)
            if sleep_time < time.time():
                await asyncio.sleep(20)
                json_data = {"girl_id":2,"action_id":10}
                resp = await self.session.post("https://api.altooshka.io/girls/action", params=query, json=json_data)
                resp_json = await resp.json()
                logger.success(f"Altooshka | Thread {self.thread} | {self.account} | Action 6 performed")
                try:
                    sleep_time = resp_json["data"]["availableAt"] - time.time()
                except:
                    sleep_time = 60*60*3
                await self.get_stats(query)
            else:
                sleep_time = sleep_time - time.time()
            logger.info(f"Altooshka Thread {self.thread} | {self.account} | Action 6, Sleep {sleep_time}")
            await asyncio.sleep(sleep_time)

    async def daily_reward(self, query):
        while True:
            await asyncio.sleep(15)
            query = await self.check_relogin(query)
            await self.session.post("https://api.altooshka.io/action/daily", params=query)
            # await self.get_stats()
            logger.info(f"Altooshka | Thread {self.thread} | {self.account} | Daily reward gathered, Sleep {6 * 60 * 60}")
            await self.get_stats(query)
            await asyncio.sleep(6 * 60 * 60)
        

    async def check_relogin(self, query):
        resp = await self.session.get("https://api.altooshka.io/user/", params=query)
        if resp.status != 201:
            return await self.get_tg_web_data()
        else:
            return query


    async def make_actions(self, query, sleep_time1, sleep_time2, sleep_time3, sleep_time4, sleep_time5, sleep_time6):
        tasks = [
            self.daily_reward(query),
            self.make_action1(query, sleep_time1),
            self.make_action2(query, sleep_time2),
            self.make_action3(query, sleep_time3),
            self.make_action4(query, sleep_time4),
            self.make_action5(query, sleep_time5),
            self.make_action6(query, sleep_time6)
        ]
        await asyncio.gather(*tasks)


    async def subs_to_init(self, query):
        await self.client.connect()
        try:
            await self.client.join_chat("altooshka_ton")
            logger.info(f"Altooshka | Thread {self.thread} | {self.account} | Join chat altooshka_ton")
            await asyncio.sleep(uniform(3,5))
            await self.client.join_chat("AltOOshka_EN")
            logger.info(f"Altooshka | Thread {self.thread} | {self.account} | AltOOshka_EN")
            await asyncio.sleep(uniform(3,5))

            # query = await self.get_tg_web_data()
            # print("query =", query)
            resp = await self.session.get("https://api.altooshka.io/user/follow/", params=query)
            await asyncio.sleep(uniform(3,5))
            # print("resp =", resp)
            resp = await self.session.post("https://api.altooshka.io/user/", params=query)
            print("resp =", resp.status)
            await asyncio.sleep(uniform(3, 5))
            
        except Exception as e:
            print("e = ", e)

        await self.client.disconnect()
        

    async def login(self):
        query = await self.get_tg_web_data()
        # print("query = ",query)
        if self.refferal_link is None:
            await self.subs_to_init(query)

        resp = await self.session.get("https://api.altooshka.io/user/", params=query)
        
        resp_json = await resp.json()
        # print(resp_json)
        await asyncio.sleep(15)
        await self.get_stats(query)

        await self.referrals_check(resp_json)
        print("resp_json =", resp_json)

        if resp_json["data"]["user"]["girls"]["1"]["actions"]:
            if "1" in resp_json["data"]["user"]["girls"]["1"]["actions"]:
                sleep_time1 = resp_json["data"]["user"]["girls"]["1"]["actions"]["1"]
            else:
                sleep_time1 = 0
            if "2" in resp_json["data"]["user"]["girls"]["1"]["actions"]:
                sleep_time2 = resp_json["data"]["user"]["girls"]["1"]["actions"]["2"]
            else:
                sleep_time2 = 0
            if "3" in resp_json["data"]["user"]["girls"]["1"]["actions"]:
                sleep_time3 = resp_json["data"]["user"]["girls"]["1"]["actions"]["3"]
            else:
                sleep_time3 = 0
            
        if resp_json["data"]["user"]["girls"]["2"]["actions"]:
            if "1" in resp_json["data"]["user"]["girls"]["2"]["actions"]:
                sleep_time4 = resp_json["data"]["user"]["girls"]["2"]["actions"]["1"]
            else:
                sleep_time4 = 0
            if "2" in resp_json["data"]["user"]["girls"]["2"]["actions"]:
                sleep_time5 = resp_json["data"]["user"]["girls"]["2"]["actions"]["2"]
            else:
                sleep_time5 = 0
            if "3" in resp_json["data"]["user"]["girls"]["2"]["actions"]:
                sleep_time6 = resp_json["data"]["user"]["girls"]["2"]["actions"]["3"]
            else:
                sleep_time6 = 0

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            print("loop already exist")
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        loop.create_task(self.make_actions(query, sleep_time1, sleep_time2, sleep_time3, sleep_time4, sleep_time5, sleep_time6))

        try:
            if not loop.is_running():
                loop.run_forever()

        except Exception as e:
            print("e =",e)
        
        await asyncio.sleep(999999999)

    async def get_tg_web_data(self):
        try:
            await self.client.connect()

            web_view = await self.client.invoke(RequestWebView(
                peer=await self.client.resolve_peer('altooshka_bot'),
                bot=await self.client.resolve_peer('altooshka_bot'),
                platform='android',
                from_bot_menu=False,
                url='https://api.altooshka.io/'
            ))

            auth_url = web_view.url
            await self.client.disconnect()
        except:
            return None
        return unquote(string=unquote(string=auth_url.split('tgWebAppData=')[1].split('&tgWebAppVersion')[0]))
    
    async def check_bot_chat(self):
        clicked = False
        try:
            await self.client.connect()
            bot_username = "altooshka_bot"
            bot = await self.client.get_users(bot_username)
            # Пробуем получить чат по username бота
            try:
                messages = self.client.get_chat_history(bot.id, limit=1)
                async for message in messages:
                    logger.info(f"Altooshka | Thread {self.thread} | {self.account} | Button found")
                    await self.client.disconnect()
                    clicked = True
                    return clicked
                else:
                    logger.info(f"Altooshka | Thread {self.thread} | {self.account} | Button not found, start with refferal link")
                    with open(self.ref_link_file, 'r') as file:
                                ref_links = json.load(file)
                                if ref_links != {}:
                                    session_name = random.choice(list(ref_links.keys()))
                                    atemp = 0
                                    while "Altooshka" not in ref_links[session_name] and atemp < 5:
                                        session_name = random.choice(list(ref_links.keys()))
                                        atemp += 1
                                    if atemp == 5:
                                        referral_link = ""
                                    else:
                                        referral_link = ref_links[session_name]["Altooshka"]
                                        logger.info(f"Altooshka | Thread {self.thread} | {self.account} | Selected session: {session_name}, Referral link: {referral_link}")
                                else:
                                    referral_link = ""
                                bot_username = "altooshka_bot"
                                start_param = referral_link
                                result = await self.client.invoke(
                                    raw.functions.messages.StartBot(
                                        bot=await self.client.resolve_peer(bot_username),
                                        peer=await self.client.resolve_peer(bot_username),
                                        random_id=random.randint(0, 2**32 - 1),
                                        start_param=start_param
                                    )
                                )
                                logger.info(f"Altooshka | Thread {self.thread} | {self.account} | Bot started")
                                clicked = False
            except Exception as e:
                clicked = False
                print("Error:", e)

            await self.client.disconnect()

        except:
            return clicked
        
        

    # async def click_start_button(self):
    #     clicked = False
    #     try:
    #         await self.client.connect()
    #         me = await self.client.get_me()
    #         self.my_id = me.id
    #         bot_username = "BullApp_bot"
    #         bot = await self.client.get_users(bot_username)

    #         try:
    #             messages = self.client.get_chat_history(bot.id, limit=1)
    #             async for message in messages:
    #                 if message.reply_markup and message.reply_markup.inline_keyboard:
    #                     # Проверяем, есть ли у нас хотя бы три ряда кнопок
    #                     if len(message.reply_markup.inline_keyboard) >= 3:
    #                         third_row_buttons = message.reply_markup.inline_keyboard[2]
    #                         # Проверяем, есть ли кнопка в третьем ряду
    #                         if third_row_buttons:
    #                             button = third_row_buttons[0]  # Берем первую кнопку третьего ряда
    #                             if button.url:  # Убедимся, что у кнопки есть url
    #                                 response = await self.session.get(button.url)
    #                                 logger.info(f"Bull | Thread {self.thread} | {self.account} | Button pressed, status: {response.status}")
    #                                 clicked = True
    #                                 await self.client.disconnect()
    #                                 return clicked
    #             else:
    #                 # Если кнопка не найдена, то берем рефаральную ссылку и по ней запускаем бота, потом нажимаем на кнопку
    #                 print("Button not found")
    #                 logger.info(f"Bull | Thread {self.thread} | {self.account} | Button not found, start with refferal link")
    #                 with open(self.ref_link_file, 'r') as file:
    #                     ref_links = json.load(file)
    #                     session_name, referral_link = random.choice(list(ref_links.items()))
    #                     logger.info(f"Bull | Thread {self.thread} | {self.account} | Selected session: {session_name}, Referral link: {referral_link}")
    #                     bot_username = referral_link.split("?start=")[0].split("/")[-1]
    #                     start_param = referral_link.split("?start=")[-1]
                        
    #                     result = await self.client.invoke(
    #                         raw.functions.messages.StartBot(
    #                             bot=await self.client.resolve_peer(bot_username),
    #                             peer=await self.client.resolve_peer(bot_username),
    #                             random_id=int(time.time() * 1000),
    #                             start_param=start_param
    #                         )
    #                     )
    #                     logger.info(f"Bull | Thread {self.thread} | {self.account} | Bot started: {result}")
    #                     clicked = False
    #         except Exception as e:
    #             clicked = False
    #             print("Error:", e)

    #         await self.client.disconnect()

    #     except:
    #         return clicked