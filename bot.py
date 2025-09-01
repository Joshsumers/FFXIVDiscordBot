#import neccessary libaries
import json
import pandas as pd
import requests as re
import statistics
import time
import asyncio
import discord
from discord.ext import commands
from discord.ext.commands import Bot
from collections import defaultdict

#Setup Static Variables
AggregatedAPIBaseURL = 'https://universalis.app/api/v2/aggregated/Exodus/'
CurrentPriceAPIBaseURL = 'https://universalis.app/api/v2/history/North-America/'
CurrentPriceAdditonalParams = '?statsWithin=600000'

headers = {
    'User-Agent':'@Pseudechis'
}


intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # Enable SERVER MEMBERS INTENT
intents.presences = True # Enable PRESENCE INTENT
bot = commands.Bot(command_prefix="!", description='BLNC Bot',intents=intents)

key = open("Key.txt").read()
ScripItemsdf = pd.read_csv('Scripitems.csv')

#Setup Functions
def fetch_prices_for_df(df, item_id_col="Item_ID", world="Exodus"):
    """
    Fetches prices for all unique Item_IDs in the DataFrame in a single API call
    and maps them back to the correct rows.

    Parameters:
        df: DataFrame containing an Item_ID column.
        item_id_col: Name of the column containing item IDs.
        world: World/server name for Universalis API.

    Returns:
        Original DataFrame with two new columns, one being "Price" which shows the price fo the item, the other being "Gil_Per_Scrip"
        which shows how much gil you get per scrip spent.
    """
    # Step 1: Get all unique IDs
    item_ids = df[item_id_col].unique()
    id_string = ",".join(map(str, item_ids))

    # Step 2: Call API once
    api_url = f"https://universalis.app/api/v2/aggregated/{world}/{id_string}"
    try:
        response = re.get(api_url, headers=headers)
        response.raise_for_status()
        data = response.json()
    except re.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return df.assign(Price=None)

    # Step 3: Build lookup dictionary
    price_lookup = {}
    for result in data.get("results", []):
        item_id = result['itemId']
        try:
            price = result["nq"]["minListing"]["world"]["price"]
        except (TypeError, KeyError):
            price = None
        price_lookup[item_id] = price

    # Step 4: Map prices back to DataFrame
    df["Price"] = df[item_id_col].map(price_lookup)
    df["Gil_Per_Scrip"] = df["Price"]/df["Scrip_Cost"]

    return df[['Item_Name','Scrip_Type','Scrip_Cost','Price','Gil_Per_Scrip']].sort_values(by="Gil_Per_Scrip", ascending = False)[:5].round(2)

@bot.event
async def on_ready():
    Activity = discord.Game(name = "BLNC Bot")
    await bot.change_presence(activity = Activity)
    print("Bot is running")

@bot.command()
async def pps(ctx,scriptype):
    scriptype = scriptype.lower()
    scripitems = ScripItemsdf.query(f"Scrip_Type == '{scriptype}'")
    QueriedItems = fetch_prices_for_df(scripitems, item_id_col="Item_ID",world="Exodus")
    msg = {}
    embdmsg = []
    for index, row in QueriedItems.iterrows():
        Name = row['Item_Name']
        Script = row['Scrip_Type']
        Cost = row['Scrip_Cost']
        Price = row['Price']
        GilPerScript = row['Gil_Per_Scrip']
        embdmsg.append((Name,Script,Cost,Price,GilPerScript))
    embed2 = discord.Embed(title = 'Top 5' +' ' + str(scriptype) + ' Items to purchase to sell', color = discord.Color.red())
    for ItemName, ScriptType, Cost, Price, GilPerScript in embdmsg:
        embed2.add_field(
            name=f'**{ItemName}**',
            value=(
                f'> Script Type: {ScriptType}\n'
                f'> Cost: {Cost:,}\n'
                f'> Sell Price: {Price:,}\n'
                f'> Gil Per Script: {GilPerScript:,}'))
    channel = bot.get_channel(ctx.channel.id)
    await channel.send(embed=embed2)
bot.run(str(key))



