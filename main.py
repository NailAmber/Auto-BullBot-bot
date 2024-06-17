from utils.core import create_sessions
from utils.telegram import Accounts
from utils.starter import start
import asyncio
import os
import json


async def main():
    action = int(input("Select action:\n1. Start soft\n2. Print stats\n3. Create sessions\n\n> "))

    if not os.path.exists('sessions'): os.mkdir('sessions')
    if not os.path.exists('statistics'): os.mkdir('statistics')
    if not os.path.exists('sessions/accounts.json'):
        with open("sessions/accounts.json", 'w') as f:
            f.write("[]")

    if action == 3:
        await create_sessions()

    if action == 2:
        if os.path.exists("./statistics/stats.json"):
            stats = {}
            with open("./statistics/stats.json", "r") as f:
                stats = json.load(f)
            
            for session in stats:
                logins = [item["login"] for item in stats[session]["friends"]]
                print(f"{session}: balance = {stats[session]["balance"]}, boost1 lvl = {stats[session]["boost1"]}, boost2 lvl = {stats[session]["boost2"]}, friends number: {len(logins)}, friends: {[item["login"] for item in stats[session]["friends"]]}, completed tasks: {stats[session]["completed"]}")

    if action == 1:
        accounts = await Accounts().get_accounts()

        tasks = []
        for thread, account in enumerate(accounts):
            session_name, phone_number, proxy = account.values()
            tasks.append(asyncio.create_task(start(session_name=session_name, phone_number=phone_number, thread=thread, proxy=proxy)))

        await asyncio.gather(*tasks)


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())