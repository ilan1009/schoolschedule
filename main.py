# main.py
import asyncio
import time

import discord
from CoroCron.Cron import Cron
from discord.ext import commands
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait


def getStuff(homeRoomIndex, examsOption=False):
    url = "https://www.alliancetlv.com/עדכוני-מערכת"  # url

    homeRoomIndex, examsOption = homeRoomIndex, examsOption

    options = Options()
    # options.add_argument("--headless")

    # Launch web driver
    driver = webdriver.Chrome(chrome_options=options)
    driver.get(url)

    wait = WebDriverWait(driver, 10)
    wait.until(ec.visibility_of_element_located((By.XPATH,
                                                 "/html/body/div[1]/div/div[3]/div/main/div/div/div/div["
                                                 "2]/div/div/div/section/div[2]/div/div["
                                                 "2]/div/div/wix-iframe/div/iframe")))

    # Enter iframe containing elements
    frame = driver.find_element(By.XPATH,
                                "/html/body/div[1]/div/div[3]/div/main/div/div/div/div[2]/div/div/div/section/div["
                                "2]/div/div[2]/div/div/wix-iframe/div/iframe")
    driver.switch_to.frame(frame)

    # Select class from dropdown
    drpClass = Select(driver.find_element(By.XPATH, "/html/body/form/div[3]/table/tbody/tr/td[1]/select"))
    drpClass.select_by_value(str(homeRoomIndex))
    time.sleep(5)

    # Select what to output, exams or schedule changes in regard to exams variable; app controller later
    if examsOption:
        examButton = driver.find_element(By.XPATH,
                                         "/html/body/form/div[3]/table/tbody/tr/td[9]/a")  # Select exams tab
        examButton.click()

        examTXT = driver.find_element(By.XPATH,
                                      "/html/body/form/div[3]/div[1]/div/table")  # Find text element

        txtToReturn = examTXT.text

        return txtToReturn

    else:
        changesButton = driver.find_element(By.XPATH,
                                            "/html/body/form/div[3]/table/tbody/tr/td[7]/a")  # Select schedule tab
        changesButton.click()

        changesTXT = driver.find_element(By.XPATH,
                                         "/html/body/form/div[3]/div[1]/div")  # Get the text element

        print(changesTXT.text)
        if changesTXT.text == 'אין שינויים':  # if this do this
            txtToReturn = 'No schedule changes'
        else:
            txtToReturn = changesTXT.text

        return txtToReturn


intents = discord.Intents.all()

bot = commands.Bot(command_prefix='$', intents=intents)


async def sendStuff():
    channel = bot.get_channel(953638497120579664)  # set channel
    await bot.wait_until_ready()  # Make sure your guild cache is ready so the channel can be found via get_channel
    t1 = getStuff(17)
    t2 = getStuff(18)
    t3 = getStuff(19)

    await channel.send('ט1:')
    await channel.send('```\n' + str(t1) + '\n```')
    await channel.send('ט2:')
    await channel.send('```\n' + str(t2) + '\n```')
    await channel.send('ט3:')
    await channel.send('```\n' + str(t3) + '\n```')


@bot.event
async def on_ready():
    print('We\'re in!')
    Cron1 = Cron()
    Cron1.Job().Hours(7).Minutes(30).Do(sendStuff)
    await Cron1.Start(blocking=False)
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(Cron1.Start())
    loop.run_forever()


@bot.command(name='send')
async def send(message, arg1=0):
    arg1index = 16 + arg1
    print(arg1index)
    if arg1 == 0:
        await message.channel.send('Failure to provide arguments')
    else:
        await message.channel.send('ט' + str(arg1) + ':')
        loadingMsg = await message.channel.send('Loading...')
        await loadingMsg.edit(content='\n```\n' + (str(getStuff(arg1index, toggle))) + '\n```')


toggle = False
bot.run('token')
