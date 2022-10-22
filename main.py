# main.py
import discord
from discord.ext import commands
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec


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
    drpClass.select_by_index(homeRoomIndex)

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

        if changesTXT == 'אין שינויים':  # if this do this
            txtToReturn = 'No schedule changes'
        else:
            txtToReturn = changesTXT.text

        return txtToReturn


intents = discord.Intents.all()

bot = commands.Bot(command_prefix='$', intents=intents)


@bot.command(name='send')
async def send(message, arg1=0):
    arg1index = 16 + arg1
    if arg1 == 0:
        await message.channel.send('Failure to provide arguments')
    else:
        await message.channel.send('ט' + str(arg1))
        loadingMsg = await message.channel.send('Loading...')
        await message.channel.send(getStuff(arg1index, toggle))
        await loadingMsg.delete()


toggle = False
bot.run('MTAzMzE3NDc1NzQyMTYzMzU1Ng.GAPy_9.4u3v7dI7dRoG765ZRYtffPv7Izi3mBiV10CeZw')
