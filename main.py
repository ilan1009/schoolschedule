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


def get_stuff(home_room):
    """Gets the schedule changes for specific class and return using SELENIUM WEB DRIVER"""

    ############################
    #                          #
    #         CRAWLING         #
    #                          #
    ############################

    url = "https://www.alliancetlv.com/עדכוני-מערכת"  # URL

    # Chrome options
    options = Options()
    options.add_argument("--headless")

    # Launch web driver
    driver = webdriver.Chrome(options=options)
    driver.get(url)

    # Enter IFRAME element
    frame = WebDriverWait(driver, 10).until(
        ec.visibility_of_element_located((By.CSS_SELECTOR, 'div#comp-kg9mlfwo iframe')))

    driver.switch_to.frame(frame)

    # Select class from dropdown
    drp_class = Select(driver.find_element(By.CSS_SELECTOR, "#TimeTableView1_ClassesList"))
    drp_class.select_by_visible_text(str(home_room))

    # Select schedule and click it with JS
    changes_button = driver.find_element(By.CSS_SELECTOR, "#TimeTableView1_btnChanges")
    changes_button.click()

    # Get the text element hidden in the schedule tab
    changes_txt = driver.find_element(By.CSS_SELECTOR, '#TimeTableView1_PlaceHolder > div')

    ############################
    #                          #
    #     TEXT FORMATTING      #
    #                          #
    ############################

    if changes_txt.text == 'אין שינויים':  # If empty just print that and return
        return "No schedule changes"

    # Some kind of hard to read text formatting ahead; not the most optimal way.

    # Open the file, clear it and write new text
    with open('vars/tmp_file.txt', 'w', encoding="utf-8") as tmp_file:
        tmp_file.truncate(0)
        tmp_file.write(changes_txt.text)
        tmp_file.close()

    # Open the files again and truncate
    with open('vars/tmp_file.txt', 'r', encoding="utf-8") as tmp_file, \
            open('vars/tmp_file_out.txt', 'w', encoding="utf-8") as tmp_file_out:
        tmp_file_out.truncate()
        while 1:
            # Get next line from file
            line = tmp_file.readline()

            # if line is empty
            # end of file is reached
            if not line:
                break
            if 'ביטול שעור' in line:
                # print("Line{}: {}".format(count, line.strip()))
                for i in range(8):
                    if 'שיעור ' + str(i) in line:
                        tmp_file_out.write(f'Period {str(i)} cancelled! W\n')
            elif 'הזזת שיעור' in line:
                for i in range(8):
                    if 'לשיעור ' + str(i) in line:
                        lesson = line.split(' לשיעור')[0].split(', ')[2]
                        tmp_file_out.write(f'Class "{lesson}" moved to period {str(i)}')
            elif 'מילוי מקום' in line:
                for i in range(8):
                    if 'שיעור ' + str(i) in line:
                        lesson = line.split(', ')[4]
                        print(lesson)
                        tmp_file_out.write(f'Period {str(i)} replaced with class "{lesson}"')

            else:
                tmp_file_out.write(line)

    # Read file and return it
    with open('vars/tmp_file_out.txt', 'r+', encoding="utf-8") as tmp_file_out:
        out = tmp_file_out.read()
        tmp_file_out.truncate()

    return out


# Some options
intents = discord.Intents.all()

bot = commands.Bot(command_prefix='$', intents=intents)


async def send_stuff():
    """Function to schedule the sending of the schedule changes of the selected classes when
    called at 7:00 every school day by a Cron"""

    print('Sending daily morning message')

    await bot.wait_until_ready()  # Make sure your guild cache is ready

    t_1 = get_stuff('ט - 1')  # ט1
    t_2 = get_stuff('ט - 2')  # ט2
    t_3 = get_stuff('ט - 3')  # ט3

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
    scheduler.add_job(send_stuff, CronTrigger(day_of_week="0, 1, 2, 3, 4, 6", hour="7", minute="0", second="30"))
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
        await loading_msg.edit(content='\n```\n' + (str(get_stuff(f'ט - {arg1}'))) + '\n```')
        print('Task completed successfully')


@bot.command(name='setchannel')
async def setchannel(ctx):
    """Sets the morning message to send to this channel."""
    with open('vars/morningid.txt', 'a+') as channelfile:
        channelfile.truncate(0)
        channelfile.write(str(ctx.channel.id))
        print(ctx.channel.name)


bot.run('MTAzMzE3NDc1NzQyMTYzMzU1Ng.G9DLiS.mv8VEZ_cnAx8P5mkqcYlCMutRTfHvodzQurqsE')
