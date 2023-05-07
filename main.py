"""A new discord bot by chips"""
import discord
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from discord.ext import commands, tasks
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
import datetime


class MyView(discord.ui.View):
    @tasks.loop(minutes=3.0)
    async def periodicallyEdit(self):
        await self.edit()
        print("edited")

    def __init__(self, day=-1):
        super().__init__(timeout=None)
        self.currentclass = 'ט - 1'
        self.day = day
        self.timeout = None
        self.periodicallyEdit.start()
        self.interaction = None

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
        self.currentclass = select.values[0]
        self.interaction = interaction

        await self.edit()

    async def edit(self):
        if self.interaction is not None:
            g = await get_table_schedule(self.currentclass, driver, self.day)  # Get the schedule and title
            schedule, title = g[0], g[1]  # Get the schedule and title
            embedtosend = await makeEmbed(schedule, title)  # Make the embed
            await self.interaction.response.edit_message(embed=embedtosend, view=MyView(self.day))  # Edit message correctly.



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
    if day == 7:  # Some guards
        return [["No school on saturdays"]], "Saturday"

    # Select class from dropdown
    drp_class = WebDriverWait(driver, 10).until(
        ec.visibility_of_element_located((By.CSS_SELECTOR, '#TimeTableView1_ClassesList')))  # Dropdown element

    drp_class = Select(drp_class)  # Select using JS
    drp_class.select_by_visible_text(str(home_room))  # Select using JS

    # Select schedule TABLE and click it with JS
    changes_button = WebDriverWait(driver, 10).until(
        ec.visibility_of_element_located((By.CSS_SELECTOR, '#TimeTableView1_btnChangesTable')))
    changes_button.click()

    # Find all rows, because table is organized into rows > cells, which made this slightly harder.
    rowsHolder = WebDriverWait(driver, 10).until(
        ec.visibility_of_element_located((By.CSS_SELECTOR, '.TTTable > tbody:nth-child(1)')))

    # Get all the rows elements/divs
    rows = rowsHolder.find_elements(By.XPATH, '*')

    # Get the daytitle, which is the first row and then get rid of that row.
    daytitle = rows[0].find_elements(By.CSS_SELECTOR, ".CTitle")[day - 1].text  # So we get the corresponding cell for the day
    rows.pop(0)

    hours = []  # Empty list init
    for row in rows:  # Find all cells for the correct day by iterating through rows.
        cells = row.find_elements(By.CSS_SELECTOR, '.TTCell')
        hours.append(cells[day - 1])

    hourSchedules = []  # More shitty stringbuilder, since no stringbuilder in python.
    for hour in hours:
        hourLessons = []
        try:
            # Find all the elements blah blah
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

    daytitle = f"{home_room}, {daytitle}"  # The title, to be used for embed title.
    return hourSchedules, daytitle


async def changeTitle(lesson, hourstitles, i, j):
    # Decided to extract this to its own function, too much nesting.

    prefix = hourstitles[i]
    if j != 0:
        prefix = "↓"
    if 'diff' in lesson:
        title = prefix + ' - ❌❌ - Cancelled'
    elif 'fix' in lesson:
        title = prefix + ' - ♻♻ - Filled in'
    elif 'md' in lesson:
        title = prefix + ' - 📝💯 - Exam'
    else:
        title = prefix
    return title


async def makeEmbed(hourSchedules, title):
    hourstitles = ["8:15 - 9:00", "9:00 - 9:45", "10:10, 10:55", "10:55 - 11:40", "12:00 -  12:45", "12:45 - 13:30",
                   "13:50 - 14:30", "14:30 - 15:15"]

    embed = discord.Embed(title=title, description="", color=discord.Colour.green())  # Init embed

    for i, hourall in enumerate(hourSchedules):  # For every "Hour" in schedule
        hourall = hourall[::2]  # Can't have more than 3 lessons on a discord embed in one line.
        j = 0
        for hourspecific in hourall:  # Could've used enumerate but this solution allowed me to use the value "j" outside of the loop.
            embed.add_field(name=await changeTitle(hourspecific, hourstitles, i, j), value=hourspecific,
                            inline=True)  # First item has a title
            j += 1

        for k in range(3 - j):  # Pad the line with some empty fields to make sure lines are formatted correctly.
            embed.add_field(name=chr(160), value=chr(160), inline=True)

    embed.set_footer(text="bot made by ilan")  # Credits, for sure
    return embed


intents = discord.Intents.all()  # Send messages, # Message content

# Some options
dev_bot_mode = True
if dev_bot_mode:
    tokenFile = "vars/devtoken.txt"
    bot = commands.Bot(command_prefix='__', intents=intents)
else:
    tokenFile = "vars/token.txt"
    bot = commands.Bot(command_prefix='$', intents=intents)


@bot.event
async def on_ready():
    """Runs on ready"""
    print('Connected')


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


with open(tokenFile, 'r') as file:
    bot.run(file.read())

# print(get_table_schedule('ט - 1', driver))
