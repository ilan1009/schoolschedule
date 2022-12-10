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

URL = "https://www.alliancetlv.com/עדכוני-מערכת"  # URL

# Chrome options
options = Options()
options.add_argument("--headless")

# Launch web driver
driver = webdriver.Chrome(options=options)
driver.get(URL)

# Enter IFRAME element
frame = WebDriverWait(driver, 10).until \
    (ec.visibility_of_element_located((By.CSS_SELECTOR, 'div#comp-kg9mlfwo iframe')))

driver.switch_to.frame(frame)


async def get_stuff(home_room, driver, refresh_option=False):
    """Gets the schedule changes for specific class and return using SELENIUM WEB DRIVER"""
    ############################
    #                          #
    #         CRAWLING         #
    #                          #
    ############################

    if refresh_option:
        driver.navigate().refresh()
    # Select class from dropdown
    drp_class = Select(driver.find_element(By.CSS_SELECTOR, "#TimeTableView1_ClassesList"))
    drp_class.select_by_visible_text(str(home_room))

    # Select schedule and click it with JS
    changes_button = WebDriverWait(driver, 10).until(
        ec.visibility_of_element_located((By.CSS_SELECTOR, '#TimeTableView1_btnChanges')))
    changes_button.click()

    # Get the text element hidden in the schedule tab
    changes_txt = WebDriverWait(driver, 10).until(
        ec.visibility_of_element_located((By.CSS_SELECTOR, '#TimeTableView1_PlaceHolder')))

    ############################
    #                          #
    #     TEXT FORMATTING      #
    #                          #
    ############################

    # Some kind of hard to read text formatting ahead; not the most optimal way.

    # Open the file, clear it and write new text
    with open('vars/tmp_file.txt', 'r+', encoding="utf-8") as tmp_file:
        tmp_file.truncate(0)
        tmp_file.write(changes_txt.text)

    with open('vars/tmp_file.txt', 'r+', encoding="utf-8") as tmp_file:
        data = []
        for i in range(8):
            data.append(' \n')
        while 1:
            # Get next line from file
            line = tmp_file.readline()

            # if line is empty
            # end of file is reached
            if not line:
                break
            if 'ביטול שעור' in line:
                for i in range(8):
                    if 'שיעור ' + str(i) in line:
                        data[i - 1] = f'Period {str(i)} cancelled! W\n'
            elif 'הזזת שיעור' in line:
                for i in range(8):
                    if 'לשיעור ' + str(i) in line:
                        lesson = line.split(' לשיעור')[0].split(', ')[2]
                        data[i - 1] = f'Class "{lesson}" moved to period {str(i)}\n'

            elif 'מילוי מקום' in line:
                for i in range(8):
                    if 'שיעור ' + str(i) in line:
                        lesson = line.split(', ')[4]
                        print(lesson)
                        data[i - 1] = f'Period {str(i)} replaced with class "{lesson}"\n'

            elif 'החלפת חדר' in line:
                for i in range(8):
                    if 'שיעור ' + str(i) in line:
                        data[i - 1] = line
    out = ""
    return out.join(data)


# Some options
intents = discord.Intents.all()

bot = commands.Bot(command_prefix='$', intents=intents)


async def send_stuff():
    """Function to schedule the sending of the schedule changes of the selected classes when
    called at 7:00 every school day by a Cron"""

    print('Sending big message')

    await bot.wait_until_ready()  # Make sure your guild cache is ready

    t_1 = await get_stuff('ט - 1', driver)  # ט1
    t_2 = await get_stuff('ט - 2', driver)  # ט2
    t_3 = await get_stuff('ט - 3', driver)  # ט3

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

    # Read file to get previously saved ID
    with open('vars/morningid.txt', 'r') as channelfile:
        # Issue a warning
        if channelfile.readline() == '':
            print('SET CHANNEL URGENTLY')
        else:
            global channel  # Set global variable
            channelfile.seek(0)
            channelid = channelfile.read()
            channel = bot.get_channel(int(channelid))
            print(channel.name)

    # Job that runs send_stuff every day at 7:00
    scheduler.add_job(send_stuff, CronTrigger(day_of_week="0, 1, 2, 3, 4, 6", hour="6", minute="50", second="0"))
    scheduler.start()  # Start


@bot.command(name='send')
async def send(message, arg1=0):
    """A command, Listens for $send, where $ is the prefix. when run with the correct arguments it
     will return the schedule changes of the selected class using the get_stuff() function."""

    print('Command send requested')

    if arg1 == 0:
        await message.channel.send('Failure to provide arguments')
    else:
        await message.channel.send('ט' + str(arg1) + ':')
        loading_msg = await message.channel.send('Loading...')
        g = await get_stuff(f'ט - {arg1}', driver)
        await loading_msg.edit(content='\n```\n' + (str(g)) + '\n```')
        print('Task completed successfully')


@bot.command(name='setchannel')
async def setchannel(ctx):
    """Sets the morning message to send to this channel."""
    with open('vars/morningid.txt', 'a+') as channelfile:
        channelfile.truncate(0)
        channelfile.write(str(ctx.channel.id))
        print(ctx.channel.name)


bot.run('MTAzMzE3NDc1NzQyMTYzMzU1Ng.GiH6ie.SpWYEyTQiV-26vbVyMwnaDLj42ixs8TOH8dcY0')
