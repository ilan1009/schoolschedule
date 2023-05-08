import discord
from discord.ext import commands, tasks
import logging
from utilfunctions import todayIs, makeEmbed

logger = logging.getLogger(__name__)


class MyView(discord.ui.View):
    def __init__(self, driver, homeroom='ט - 1', day=-1):
        super().__init__(timeout=None)
        self.currentclass = homeroom
        if day == -1:
            self.day = todayIs() + 1
            logger.info(f'day {self.day} (+1 for actual day) automatically detected')
        else:
            self.day = day
        self.timeout = None
        self.interaction = None
        self.driver = driver

    @discord.ui.select(  # the decorator that lets you specify the properties of the select menu
        placeholder="Choose class",  # the placeholder text that will be displayed if nothing is selected
        min_values=1,  # the minimum number of values that must be selected by the users
        max_values=1,  # the maximum number of values that can be selected by the users
        custom_id="class-selector",
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

    @discord.ui.button(label="Day Backwards", custom_id="backwards-grey")
    async def back(self, interaction: discord.Interaction, button: discord.Button):
        self.day -= 1
        if self.day == 6:
            self.day = 1
        self.interaction = interaction
        logger.info(f'day {self.day} (+1 for actual day) requested by {self.interaction.user.name}')
        await self.edit()

    @discord.ui.button(label="Day Forwards", custom_id="forwards-grey")
    async def forw(self, interaction: discord.Interaction, button: discord.Button):
        self.day += 1
        if self.day == 0:
            self.day = 5
        self.interaction = interaction
        logger.info(f'day {self.day} (+1 for actual day) requested by {self.interaction.user.name}')
        await self.edit()

    async def edit(self):
        while True:
            try:
                if self.interaction is not None:
                    g = await self.driver.get_table_schedule(self.currentclass, self.day)  # Get the schedule and title
                    schedule, title, footer_last_updated = g[0], g[1], g[2]  # Get the schedule and title
                    embedtosend = await makeEmbed(schedule, title, footer_last_updated)  # Make the embed
                    await self.interaction.response.edit_message(embed=embedtosend,
                                                                 view=MyView(self.driver,
                                                                             day=self.day,
                                                                             homeroom=self.currentclass))  # Edit message correctly.
            except discord.errors.NotFound:
                continue
            break


class scheduleBot(commands.Bot):
    def __init__(self, driver, prefix="$"):
        intents = discord.Intents.all()  # Send messages, # Message content
        self.driver = driver
        super().__init__(command_prefix=commands.when_mentioned_or(prefix), intents=intents)

    async def setup_hook(self) -> None:
        # Register the persistent view for listening here.
        # Note that this does not send the view to any message.
        # In order to do this you need to first send a message with the View, which is shown below.
        # If you have the message_id you can also pass it as a keyword argument, but for this example
        # we don't have one.
        self.add_view(MyView(self.driver))
        await self.add_cog(SendCommands(self, self.driver))

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')


class SendCommands(commands.Cog):
    def __init__(self, botObject, driver):
        self.driver = driver
        self.bot = botObject

    @commands.command(name="send")
    async def send(self, message, arg2=-1):
        """A command, Listens for $send, where $ is the prefix. when run with the correct arguments it
         will return the schedule of the selected class and day """

        print('Command send requested')

        if arg2 != -1:
            arg2_v = f"day {arg2}"
            try:
                arg2 = int(arg2)
                if arg2 < 1 or arg2 > 5 and not 999:
                    raise ValueError
            except ValueError:
                await message.channel.send(
                    'Invalid argument. Please provide an integer between 1 and 5 corresponding to the days sunday to thursday')
                return
        else:
            await message.channel.send('Tip: specify the day with `$send 2` for example, monday.')
            arg2_v = "today"

        await message.channel.send("Select a class to view its schedule", view=MyView(self.driver, day=arg2))
        print('Task completed successfully')
