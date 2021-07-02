import discord
import os
from dotenv import load_dotenv
import requests
from requests.exceptions import Timeout
from bs4 import BeautifulSoup
from pdf2image import convert_from_bytes


# loading .env file with token
load_dotenv()

# creating discord client
client = discord.Client()

# on_ready event
@client.event
async def on_ready():
    print("We have logged in a as {0.user}".format(client))

# on_message events
@client.event
async def on_message(message):
    
    # to prevent response to bot
    if message.author == client.user:
        return

    # Initial hello test
    if message.content.startswith("!hello"):
        await message.channel.send("Hello")

    # Help
    if message.content.startswith("!sneak --help"):
        await message.channel.send("With '!sneak' you can preview pdfs, especially for arxiv papers.\nMust be a valid url, ends with pdf.\ne.g. !sneak https://arxiv.org/pdf/2102.04754.pdf")

    # !sneak function, depends .pdf at the end of message
    if message.content.startswith('!sneak') and message.content.endswith('.pdf'):
        
        # Dirty sanity check
        sneak_message = 'http'+ message.content.split("http")[1]
        
        #-- Parsing header info from arxiv page --#

        async with message.channel.typing():

            # Parsing Header information
            if 'arxiv' in sneak_message:

                # target url
                url = sneak_message.replace('/pdf', '/abs')
                  
                # making requests instance
                try:
                    reqs = requests.get(url, verify=True)

                    # using the BeautifulSoup to parse header information from arxiv page.
                    soup = BeautifulSoup(reqs.text, 'html.parser')
                    title = soup.find_all('title')[0].get_text()
                    submitted = soup.find_all(class_='dateline')[0].get_text().strip()
                    authors = soup.find_all(class_='authors')[0].get_text()
                    
                    # displaying the title, submission date, and authors
                    await message.channel.send("Parsing PDF: \n```{}\n{}\n{}```".format(title, submitted, authors))

                except:
                    await message.channel.send("Error: Header Arxiv")

            else:
                await message.channel.send("No arxiv format")
        
        #-- Parsing PDF --#

        async with message.channel.typing():

            # Parsing PDF    
            try:
                # target pdf, checks for max size before
                pdf = requests.get(sneak_message, stream=True, verify=True)
                if int(pdf.headers['content-length']) > 15000000:
                   await message.channel.send("Error: PDF beyond 15MB limit")
 
                else:
                    # converts bytes to temp-image and uploads it
                    screenshot = convert_from_bytes(pdf.content, dpi=50,  last_page=1)[0]
                    screenshot.save("screenshot.png", filename="screenshot.png")
                    await message.channel.send(file=discord.File("screenshot.png"))

                # Posts first 3 pages
                #for i in range(0,3):
                #    screenshot = convert_from_bytes(pdf.content, dpi=50,  last_page=3)[i]
                #    screenshot.save("screenshot{}.png".format(i), filename="screenshot{}.png".format(i))
                #await message.channel.send(files=[discord.File("screenshot0.png"), discord.File("screenshot1.png"), discord.File("screenshot2.png")])
            except:
                await message.channel.send("Error: Couldn't parse PDF")

# runs client with token from env file.
client.run(os.getenv('TOKEN'))

