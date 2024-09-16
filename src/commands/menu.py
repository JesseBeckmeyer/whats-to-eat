import discord
import json
import aiohttp
from discord.ext import commands
from discord import Option
from datetime import datetime, timedelta

API_URL = "https://api.dineoncampus.com/v1/sites/todays_menu?site_id=64872d0f351d53058416c3d5"
HDR = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}

class Menu(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cache = {}
        self.cache_timestamp = None

    async def fetch_menu_data(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(API_URL, headers=HDR) as response:
                return await response.json()

    async def get_menu_data(self):
        if self.cache_timestamp is None or datetime.now() - self.cache_timestamp > timedelta(days=1):
            self.cache = await self.fetch_menu_data()
            self.cache_timestamp = datetime.now()
        return self.cache

    @discord.slash_command(name="menu", description="Get the menu for a specific period")
    async def menu(self, ctx, period: str = Option(description="The period you want the menu for", choices=["Breakfast", "Lunch", "Dinner"])):
        data_json = await self.get_menu_data()

        desired_stations = {"Homestyle", "500 Degrees", "Flame", "Delicious Without"}

        embed = discord.Embed(title="Today's Menu", color=discord.Color.blue())

        for location in data_json['locations']:
            embed.add_field(name="Location", value=location['name'], inline=False)
            for period_data in location['periods']:
                if period_data['name'].lower() == period.lower():
                    embed.add_field(name="Period", value=period_data['name'], inline=False)
                    for station in period_data['stations']:
                        if station['name'] in desired_stations:
                            station_info = f"**Station Name:** {station['name']}\n"
                            for item in station['items']:
                                station_info += f"**Item Name:** {item['name']}\n"
                                station_info += f"Calories: {item['calories']}\n"
                                station_info += f"Portion: {item['portion']}\n\n"
                            embed.add_field(name=station['name'], value=station_info, inline=False)

        await ctx.respond(embed=embed)

def setup(bot):
    bot.add_cog(Menu(bot))
