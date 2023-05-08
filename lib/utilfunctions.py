from datetime import date

from discord import Embed, Colour


def todayIs():
    # Get current date
    today = date.today()

    # Get ISO calendar tuple (year, week number, day number)
    iso = today.isocalendar()

    # Get day of the week (Monday is 0, Sunday is 6)
    day = iso[2] - 1

    # Adjust for Sunday as the first day of the week
    day = (day + 1) % 7

    return day


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


async def makeEmbed(hourSchedules, title, footer_last_updated):
    hourstitles = ["8:15 - 9:00", "9:00 - 9:45", "10:10, 10:55", "10:55 - 11:40", "12:00 -  12:45", "12:45 - 13:30",
                   "13:50 - 14:30", "14:30 - 15:15"]

    embed = Embed(title=title, description="", color=Colour.green())  # Init embed

    for i, hourall in enumerate(hourSchedules):  # For every "Hour" in schedule
        # hourall = hourall[::2]  # Can't have more than 3 lessons on a discord embed in one line.
        j = 0
        for hourspecific in hourall:  # Could've used enumerate but this solution allowed me to use the value "j" outside of the loop.
            embed.add_field(name=await changeTitle(hourspecific, hourstitles, i, j), value=hourspecific,
                            inline=True)  # First item has a title
            j += 1

        for k in range(3 - j):  # Pad the line with some empty fields to make sure lines are formatted correctly.
            embed.add_field(name=chr(160), value=chr(160), inline=True)

    embed.set_footer(text=footer_last_updated + '\ndeveloped by Ilan')  # Credits, for sure
    return embed
