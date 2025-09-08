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

#Setup Header for API calls incase discussion is needed. 
headers = {
    'User-Agent':'Discord: @Pseudechis'
}


intents = discord.Intents.default()
intents.message_content = True
intents.members = True  
intents.presences = True 
bot = commands.Bot(command_prefix="!", description='BLNC Bot',intents=intents)

key = open("Key.txt").read()
ScripItemsdf = pd.read_csv('Scripitems.csv')
ExpensiveItemsdf = pd.read_csv('Expensiveitems.csv')

#Setup Functions
def fetch_prices_for_df(df, quantity, item_id_col="Item_ID", world="Exodus"):
    """
    Fetches prices for all unique Item_IDs in the DataFrame in a single API call
    and maps them back to the correct rows.

    Parameters:
        df: DataFrame containing an Item_ID column.
        item_id_col: Name of the column containing item IDs.
        world: World/server name for Universalis API.

    Returns:
        Original DataFrame with two new columns, one being "Price" which shows the price for the item, the other being "Gil_Per_Scrip"
        which shows how much gil you get per scrip spent.
    """
    # Get all item IDs from the dataframe for the currency type requested
    item_ids = df[item_id_col].unique()
    id_string = ",".join(map(str, item_ids))

    #Call Universalis aggregation API and feed it the world function as well as the comma seperated string of item ids
    api_url = f"https://universalis.app/api/v2/aggregated/{world}/{id_string}"
    try:
        response = re.get(api_url, headers=headers)
        response.raise_for_status()
        data = response.json()
    except re.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return df.assign(Price=None)

    #Build lookup dictionary for aggregated prices by item id for the world requested
    price_lookup = {}
    salesvolume_lookup = {}
    for result in data.get("results", []):
        item_id = result['itemId']
        try:
            price = result["nq"]["minListing"]["world"]["price"]
            salesvolume = result["nq"]["dailySaleVelocity"]["world"]["quantity"]
        except (TypeError, KeyError):
            price = None
            salesvolume = None
        price_lookup[item_id] = price
        salesvolume_lookup[item_id] = salesvolume

    #create new DF columns for the information above by mapping them back to the data frame utilziing the item id, while also creating a Gil Per Currency column
    df["Price"] = df[item_id_col].map(price_lookup)
    df["Gil_Per_Currency"] = df["Price"]/df["Currency_Cost"]
    df["Salesvolume"] = df[item_id_col].map(salesvolume_lookup)
    
    #Return Dataframe with only the columns that we are interested in
    return df[['Item_Name','Currency_Type','Currency_Cost','Price','Gil_Per_Currency','Salesvolume']].sort_values(by="Gil_Per_Currency", ascending = False)[:quantity].round(2)

def fetch_price_for_expensive_items(df,  item_id_col="Item_ID", Region = "North-America",World = "Exodus"):

    """
    Fetches prices for all the "Expensive" items that were imported from the csv, feeds them through universalis real time pricing API for NA prices, and Aggreation API for exodus prices.
    Picks the cheapest North-America Price, compares it to the aggregated Exodus price and then exports that to a df with a pricing ratio.
    The goal of this function is to find mispriced items, or items that are significantly cheaper than they are on exodus for potential resell.

    Parameters:
        df: DataFrame containing an Item_ID column IE: the dataframe that was created from our expensive items csv.
        item_id_col: Name of the column containing item IDs.
        Region: The region with which the real time pricing api will be ran against to find the cheapest examples of the items.
        World: The world that the aggregation API will be ran against to comapre the cheapest price to in order to determine if it is a good deal.

    Returns:
        A data frame that contains columns for the name of each of the expensive items,"Cheapest" price for each of the expensive items,
        the world that has the item for that price, the aggregated price for the world that was outlined in the paramater above, and a ratio
        showing how much cheaper the cheapest price is compared to that aggregated price.
    """
    #Get item ids for "expensive" items from the dataframe that is fed to the function
    item_ids = df[item_id_col].unique()
    id_string = ",".join(map(str, item_ids))

    #Call Universalis real time pricing API for regional pricing and aggregation API for exodus pricing to give a better idea of "real pricing ie: whatsa  deal"
    region_api_url = f'https://universalis.app/api/v2/{Region}/{id_string}?listings=1&statsWithin=65000&fields=items.listings.pricePerUnit%2Citems.listings.worldName'
    world_api_url = f"https://universalis.app/api/v2/aggregated/{World}/{id_string}"
    try:
        region_response = re.get(region_api_url, headers=headers)
        world_response = re.get(world_api_url, headers=headers)
        region_response.raise_for_status()
        world_response.raise_for_status()
        regiondata = region_response.json()
        worlddata=world_response.json()
    except re.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return df.assign(Price=None)
    #build dictionary of cheapest NA Priced item and the world that it is on by item id
    na_price_lookup = {}
    world_name_lookup = {}
    
    for result in regiondata.get("items", []):
        item_id = result
        for result2 in regiondata.get("items",[]).get(item_id,[]).get("listings",[]):
            try:
                naprice = result2["pricePerUnit"]
                world = result2["worldName"]
            except (TypeError, KeyError):
                naprice = None
                world = None
        na_price_lookup[int(item_id)] = naprice
        world_name_lookup[int(item_id)] = world

    #build dictionary of aggreated price of each item based on the world entered, default being Exodus
    world_price_lookup = {}
    for result in worlddata.get("results",[]):
        item_id = result['itemId']
        try:
            worldprice = result["nq"]["minListing"]["world"]["price"]
        except (TypeError, KeyError):
            worldprice = None
        world_price_lookup[item_id] = worldprice
    
    #create new DF columns for the information above by mapping them back to the data frame utilziing the item id, while also creating a price ratio column based on that information
    df['CheapestPrice'] = df[item_id_col].map(na_price_lookup)
    df['CheapestWorld'] = df[item_id_col].map(world_name_lookup)
    df['ExodusPrice'] = df[item_id_col].map(world_price_lookup)
    df['PriceRatio'] = df['CheapestPrice']/df['ExodusPrice']

    #return the DF with the information we are interested in
    return df[['Item_Name','CheapestPrice','CheapestWorld','ExodusPrice','PriceRatio']].round(2)
@bot.event
async def on_ready():
    Activity = discord.Game(name = "BLNC Bot")
    await bot.change_presence(activity = Activity)
    bot.loop.create_task(checkprices())
    print("Bot is running")

async def checkprices():
    while True:
        await asyncio.sleep(60)
        print("Checking Prices!")
        ExpensiveItemCheck = fetch_price_for_expensive_items(ExpensiveItemsdf)
        GoodPricedItems = ExpensiveItemCheck.query("PriceRatio <= 0.50")
        Channel = bot.get_channel(1414393136779886653)
        if GoodPricedItems.empty == True:
            print("No Exceptionally Well Priced items found")
        else:
            for index, row in GoodPricedItems.iterrows():
                Name = row["Item_Name"]
                CheapestWorld = row["CheapestWorld"]
                CheapestPrice = row["CheapestPrice"]
                ExoPrice = row["ExodusPrice"]
                Ratio = row["PriceRatio"]
                goodpricedembmsg = discord.Embed(title=f"{Name} is well priced on {CheapestWorld}", color= discord.Color.dark_red())
                goodpricedembmsg.add_field(
                    name = f"**{Name}**",
                    value=(
                    f'> Item Name: {Name}\n'
                    f'> Cheapest World: {CheapestWorld}\n'
                    f'> Cheapest Price: {CheapestPrice:,}\n'
                    f'> Exodus Price: {ExoPrice:,}\n'
                    f'> Price Ratio: {Ratio}'))
                goodpricedembmsg.set_footer(text="The Cheapest Prices are checked on a 60 second basis utilizing Universalis Real-Time API, while the Exodus Prices are checked utilizing the Universalis Aggreation API to get better averages.")
                await Channel.send(embed = goodpricedembmsg)

@bot.command()
async def gps(ctx,scriptype, quantity = 5):
    scriptype = scriptype.lower()
    scripitems = ScripItemsdf.query(f"Currency_Type == '{scriptype}'")
    QueriedItems = fetch_prices_for_df(scripitems, quantity, item_id_col="Item_ID",world="Exodus")
    msg = {}
    embdmsg = []
    for index, row in QueriedItems.iterrows():
        Name = row['Item_Name']
        Script = row['Currency_Type']
        Cost = row['Currency_Cost']
        Price = row['Price']
        GilPerScript = row['Gil_Per_Currency']
        DailySales = row['Salesvolume']
        embdmsg.append((Name,Script,Cost,Price,GilPerScript,DailySales))
    embed2 = discord.Embed(title = 'Current Top ' + str(quantity) +' '+ str(scriptype) + ' item listings (Gil Per Currency) ', color = discord.Color.red())
    for ItemName, ScriptType, Cost, Price, GilPerScript, DailySales in embdmsg:
        embed2.add_field(
            name=f'**{ItemName}**',
            value=(
                f'> Currency Type: {ScriptType}\n'
                f'> Cost: {Cost:,}\n'
                f'> Sell Price: {Price:,}\n'
                f'> Gil Per Currency: {GilPerScript:,}\n'
                f'> Daily Sales: {DailySales:,}'))
        embed2.set_footer(text="The information provided comes from the Universalis API, information should be utilized to make informed decisions. Rankings can be influenced by items with few inflated listings")
    channel = bot.get_channel(ctx.channel.id)
    await channel.send(embed=embed2)
bot.run(str(key))



