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
import datetime

URL = "https://www.alliancetlv.com/עדכוני-מערכת"  # URL

# Chrome options
options = Options()
options.add_argument("--headless")

# Launch web driver
driver = webdriver.Chrome(options=options)
driver.get(URL)

# Enter IFRAME element
frame = WebDriverWait(driver, 10).until(ec.visibility_of_element_located((By.CSS_SELECTOR, 'div#comp-kg9mlfwo iframe')))

driver.switch_to.frame(frame)


async def todayIs():
    # Get current date
    today = datetime.date.today()

    # Get ISO calendar tuple (year, week number, day number)
    iso = today.isocalendar()

    # Get day of the week (Monday is 0, Sunday is 6)
    day = iso[2] - 1

    # Adjust for Sunday as the first day of the week
    day = (day + 1) % 7

    return day


async def get_table_schedule(home_room, driver, day):
    """Gets the schedule changes for specific class and return using SELENIUM WEB DRIVER"""
    if day < 0:
        day = await todayIs() + 1

    # Select class from dropdown
    drp_class = WebDriverWait(driver, 10).until(
        ec.visibility_of_element_located((By.CSS_SELECTOR, '#TimeTableView1_ClassesList')))
    drp_class = Select(drp_class)
    drp_class.select_by_visible_text(str(home_room))

    # Select schedule TABLE and click it with JS
    changes_button = WebDriverWait(driver, 10).until(
        ec.visibility_of_element_located((By.CSS_SELECTOR, '#TimeTableView1_btnChangesTable')))
    changes_button.click()

    rowsHolder = WebDriverWait(driver, 10).until(
        ec.visibility_of_element_located((By.CSS_SELECTOR, '.TTTable > tbody:nth-child(1)')))

    rows = rowsHolder.find_elements(By.XPATH, '*')
    rows.pop(0)

    hours = []
    for row in rows:
        # print(row.get_attribute("outerHTML"))
        cells = row.find_elements(By.CSS_SELECTOR, '.TTCell')
        hours.append(cells[day - 1])
        # print(cells[day-1].get_attribute("outerHTML"))

    hourSchedules = []
    for hour in hours:
        hourLessons = []
        try:
            hourLessonElements = hour.find_elements(By.CSS_SELECTOR, 'td.TableEventChange')
            if hourLessonElements:
                for hourLesson in hourLessonElements:
                    hourLessons.append(hourLesson.text)

            hourLessonsElements = hour.find_elements(By.CSS_SELECTOR, '.TTLesson')
            if hourLessonsElements:
                for hourLesson in hourLessonsElements:
                    hourLessons.append(hourLesson.text)

            if hourLessons:
                hourSchedules.append(hourLessons)

        except Exception as e:
            continue

    out = []
    for i, j in enumerate(hourSchedules):
        jjoined = '\n'.join(j)
        out.append(f'({i + 1}) | {jjoined}')
    return "\n------------------------------------------\n".join(out)


# Some options
intents = discord.Intents.all()

bot = commands.Bot(command_prefix='$', intents=intents)


@bot.command(name='sendBigMessage')
async def send_stuff(message):
    """Function to schedule the sending of the schedule changes of the selected classes when
    called at 7:00 every school day by a Cron"""

    print('Sending big message')

    await bot.wait_until_ready()  # Make sure your guild cache is ready

    classes = []
    for i in range(0, 7):
        c_i = await get_table_schedule('ט - ' + str(i + 1), driver, -1)
        classes.append(c_i)

    for i in range(0, len(classes)):
        await channel.send(
            "###########   **" + f"כיתה ט-{i}" + '**   ###########\n------------------------------------------\n' +
            classes[i] + '\n------------------------------------------\n..ilan -//h...')


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
            if not channel:
                pass
            print(channel.name)

    # await send_stuff()
    # Job that runs send_stuff every day at 7:00
    scheduler.add_job(send_stuff, 'cron', day_of_week="0, 1, 2, 3, 4, 6", hour="7", minute="5", second="0")
    scheduler.start()  # Start


@bot.command(name='send')
async def send(message, arg1, arg2=-1):
    """A command, Listens for $send, where $ is the prefix. when run with the correct arguments it
     will return the schedule of the selected class and day """

    print('Command send requested')

    if not arg1:
        await message.channel.send('Failure to provide arguments')

    try:
        arg1 = int(arg1)
        if arg1 < 1 or arg1 > 7:
            raise ValueError
    except ValueError:
        await message.channel.send(
            'Invalid argument. Please provide an integer between 1 and 7 corresponding to classroom number\n'
            'for example, 4 => ט-4.')
        return
    if arg2 != -1:
        arg2_v = f"day {arg2}"
        try:
            arg2 = int(arg2)
            if arg2 < 1 or arg2 > 5:
                raise ValueError
        except ValueError:
            await message.channel.send(
                'Invalid argument. Please provide an integer between 1 and 5 corresponding to the days sunday to thursday')
            return
    else:
        await message.channel.send('Day not specified, sending todays schedule.')
        arg2_v = "today"

    await message.channel.send(f"Class {arg1}, {arg2_v}")
    loading_msg = await message.channel.send('Loading...')
    g = await get_table_schedule(f'ט - {arg1}', driver, arg2)
    await loading_msg.edit(content=(str(g) + '\n------------------------------------------\n..ilan -//h...'))
    print('Task completed successfully')


@bot.command(name='setchannel')
async def setchannel(ctx):
    """Sets the morning message to send to this channel."""
    with open('vars/morningid.txt', 'a+') as channelfile:
        channelfile.truncate(0)
        channelfile.write(str(ctx.channel.id))
        print(ctx.channel.name)


bot.run('token')

# print(get_table_schedule('ט - 1', driver))
