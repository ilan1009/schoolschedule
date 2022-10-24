"""A new discord bot by chips"""
import discord
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from discord.ext import commands
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait


def get_stuff(home_room_index):
    """Gets the schedule changes for specific class and return using SELENIUM WEB DRIVER"""
    url = "https://www.alliancetlv.com/עדכוני-מערכת"  # url

    # home_room_index = home_room_index

    options = Options()
    options.add_argument("--headless")

    # Launch web driver
    driver = webdriver.Chrome(chrome_options=options)
    driver.get(url)

    frame = WebDriverWait(driver, 10).until(
        ec.visibility_of_element_located((By.CSS_SELECTOR, 'div#comp-kg9mlfwo iframe')))
    driver.switch_to.frame(frame)

    # Select class from dropdown
    drp_class = Select(driver.find_element(By.CSS_SELECTOR, "#TimeTableView1_ClassesList"))
    drp_class.select_by_value(str(home_room_index))

    changes_button = driver.find_element(By.CSS_SELECTOR,
                                         "#TimeTableView1_btnChanges")  # Select schedule tab
    changes_button.click()

    changes_txt = driver.find_element(By.CSS_SELECTOR,
                                      '#TimeTableView1_PlaceHolder > div')  # Get the text element

    print(changes_txt.text)
    if changes_txt.text == 'אין שינויים':  # if this do this
        return "No schedule changes"
    else:
        return changes_txt.text


intents = discord.Intents.all()

bot = commands.Bot(command_prefix='$', intents=intents)


async def send_stuff():
    """Function to schedule the sending of the schedule changes of the selected classes when
    called at 7:00 every school day by a Cron"""

    print('Sending daily morning message')

    channel = bot.get_channel(1033324125843894283)  # set channel
    await bot.wait_until_ready()  # Make sure your guild cache is ready

    t_1 = get_stuff(17)  # ט1
    t_2 = get_stuff(18)  # ט2
    t_3 = get_stuff(19)  # ט3

    await channel.send('ט1:')
    await channel.send('```\n' + str(t_1) + '\n```')
    await channel.send('ט2:')
    await channel.send('```\n' + str(t_2) + '\n```')
    await channel.send('ט3:')
    await channel.send('```\n' + str(t_3) + '\n```')


@bot.event
async def on_ready():
    """Runs on ready"""
    print('Connected')

    # Init scheduler
    scheduler = AsyncIOScheduler()
    print('Scheduler initiated')

    # Job that runs send_stuff every day at 7:00
    scheduler.add_job(send_stuff, CronTrigger(day_of_week="0, 1, 2, 3, 4, 6", hour="7", minute="0", second="0"))
    scheduler.start()  # Start


@bot.command(name='send')
async def send(message, arg1=0):
    """A command, Listens for $send, where $ is the prefix. when run with the correct arguments it will return the
    schedule changes of the selected class using the get_stuff() function."""

    print('Command send requested; ' + message)

    arg1index = 16 + arg1

    if arg1 == 0:
        await message.channel.send('Failure to provide arguments')
    else:
        await message.channel.send('ט' + str(arg1) + ':')
        loading_msg = await message.channel.send('Loading...')
        await loading_msg.edit(content='\n```\n' + (str(get_stuff(arg1index))) + '\n```')
        print('Task completed successfully')


toggle = False
bot.run('place')
