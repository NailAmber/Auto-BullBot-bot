from utils.core import create_sessions
from utils.telegram import Accounts
from utils.starter import start, altooshkaStart, vertusStart, vertusStats, majorStart
import asyncio
import os
import json
from utils.proceed_raw_api import proceed_data

async def main():
    action = int(input("Select action:\n1. Start soft\n2. Print stats\n3. Create sessions\n4. Proceed raw data api configs\n\n> "))

    if not os.path.exists('sessions'): os.mkdir('sessions')
    if not os.path.exists('statistics'): os.mkdir('statistics')
    if not os.path.exists('sessions/accounts.json'):
        with open("sessions/accounts.json", 'w') as f:
            f.write("[]")

    if action == 4:
        await proceed_data()

    if action == 3:
        await create_sessions()

    if action == 2:
        choose_bot = int(input("Select bot:\n1. Bull\n2. Altooshka\n3. Vertus\n\n> "))
        
        if os.path.exists("./statistics/stats.json"):
            stats = {}
            with open("./statistics/stats.json", "r") as f:
                stats = json.load(f)
            
            for session in stats:
                if choose_bot == 1:
                    logins = [item["login"] for item in stats[session]["Bull"]["friends"]]
                    print(f"{session}: balance = {stats[session]["Bull"]["balance"]}, boost1 lvl = {stats[session]["Bull"]["boost1"]}, boost2 lvl = {stats[session]["Bull"]["boost2"]}, friends number: {len(logins)}, friends: {[item["login"] for item in stats[session]["Bull"]["friends"]]}, completed tasks: {stats[session]["Bull"]["completed"]}")
                if choose_bot == 2:
                    print(f"{session}: balance = {stats[session]["Altooshka"]["balance"]}")
                if choose_bot == 3:
                    await vertusStats()

    if action == 1:

        selected_bots = input("Select bots (e. 1 2):\n1. Bull\n2. Altooshka\n3. Vertus\n4. Major\n\n> ")
        accounts = await Accounts().get_accounts()

        tasks = []
        for thread, account in enumerate(accounts):
            session_name, phone_number, proxy = account.values()
            if "1" in selected_bots:
                tasks.append(asyncio.create_task(start(session_name=session_name, phone_number=phone_number, thread=thread, proxy=proxy)))
            if "2" in selected_bots:
                tasks.append(asyncio.create_task(altooshkaStart(session_name=session_name, phone_number=phone_number, thread=thread, proxy=proxy)))
            if "3" in selected_bots:
                tasks.append(asyncio.create_task(vertusStart(session_name=session_name, phone_number=phone_number, thread=thread, proxy=proxy)))
            if "4" in selected_bots:
                tasks.append(asyncio.create_task(majorStart(session_name=session_name, phone_number=phone_number, thread=thread, proxy=proxy)))

        await asyncio.gather(*tasks)


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())