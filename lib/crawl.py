import logging

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait

from utilfunctions import todayIs

logger = logging.getLogger(__name__)


class driver:
    def __init__(self):
        self.URL = "https://www.alliancetlv.com/עדכוני-מערכת"  # URL

        # Chrome options
        options = Options()
        options.add_argument("--headless")

        # Launch web driver
        self.driver = webdriver.Chrome(options=options)
        self.driver.get(self.URL)

        # Enter IFRAME element
        frame = WebDriverWait(self.driver, 10).until(
            ec.visibility_of_element_located((By.CSS_SELECTOR, 'div#comp-kg9mlfwo iframe')))

        self.driver.switch_to.frame(frame)
        logger.info("Driver ready at " + self.URL)

    async def get_table_schedule(self, home_room, day):
        """Gets the schedule changes for specific class and return using SELENIUM WEB DRIVER"""

        if day < 0:
            day = todayIs() + 1
        if day == 7:  # Some guards
            return [["No school on saturdays"]], "Saturday"

        driver = self.driver

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
        daytitle = rows[0].find_elements(By.CSS_SELECTOR, ".CTitle")[
            day - 1].text  # So we get the corresponding cell for the day
        rows.pop(0)

        hours = []  # Empty list init
        for row in rows:  # Find all cells for the correct day by iterating through rows.
            cells = row.find_elements(By.CSS_SELECTOR, '.TTCell')
            hours.append(cells[day - 1])

        hourSchedules = []  # More shitty stringbuilder, since no stringbuilder in python.
        for hour in hours:
            hourLessons = []
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

        daytitle = f"{home_room}, {daytitle}"  # The title, to be used for embed title.
        footer_last_updated = ','.join(driver.find_element(By.CSS_SELECTOR, "#TimeTableView1_lblUpdateDate").text.split(',')[0:2])
        return hourSchedules, daytitle, footer_last_updated
