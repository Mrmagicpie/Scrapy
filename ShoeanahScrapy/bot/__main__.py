#
#           ShoeanahScrapy/bot __main__.py | 2021 (c) Mrmagicpie
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#
# General things used in the bot.
import discord, asyncio, os, logging, multiprocessing, json
from discord.ext import commands
from yaml import safe_load as sl
from io import BytesIO

# The CrawlerProcess will run the scraper properly.
from scrapy.crawler import CrawlerProcess

# Import the scraper to be used in the CrawlerProcess.
from scraper import PyPiScraper

# Import multiprocessing process that we can run the scraper more than once.
#   Without multiprocessing you can only run the spider once!
from multiprocessing import Process
#
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#
# Set logging so it doesn't log everything - if you don't do this it isn't pretty!
logging.getLogger('scrapy').propagate = False
logs_e = logging.getLogger("discord")
logs_e.setLevel(logging.ERROR)
#
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#
if "config.yml" not in os.listdir(os.getcwd()):
    with open("config.yml", "w") as f:
        config_file = """

# ShoeanahScrapy/bot config.yml | 2021 (c) Mrmagicpie

token: "put your token here"
prefixes:
  - "bot prefix "
  - "bot name "
        """
        f.write(config_file)
        raise Exception("Please fill out your config with your bot's details!")

config = sl(open("config.yml"))
#
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#
async def get_prefix(bot, message):
    # prefixes = ["(main prefix)", "(bot name) "]
    prefixes = config['prefixes']
    return commands.when_mentioned_or(*prefixes)(bot, message)
#
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#
bot = commands.Bot(command_prefix=get_prefix, intents=discord.Intents.all())
#
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#
@bot.event
async def on_ready():

    print(f'''
|--------------------|
| Bot ready!         |
| Signed in as:      |
|    {bot.user}    |
|--------------------|
    ''')

    await bot.change_presence(status=discord.Status.online,
                              activity=discord.Activity(name="Still waking up 😒, hold on!",
                                                        type=discord.ActivityType.watching))

    await asyncio.sleep(10)
    await bot.change_presence(status=discord.Status.online, activity=discord.Activity(name="Change me", type=discord.ActivityType.playing))

#
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#
def run_scraper(queue):
    project = queue.get()
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
    })
    process.crawl(PyPiScraper, project=project)
    process.start()
    queue.put(project)

#
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#
@bot.command()
async def test(ctx):
    project = {}
    queue = multiprocessing.Queue()
    queue.put(project)
    p = Process(target=run_scraper, args=(queue,))
    p.start()
    p.join()
    project = queue.get()
    f = BytesIO(project)
    await ctx.send(f"We ran your scraper, and the output is sent in a file!", file=discord.File(f, "Scrapper Output.json"))
    return

#
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#
bot.run(config['token'])
#
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#
