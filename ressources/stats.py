#!/usr/bin/env python3
#coding:utf-8
import nest_asyncio

import os, json, asyncio
from aiohttp import ClientSession
from ressources.tools import *
import ressources.SqlManagment as SqlManagment
from ressources.exceptions import *

# import __init__
# from tools import *
# import SqlManagment as SqlManagment
# from exceptions import *

nest_asyncio.apply() #fix asyncio error

class Stats:
    """Get apex legends stats"""
    def __init__(self, player: str = "", platform: str = 'pc'):
        self.player = player
        self.base_platform = platform.lower()
        self.platform = platformConvert(platform)

    async def req(self, session):
        url = f"https://public-api.tracker.gg/apex/v1/standard/profile/{self.platform}/{self.player}"
        async with session.get(url, headers=headers) as resp:
            try:
                assert resp.status == 200
            except AssertionError:
                raise PlayerNotFound(resp.status)
            return await resp.json()

    async def mult_req(self,player, platform, session):
        url = f"https://public-api.tracker.gg/apex/v1/standard/profile/{platformConvert(platform)}/{player}"
        async with session.get(url, headers=headers) as resp:
            try:
                assert resp.status == 200
            except:
                await asyncio.sleep(60)
            return await resp.json()

    async def single_request(self, player, platform):
        async with ClientSession() as session:
            task = asyncio.ensure_future(self.req(session))
            responses = await asyncio.gather(task)
        stat_tmp, legends_stat = {}, []
        platform = 'xbl' if self.platform == '1' else self.base_platform
        data = {"level":responses[0]['data']['metadata']['level'],
                "name":responses[0]['data']['metadata']['platformUserHandle'],
                "profile":f"https://apex.tracker.gg/profile/{platform}/{responses[0]['data']['metadata']['platformUserHandle']}"}
        for i, _data in enumerate(responses[0]['data']['children']):
            stat_tmp['legend'] = _data['metadata']['legend_name']
            for stat in _data['stats']:
                stat_tmp[stat['metadata']['name']] = str(stat['displayValue'])
            legends_stat.append({str(i):stat_tmp})
            stat_tmp = {}

        data['legends'] = legends_stat
        all_stats = {}
        for _all in responses[0]['data']['stats']:
            if _all['metadata']['name'] != 'Level':
                all_stats[_all['metadata']['name']] = _all['displayValue']

        data['all'] = all_stats
        return data

    async def multi_requests(self, players: dict = {}):
        global leaderboard_sorted
        if not len(players):
            print("Missing arguments")
            return
        tasks = []
        acc = 1
        async with ClientSession() as session:
            for player, platform in players.items():
                if acc % 31 == 0:
                    await asyncio.sleep(61)
                task = asyncio.ensure_future(self.mult_req(player, platform, session))
                tasks.append(task)
                acc+=1
            responses = await asyncio.gather(*tasks)
        leaderboard_sorted = {}
        players_keys = list(players.keys())
        players_values = list(players.values())
        for i,rtask in enumerate(responses):
            try:
                for _all in rtask['data']['stats']:
                    if _all['metadata']['name'] == 'Kills':
                        leaderboard_sorted[rtask['data']['metadata']['platformUserHandle']] = int(_all['value'])
                        print(leaderboard_sorted)
            except Exception as e:
                print(f"{i} {players_keys[i]} : {players_values[i]} {e} {responses[i]}")
                continue
        return leaderboard_sorted

    def single_data(self):
        return asyncio.run(self.single_request(self.player, self.platform))

    def multi_data(self, players: dict):
        return sorted(asyncio.run(self.multi_requests(players)).items(), key = lambda kv:(kv[1], kv[0]), reverse=True)


    async def statsExists(self):
        try:
            async with ClientSession() as session:
                task = asyncio.ensure_future(self.req(session))
                responses = await asyncio.gather(task)
                return True
        except PlayerNotFound:
            return False

    def exists(self):
        return asyncio.run(self.statsExists())

    def mozambique(self): #Just do a request for apexlegendsstatus database
        pass
        # try:
        #     return requests.get(f'http://api.mozambiquehe.re/bridge?platform={legendStatusConvert(self.platform)}&player={self.player}&auth={AUTH}&version=2')
        # except Exception as e:
        #     print(f'{type(e).__name__} : {e}')
        #     return

    async def iconUrl(self):
        global icon
        async with ClientSession() as session:
            task = asyncio.ensure_future(self.req(session))
            icon = await asyncio.gather(task)
        return icon
    
    def get_icon(self):
        return list(asyncio.run(self.iconUrl()))[0]['data']['children'][0]['metadata']['icon']