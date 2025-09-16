Discord Bot whos primary goal is to assist with finding the best options for you to spend your currencies on and turn them into gil. More features to come soon as requested.    for information related to his bot / script plus contact Pseudechis on discord.
-----------------------------------------------------------
<b> Current primary command is !gps [scriptype] [quantity] </b>  
<b> if the scrip type is two words then it needs to be in quotation marks as well <b>  
<b>The scrip types available are as follows:  </b>  

orange crafter   
orange gatherer  
purple crafter  
purple gatherer  
skybuilders  
faux  
bozjan clusters  
cosmocredit  
oc silver  
oc gold  
sanguinite  

-----------------------------------------------------------
Other commands include
-----------------------------------------------------------

Ping - which makes the bot ping the specified role  

NoPing - which makes the bot not ping  

Threshold - which tells you the current priceratio (default of 0.33) for it posting a message.  

changethreshold(threshold) - which will allow you to change the threshold it should be a decimal IE: 0.3 would be 30% cheaper than world pricing. 

currencyrefresh- which refreshes the currency item data frame based on an update to the csv.  

itemrefresh - which refreshes the Expensiveitems df based on updates to that csv.  

deleteitem(itemname,csv = False) - which deletes an item from the dataframe temporarily, it will be readded upon running the itemrefresh command, if the csv command is added as True then it will permanetely delete the item from the csv.  

additem(itemname,itemid,csvb = False) - which adds an item to the dataframe temporarily, it will be lost among refresh of the dataframe. if csv is changed to true then it will be added to the csv permanetely. the permanent versions of delete / add item can only be ran by the guild owner.

-----------------------------------------------------------
Also has a task that auto-runs based on an asyncio.sleep period of 60 seconds that checks for prices items that are potentially mispriced or significantly cheaper on another world in the region (default North-America) than the selected world (default Exodus) if 
they are found to be significantly cheaper based on a price ratio (currently <=0.33 or 66% cheaper) then a message is posted to a specified discord channel alerting of these mispriced item, how much they are, and what world they are on.
