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


class MyView(discord.ui.View):
    def __init__(self, day=-1):
        super().__init__(timeout=None)
        self.day = day
        self.timeout = None

    @discord.ui.select(  # the decorator that lets you specify the properties of the select menu
        placeholder="Choose class",  # the placeholder text that will be displayed if nothing is selected
        min_values=1,  # the minimum number of values that must be selected by the users
        max_values=1,  # the maximum number of values that can be selected by the users
        custom_id="class",
        options=[
            discord.SelectOption(
                label="ט - 1",
                description="כיתת הNPCS "
            ),
            discord.SelectOption(
                label="ט - 2",
                description="הבית של מקזסטי רובל"
            ),
            discord.SelectOption(
                label="ט - 3",
                description="תולדות אפור התחילו פה"
            ),
            discord.SelectOption(
                label="ט - 4",
                description="בהחלט אחד מהכיתות בכל הזמנים"
            ),
            discord.SelectOption(
                label="ט - 5",
                description="כיתה ט-5"
            ),
            discord.SelectOption(
                label="ט - 6",
                description="class"
            ),
            discord.SelectOption(
                label="ט - 7",
                description="choose a class"
            ),
        ]
    )
    async def select_callback(self, interaction, select):  # the function called when the user is done selecting options
        g = await get_table_schedule(select.values[0], driver, self.day)
        schedule = g[0]
        title = g[1]
        embedtosend = await makeEmbed(schedule, title)
        await interaction.response.edit_message(embed=embedtosend, view=MyView(self.day))


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
    if day == 7:
        return [["No school on saturdays"]], "Saturday"

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

    daytitle = rows[0].find_elements(By.CSS_SELECTOR, ".CTitle")[day - 1].text
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
                    hourLessons.append('```' + hourLesson.text + '```')

            hourLessonElements = hour.find_elements(By.CSS_SELECTOR, 'td.TableFillChange')
            if hourLessonElements:
                for hourLesson in hourLessonElements:
                    hourLessons.append('```fix\n' + hourLesson.text + '```')

            hourLessonElements = hour.find_elements(By.CSS_SELECTOR, 'td.TableFreeChange')
            if hourLessonElements:
                for hourLesson in hourLessonElements:
                    hourLessons.append('```diff\n- ' + hourLesson.text + '```')

            hourLessonElements = hour.find_elements(By.CSS_SELECTOR, 'td.TableExamChange')
            if hourLessonElements:
                for hourLesson in hourLessonElements:
                    hourLessons.append('```md\n# ' + hourLesson.text + '```')

            hourLessonsElements = hour.find_elements(By.CSS_SELECTOR, '.TTLesson')
            if hourLessonsElements:
                for hourLesson in hourLessonsElements:
                    hourLessons.append('```' + hourLesson.text + '```')

            if hourLessons:
                hourSchedules.append(hourLessons)

        except Exception as e:
            continue

    """
    out = []
    for i, j in enumerate(hourSchedules):
        jjoined = '\n'.join(j)
        out.append(f'({i + 1}) | {jjoined}')
    return f"{home_room}, {daytitle}\n\n" + ("\n\n".join(out))
    """
    daytitle = f"{home_room}, {daytitle}"
    return hourSchedules, daytitle


async def changeTitle(lesson, hourstitles, i):
    if 'diff' in lesson:
        title = hourstitles[i] + ' - ❌❌❌ - Cancelled'
    elif 'fix' in lesson:
        title = hourstitles[i] + ' - ♻♻♻ - Filled in'
    elif 'md' in lesson:
        title = hourstitles[i] + ' - 📝📝💯 - Exam'
    else:
        title = hourstitles[i]
    return title


async def makeEmbed(hourSchedules, title):
    hourstitles = ["8:15 - 9:00", "9:00 - 9:45", "10:10, 10:55", "10:55 - 11:40", "12:00 -  12:45", "12:45 - 13:30",
                   "13:50 - 14:30", "14:30 - 15:15"]
    embed = discord.Embed(title=title, description="", color=discord.Colour.green())
    for i, hourall in enumerate(hourSchedules):  # For every "Hour" in schedule
        for j, hourspecific in enumerate(hourall):
            if j == 0:  # The first item shouldn't be inline so we can have new lines for each segment of the schedule.
                embed.add_field(name=await changeTitle(hourspecific, hourstitles, i), value=hourspecific, inline=False)  # First item has a title
            else:
                embed.add_field(name=chr(160), value=hourspecific, inline=True)  # Others dont have a title.
    embed.set_footer(text="bot made by ilan")
    return embed


# Some options
intents = discord.Intents.all()

bot = commands.Bot(command_prefix='__', intents=intents)


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
        await channel.send(str(classes[i]) + '\n.')


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
async def send(message, arg2=-1):
    """A command, Listens for $send, where $ is the prefix. when run with the correct arguments it
     will return the schedule of the selected class and day """

    print('Command send requested')

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
        await message.channel.send('Tip: specify the day with `$send 2` for example, monday.')
        arg2_v = "today"

    await message.channel.send("Select a class to view its schedule", view=MyView(day=arg2))
    print('Task completed successfully')


@bot.command(name='setchannel')
async def setchannel(ctx):
    """Sets the morning message to send to this channel."""
    with open('vars/morningid.txt', 'a+') as channelfile:
        channelfile.truncate(0)
        channelfile.write(str(ctx.channel.id))
        print(ctx.channel.name)


with open('vars/devtoken.txt', 'r') as file:
    bot.run(file.read())

# print(get_table_schedule('ט - 1', driver))
