"""A new discord bot by chips"""
import logging

import lib.bot as bot
import lib.crawl as crawl


def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s;%(levelname)s;%(message)s')
    logger = logging.getLogger(__name__)

    logger.info("Creating driver object")
    driver = crawl.driver()

    dev_bot_mode = (int(input('0 for dev mode: ')) == 0)
    if dev_bot_mode:
        tokenFile = "vars/devtoken.txt"
        bot1 = bot.scheduleBot(driver, prefix="__")
    else:
        tokenFile = "vars/token.txt"
        bot1 = bot.scheduleBot(driver)

    with open(tokenFile, 'r') as file:
        bot1.run(file.read())


if __name__ == "__main__":
    main()
