Discord Bot whos primary goal is to assist with finding the best options for you to spend your currencies on and turn them into gil. More features to come soon as requested.    for information related to his bot / script plus contact Pseudechis on discord.
-----------------------------------------------------------
<b> Current command is !gps [scriptype] [quantity] </b>  
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

Also has a command that auto-runs based on an asyncio.sleep period of 60 seconds that checks for prices items that are potentially mispriced or significantly cheaper on another world in the region (default North-America) than the selected world (default Exodus) if 
they are found to be significantly cheaper based on a price ratio (currently <=0.50 or 50% cheaper) then a message is posted to a specified discord channel alerting of these mispriced item, how much they are, and what world they are on.
