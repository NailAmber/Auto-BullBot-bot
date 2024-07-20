import random
from utils.core import logger
from pyrogram import Client, raw 
from urllib.parse import unquote, quote
import asyncio
from fake_useragent import UserAgent
from random import uniform
from data import config
from pyrogram.raw.functions.messages import RequestAppWebView
from pyrogram.raw.types import InputBotAppShortName
import json
import os
import httpx
import time
from pyrogram.raw.functions.messages import RequestWebView

class WormfareBot:
    def __init__(self, thread: int, session_name: str, phone_number: str, proxy: [str, None]):
        self.account = session_name + '.session'
        self.thread = thread
        self.proxy = f"{config.PROXY_TYPES['REQUESTS']}://{proxy}" if proxy is not None else None
        self.user_agent_file = "./sessions/user_agents.json"
        self.statistics_file = "./statistics/stats.json"
        self.ref_link_file = "./sessions/ref_links.json"
        self.major_refs = './sessions/major_refs.json'
        

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
        # self.refferal_link = await self.get_ref_link()
        user_agent = await self.get_user_agent()
        headers = {'User-Agent': user_agent}
        self.session = httpx.AsyncClient(headers=headers)
        self.initialized = True


    @classmethod
    async def create(cls, thread: int, session_name: str, phone_number: str, proxy: [str, None]):
        instance = cls(session_name=session_name, phone_number=phone_number, thread=thread, proxy=proxy)
        await instance.init_async(proxy)
        return instance


    async def referrals_check(self, ref_number):
            if self.refferal_link is None:
                ref_links = await self.load_ref_links()
                if self.account not in ref_links:
                    ref_links[self.account] = {"Major": ref_number}
                else:
                    Major_ref = ref_links[self.account] 
                    Major_ref["Major"] = ref_number
                await self.save_ref_links(ref_links)


    async def get_user_agent(self):
        user_agents = await self.load_user_agents()
        if self.account in user_agents:
            return user_agents[self.account]
        else:
            new_user_agent = UserAgent(os='ios').random
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

    async def load_major_refs(self):
        if os.path.exists(self.major_refs):
            with open(self.major_refs, 'r') as f:
                return json.load(f)
        else:
            return {}
        
    async def save_major_refs(self, major_refs):
        os.makedirs(os.path.dirname(self.major_refs), exist_ok=True)
        with open(self.major_refs, 'w') as f:
            json.dump(major_refs, f, indent=4)

    async def get_stats(self, query):
        resp = await self.session.get("https://api.altooshka.io/user/", params=query)
        resp_json = await resp.json()
        logger.info(f"Wormfare | Thread {self.thread} | {self.account} | Balance: {resp_json["data"]["user"]["gems"]}")
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


    async def tg_join_task(self, mini_task):
        if 'https://t.me/' in mini_task['url'] and not 'boost' in mini_task['url']:

                if 'startapp' in mini_task['url']:
                    bot_username = mini_task['url'].split('/')[3]
                    start_param = mini_task['url'].split('/')[4].split('=')[1]

                    await self.client.connect()
                    try:
                        result = await self.client.invoke(
                            raw.functions.messages.StartBot(
                                bot=await self.client.resolve_peer(bot_username),
                                peer=await self.client.resolve_peer(bot_username),
                                random_id=int(time.time() * 1000),
                                start_param=start_param
                            )
                        )
                    except Exception as e:
                        print("e = ", e)   
                    await self.client.disconnect() 

                    if 'cityholder' in mini_task['url']:
                        await self.make_cd_holder_task()
                else:
                    await self.client.connect()
                    try:
                        if '+' in mini_task['url']:
                            await self.client.join_chat(mini_task['url'])
                        else:
                            await self.client.join_chat(mini_task['url'].split('/')[3])
                    except Exception as e:
                        print("e = ", e)
                    await self.client.disconnect()
                    
                await asyncio.sleep(1)


    async def make_task(self, resp_json):
        try:
            for task in resp_json:
                if 'isCompleted' in task and task['isCompleted'] == True:
                    continue
                if task['isSimpleCheck'] == True:
                    json_data = {
                        'questId':task['id']
                    }
                    resp = await self.session.post('https://api.clicker.wormfare.com/quest/check-completion', json=json_data)
                    resp = await self.session.post('https://api.clicker.wormfare.com/quest/claim-reward', json=json_data)
                    complete = resp.json()
                    if complete['success'] == True:
                        logger.success(f"Wormfare | Thread {self.thread} | {self.account} | Quest complete {task['id']}")
                    await asyncio.sleep(2)
                else:
                    if 'maxCompleteTimes' in task and 'completeTimes' in task and task['maxCompleteTimes'] <= task['completeTimes']:
                        continue
                    if task['type'] == 'complex':
                        for mini_task in task['tasks']:
                            try:
                                await self.tg_join_task(mini_task)
                                json_data = {
                                    'questId':task['id'],
                                    'taskId':mini_task['id']
                                }
                                resp = await self.session.post('https://api.clicker.wormfare.com/quest/check-completion', json=json_data)
                                mini_task_json = resp.json()
                                if mini_task_json['success'] == True:
                                    logger.success(f"Wormfare | Thread {self.thread} | {self.account} | Task {mini_task['id']} in Quest {task['id']} complete")
                                    await asyncio.sleep(3)
                            except Exception as e:
                                logger.error(f"Wormfare | Thread {self.thread} | {self.account} | error: {e}")
                    json_data = {
                        'questId':task['id']
                    }
                    resp = await self.session.post('https://api.clicker.wormfare.com/quest/check-completion', json=json_data)
                    resp = await self.session.post('https://api.clicker.wormfare.com/quest/claim-reward', json=json_data)
                    complete = resp.json()
                    if complete['success'] == True:
                        logger.success(f"Wormfare | Thread {self.thread} | {self.account} | Quest complete {task['id']}")
                        await asyncio.sleep(2)
        except Exception as e:
            logger.error(f"Wormfare | Thread {self.thread} | {self.account} | error: {e}")

    async def login(self):
        query = await self.get_tg_web_data()

        json_data = {
            'initData':query
        }
        
        resp = await self.session.post('https://api.clicker.wormfare.com/auth/login', json=json_data)
        resp_json = resp.json()
        self.session.headers.pop('Authorization', None)
        self.session.headers['Authorization'] = "Bearer " + resp_json.get("accessToken")
        resp = await self.session.get('https://api.clicker.wormfare.com/user/profile')
        resp_json = resp.json()

        await asyncio.sleep(2)

        quests = await self.session.get('https://api.clicker.wormfare.com/quest')
        quests_json = quests.json()
        await self.make_task(quests_json)
        await asyncio.sleep(5)
        await self.make_task(quests_json)
        json_data ={
            'type':'accountAge'
        }
        resp = await self.session.post('https://api.clicker.wormfare.com/claim', json=json_data)
        
        json_data ={
            'type':'Quests'
        }
        resp = await self.session.post('https://api.clicker.wormfare.com/claim', json=json_data)
        await asyncio.sleep(2)
        resp = await self.session.get('https://api.clicker.wormfare.com/user/profile')
        resp_json = resp.json()
        logger.info(f"Wormfare | Thread {self.thread} | {self.account} | jams {resp_json['jam']} ,score {resp_json['totalEarnedScore']}, rank {resp_json['rank']}")
        sleep_time = 60 * 60 * 12 + uniform(config.DELAYS['MAJOR_SLEEP'][0], config.DELAYS['MAJOR_SLEEP'][1])
        logger.info(f"Wormfare | Thread {self.thread} | {self.account} | Sleep {sleep_time}")
        for _ in range(int(sleep_time / 60)):
            await asyncio.sleep(60)


    async def get_tg_web_data(self):
        try:
            await self.client.connect()
            bot_username = "wormfare_slap_bot"
            bot = await self.client.get_users(bot_username)
            not_found = True
            # Пробуем получить чат по username бота
            try:
                messages = self.client.get_chat_history(bot.id, limit=1)
                async for message in messages:
                    logger.info(f"Wormfare | Thread {self.thread} | {self.account} | Button found")
                else:
                    not_found = False
            except Exception as e:
                clicked = False
                print("Error:", e)        
            major_refs = await self.load_major_refs()
            if major_refs == {}:
                for refka in config.MAJOR_REFS:
                    major_refs[refka] = {'current': 0, 'max': int(uniform(config.MAJOR_REFS_NUMBER[0], config.MAJOR_REFS_NUMBER[1]))}
            # print('refki =',major_refs)
            max_ref_session = -1
            good_ref_link = ''
            for ref in major_refs:
                if max_ref_session < major_refs[ref]['current'] and major_refs[ref]['current'] < major_refs[ref]['max']:
                    max_ref_session = major_refs[ref]['current']
                    good_ref_link = ref
            if good_ref_link == '':
                good_ref_link = '374069367'
            else:
                if not_found:
                    major_refs[good_ref_link]['current'] += 1
            
            await self.save_major_refs(major_refs)
            # logger.info(f"Wormfare | Thread {self.thread} | {self.account} | Loging under ref: {good_ref_link}")

            web_view = await self.client.invoke(RequestAppWebView(
                peer=await self.client.resolve_peer('wormfare_slap_bot'),
                app=InputBotAppShortName(bot_id=await self.client.resolve_peer('wormfare_slap_bot'), short_name="start"),
                platform='ios',
                write_allowed=True,
                start_param=good_ref_link
            ))
            await self.client.disconnect()

            auth_url = web_view.url
            query = unquote(string=auth_url.split('tgWebAppData=')[1].split('&tgWebAppVersion')[0])
            return query
        except:
            return None