import discord, random, json, itertools
from urllib.request import urlopen
from bs4 import BeautifulSoup
from discord.ext import commands, tasks
from discord.utils import find
from flask import Flask
from threading import Thread
'''
app = Flask('')

@app.route('/')
def main():
  return "Your Bot Is Ready"

def run():
  app.run(host="98.31.12.77", port=8000)

def keep_alive():
  server = Thread(target=run)
  server.start()

status = itertools.cycle(['with Python','JetHub'])

@tasks.loop(seconds=10)
async def change_status():
  await client.change_presence(activity=discord.Game(next(status)))
'''
def get_prefix(client, message):
  with open("prefixes.json", "r") as f:
    prefixes = json.load(f)
  if prefixes[str(message.guild.id)]:
    return prefixes[str(message.guild.id)]
  return "$"

client = commands.Bot(command_prefix = get_prefix, help_command = None)

@client.event
async def on_guild_join(guild):
  with open("prefixes.json", "r") as f:
    prefixes = json.load(f)

  with open("answers.json", "r") as f:
    answers = json.load(f)

  with open("frequencies.json", "r") as f:
    frequencies = json.load(f)

  with open("channels.json", "r") as f:
    channels = json.load(f)
  
  prefixes[str(guild.id)] = "$"
  frequencies[str(guild.id)] = "0"
  answers[str(guild.id)] = None
  channels[str(guild.id)] = None

  with open("prefixes.json", "w") as f:
    json.dump(prefixes, f, indent=2)

  with open("frequencies.json", "w") as f:
    json.dump(frequencies, f, indent=2)

  with open("answers.json", "w") as f:
    json.dump(answers, f, indent=2)

  with open("channels.json","w") as f:
    json.dump(channels, f, indent=2)

  general = find(lambda x: x.name == "general",  guild.text_channels)
  if general and general.permissions_for(guild.me).send_messages:
    embed=discord.Embed(title="**Hello!**", description="Thank you for inviting me to your server! I'm still in my developmental stages so if you find any bugs, have any suggestions, or would like some help, please join my support server. Any input would be greatly appreciated! https://discord.gg/cBNQpV6rwh", color=discord.Colour.orange())
    await general.send(embed=embed)

@client.event
async def on_guild_remove(guild):
  with open("prefixes.json", "r") as f:
    prefixes = json.load(f)

  with open("answers.json", "r") as f:
    answers = json.load(f)

  with open("frequencies.json", "r") as f:
    frequencies = json.load(f)

  with open("channels.json", "r") as f:
    channels = json.load(f)
  
  prefixes.pop(str(guild.id))
  frequencies.pop(str(guild.id))
  answers.pop(str(guild.id))
  channels.pop(str(guild.id))

  with open("prefixes.json", "w") as f:
    json.dump(prefixes, f, indent=2)

  with open("frequencies.json", "w") as f:
    json.dump(frequencies, f, indent=2)

  with open("answers.json", "w") as f:
    json.dump(answers, f, indent=2)

  with open("channels.json","w") as f:
    json.dump(channels, f, indent=2)

@client.event
async def on_command_error(context, error):
  pass

@client.event
async def on_ready():
  print("Bot is ready.")
  #change_status.start()
  
@client.command()
async def ping(context):
  await context.send(f"bot latency = {round(client.latency * 1000)}ms")

@client.command()
async def changeprefix(context, prefix):
  with open("prefixes.json", "r") as f:
    prefixes = json.load(f)

  prefixes[str(context.guild.id)] = prefix

  with open("prefixes.json", "w") as f:
    json.dump(prefixes, f, indent=2)

  await context.send("Prefix is now " + prefix)

@client.command()
async def freq(context):
  with open("frequencies.json", "r") as f:
    frequencies = json.load(f)

@client.command()
async def changefreq(context, arg):
  try:
    if 0<=float(arg)<=1:
      with open("frequencies.json", "r") as f:
        frequencies = json.load(f)

      frequencies[str(context.guild.id)] = float(arg)

      with open("frequencies.json", "w") as f:
        json.dump(frequencies, f, indent=2)

      await context.send("frequency is now " + arg)
    else:
      await context.send("Sorry, the frequency must be a number between 0 and 1")
  except:
    await context.send("Incompatible frequency")

@client.command()
async def direct(context, message):
  channel = context.guild.get_channel(int(message[2:-1]))
  if channel == None:
    await context.send("Specificied channel could not be found")
  elif channel.permissions_for(context.guild.me).send_messages and channel.permissions_for(context.guild.me).read_messages:

    with open("channels.json", "r") as f:
      channels = json.load(f)

    channels[str(context.guild.id)] = int(message[2:-1])

    with open("channels.json", "w") as f:
      json.dump(channels, f, indent=2)

    await context.send("Future spontaneous trivia questions will be sent to "+message)
  else:
    await context.send("I am not permitted to send and receive messages in this channel")

@client.command()
async def go(context):

  num = random.choice(range(1,348))

  url = "https://senseis.xmp.net/?XuanxuanQijingProblem"+str(num)
  
  try:
    page = urlopen(url)
  except:
    await context.send("Error opening the senseis.xmp.net")

  soup = BeautifulSoup(page, "html.parser")

  var = soup.find(alt="[Diagram]")
  img = var.get("src")
  
  embed=discord.Embed(title="Xuanxuan Qijing Problem "+str(num), url=url, color=discord.Colour.red())
  
  if img:
    embed.set_image(url="https://senseis.xmp.net/"+img)
  await context.send(embed=embed)

  url = "https://senseis.xmp.net/?XuanxuanQijingProblem"+str(num)+"%2FSolution"
  
  try:
    page = urlopen(url)
  except:
    await context.send("Solution does not exist, but feel free to create one by clicking the link in the title!")
    
  soup = BeautifulSoup(page, "html.parser")

  var = soup.find(alt="[Diagram]")
  img = var.get("src")
  
  with open("answers.json", "r") as f:
    answers = json.load(f)

  answers[str(context.guild.id)] = (img,url,num)

  with open("answers.json", "w") as f:
      json.dump(answers, f, indent=2)

@client.command()
async def sol(context):
  with open("answers.json", "r") as f:
    answers = json.load(f)

  img = answers[str(context.guild.id)][0]
  url = answers[str(context.guild.id)][1]
  num = answers[str(context.guild.id)][2]

  embed=discord.Embed(title="Xuanxuan Qijing Problem "+str(num)+" / Solution", url=url, color=discord.Colour.red())
  embed.set_image(url="https://senseis.xmp.net/"+img)

  answers[str(context.guild.id)] = None
  
  with open("answers.json", "w") as f:
      json.dump(answers, f, indent=2)
  
  await context.send(embed=embed)

@client.command()
async def help(context):
  embed=discord.Embed(title="**Command Summary**", description=None, color=discord.Colour.orange())
  embed.add_field(name="**ping**", value="Returns bot latency", inline=False)
  embed.add_field(name="**changeprefix (prefix)**", value="Changes prefix to the given prefix", inline=False)
  embed.add_field(name="**freq**" , value="Returns chance of sending a random problem on each message", inline=False)
  embed.add_field(name="**changefreq**", value="Changes frequeny to the given frequency", inline=False)
  embed.add_field(name="**go**", value="Sends a random tsumego problem", inline=False)
  embed.add_field(name="**sol**", value="Sends solution to most recent tsumego problem", inline=False)
  await context.send(embed=embed)

@client.event
async def on_message(message):
  context = await client.get_context(message)
      
  with open("frequencies.json", "r") as f:
    frequencies = json.load(f)

  f = frequencies[str(context.guild.id)]

  if random.random() < float(f):
    await go(context)

  await client.process_commands(message)

client.run("""bot token""")
