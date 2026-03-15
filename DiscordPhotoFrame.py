#ToDo: Add bot to more channels, printing text quotes
#Probably should be converted into a bot ie @bot.command, though for now it only listens
#Weird ideas: "quote" IE ability to send text to it and it composites with previous image, hit button to switch mode to weather or something boring, mirror gdrive grocery list
#Make a basic frame, figure out where to put it, power supply? Auto restart script on reboot

import discord
import os

import gpiod #for LED
import gpiodevice #For LED
from gpiod.line import Bias, Direction, Value

from inky.auto import auto #e-ink display library thing
inky = auto(ask_user=True, verbose=True) #setting the var
from PIL import Image #basic image editor
from PIL import ImageOps #More advanced image editor

#Async nonsense
import functools
import typing
import asyncio

import requests
import re

# Add an ".env" file with TOKEN=your_token_here, or just plaintext it lol
import os #Uses "pip install python-dotenv" to read the .env file for the bot token.

#Load environment variables (bot token)
load_dotenv() #Comment out if you wanna use plaintext
TOKEN = os.getenv("TOKEN")

image_types = ["png", "jpeg", "gif", "jpg", "mp4", "mov"] #You can add more attachments/formats here to be saved.

LED_PIN = 13 #gpio for screen LED
chip = gpiodevice.find_chip_by_platform()

# Setup for the LED pin
led = chip.line_offset_from_id(LED_PIN)
gpio = chip.request_lines(consumer="inky", config={led: gpiod.LineSettings(direction=Direction.OUTPUT, bias=Bias.DISABLED)})


def to_thread(func: typing.Callable) -> typing.Coroutine:
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        return await asyncio.to_thread(func, *args, **kwargs)
    return wrapper


@to_thread
def updateInky(file):
    print("Submitting image to inky")
    gpio.set_value(led, Value.ACTIVE)#LED on when reciving  
    openedImage = Image.open(file)
    im = openedImage.convert('RGB') #sanitizes the image (removes gif frames)
    resizedimage = im.resize(inky.resolution)
    resizedimage = ImageOps.pad(im, inky.resolution, color="#fff")
    try:
        inky.set_image(resizedimage)
    except TypeError:
        inky.set_image(resizedimage)
    inky.show()
    gpio.set_value(led, Value.INACTIVE)#LED off when done


class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

    #Listens for star emoji reaction from every message
    async def on_reaction_add(self, reaction, user):
        message = reaction.message # our embed
        print("Reaction")
        if str(reaction.emoji) == "⭐": #checking the emoji
            print("Found Star Reaction")
            if "https://images-ext-1.discordapp.net" in message.content or "https://tenor.com/view/" in message.content:
                self.image = message.content #link to tenor gif - not formatted
                print("Found tenor link...")
                url = self.image
                if re.findall(r'https?://tenor.com/view\S+', url):
                    tenor_http = requests.get(url)
                    direct_link_list = re.findall(r"https?://media1.tenor.com/m\S+.gif", tenor_http.text)
                    direct_link = direct_link_list[0]
                    print(direct_link)
                    img_data = requests.get(direct_link).content
                    with open(f'attachments/tenorgif', 'wb') as handler:
                        handler.write(img_data)# writes image to disk
                    await updateInky(f'attachments/tenorgif')
                
            for attachment in message.attachments:
                if any(attachment.filename.lower().endswith(image) for image in image_types):
                    await attachment.save(f'attachments/{attachment.filename}') 
                    # 'attachments/{{attachment.filename}' is the PATH to where the attachments/images will be saved. Example: home/you/Desktop/attachments/{{attachment.filename}
                    print(f'Attachment {attachment.filename} has been saved to directory/folder > attachments.')
                    await updateInky(f'attachments/{attachment.filename}') 
                    #you have to run everything async with the "await" command to not block the thread       



intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)
client.run('TOKEN')