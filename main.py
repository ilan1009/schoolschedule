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
    driver = webdriver.Chrome(chrome_options=options)
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

    if changes_txt.text == 'אין שינויים':  # If empty just print that
        return "No schedule changes"

    # Some kind of hard to read text formatting; not the most optimal way.
    else:
        # Open the file, clear it and write new text
        tmpfile = open('tmpfile.txt', 'w', encoding="utf-8")
        tmpfile.truncate(0)
        tmpfile.write(changes_txt.text)
        tmpfile.close()

        # Open the files again and truncate
        tmpfile = open('tmpfile.txt', 'r', encoding="utf-8")
        tmpfileout = open('tmpfileout.txt', 'w', encoding="utf-8")
        tmpfileout.truncate()
        while 1:
            # Get next line from file
            line = tmpfile.readline()

            # if line is empty
            # end of file is reached
            '25.10.2022, שיעור 1, פירשטמן מני, ביטול שעור'
            if not line:
                break
            if 'ביטול שעור' in line:
                # print("Line{}: {}".format(count, line.strip()))
                for i in range(8):
                    if ('שיעור ' + str(i)) in line:
                        tmpfileout.write(f'Period {str(i)} cancelled! W\n')
            elif 'הזזת שיעור' in line:
                for i in range(8):
                    if ('לשיעור ' + str(i)) in line:
                        lesson = line.split(' לשיעור')[0].split(', ')[2]
                        tmpfileout.write(f'Class "{lesson}" moved to period {str(i)}')

            else:
                tmpfileout.write(line)

        # Save files
        tmpfileout.close()
        tmpfile.close()

        # Read file and return it
        tmpfileout = open('tmpfileout.txt', 'r+', encoding="utf-8")
        out = tmpfileout.read()
        print(out)

        tmpfileout.close()

        return out


# Some options
intents = discord.Intents.all()

bot = commands.Bot(command_prefix='$', intents=intents)


async def send_stuff():
    """Function to schedule the sending of the schedule changes of the selected classes when
    called at 7:00 every school day by a Cron"""

    print('Sending daily morning message')

    channel = bot.get_channel(1033324125843894283)  # set channel
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

    # Job that runs send_stuff every day at 7:00
    scheduler.add_job(send_stuff, CronTrigger(day_of_week="0, 1, 2, 3, 4, 6", hour="7", minute="0", second="0"))
    scheduler.start()  # Start


@bot.command(name='send')
async def send(message, arg1=0):
    """A command, Listens for $send, where $ is the prefix. when run with the correct arguments it will return the
    schedule changes of the selected class using the get_stuff() function."""

    print('Command send requested')

    if arg1 == 0:
        await message.channel.send('Failure to provide arguments')
    else:
        await message.channel.send('ט' + str(arg1) + ':')
        loading_msg = await message.channel.send('Loading...')
        await loading_msg.edit(content='\n```\n' + (str(get_stuff(f'ט - {arg1}'))) + '\n```')
        print('Task completed successfully')


toggle = False
bot.run('69')
