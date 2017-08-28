import os
import shutil
import sqlite3
import sys
import time
import zipfile

import requests
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait


class Automation:
    def __init__(self):
        if not os.path.isfile("chromedriver.exe"):
            print("chromedriver.exe가 존재하지 않습니다. 최신 릴리즈를 최초 1회 다운로드합니다.", file=sys.stderr)

            chromedriver_latest_release = requests.get(
                "https://chromedriver.storage.googleapis.com/LATEST_RELEASE").text.strip()

            r = requests.get("https://chromedriver.storage.googleapis.com/"
                             + chromedriver_latest_release + "/chromedriver_win32.zip", stream=True)

            with open("chromedriver_win32.zip", "wb") as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)

            with zipfile.ZipFile("chromedriver_win32.zip") as zip:
                zip.extract("chromedriver.exe")

            os.remove("chromedriver_win32.zip")

        self.driver = webdriver.Chrome()

    def __del__(self):
        self.driver.quit()

    def click_css_selector(self, css_selector, wait=10):
        if wait != 0:
            WebDriverWait(self.driver, wait).until(expected_conditions.element_to_be_clickable((By.CSS_SELECTOR, css_selector)))
        self.driver.find_element_by_css_selector(css_selector).click()

    def find_css_selector(self, css_selector, wait=10):
        if wait != 0:
            WebDriverWait(self.driver, wait).until(expected_conditions.element_to_be_clickable((By.CSS_SELECTOR, css_selector)))
        return self.driver.find_element_by_css_selector(css_selector)

    def send_keys_css_selector(self, css_selector, keys):
        WebDriverWait(self.driver, 10).until(expected_conditions.element_to_be_clickable((By.CSS_SELECTOR, css_selector)))
        x = self.driver.find_element_by_css_selector(css_selector)
        x.clear()
        x.click()
        x.send_keys(Keys.TAB)
        x.send_keys(keys)

    def click_xpath(self, xpath, wait=10):
        if wait != 0:
            WebDriverWait(self.driver, wait).until(expected_conditions.element_to_be_clickable((By.XPATH, xpath)))
        self.driver.find_element_by_xpath(xpath).click()

    def find_xpath(self, xpath, wait=10):
        if wait != 0:
            WebDriverWait(self.driver, wait).until(expected_conditions.element_to_be_clickable((By.XPATH, xpath)))
        return self.driver.find_element_by_xpath(xpath)

    def send_keys_xpath(self, xpath, keys):
        WebDriverWait(self.driver, 10).until(expected_conditions.element_to_be_clickable((By.XPATH, xpath)))
        x = self.driver.find_element_by_xpath(xpath)
        x.clear()
        x.click()
        x.send_keys(Keys.TAB)
        x.send_keys(keys)

    def is_alert(self):
        try:
            WebDriverWait(self.driver, 1).until(expected_conditions.alert_is_present(), "")
            alert = self.driver.switch_to.alert
            text = alert.text
            alert.accept()
            return True, text

        except TimeoutException:
            return False, ""

    @staticmethod
    def read_txt(filename, sep=None):
        with open(filename, "r") as f:
            for l in f:
                if sep is not None:
                    yield l.strip().split(sep)
                else:
                    yield l.strip()

    @staticmethod
    def format_time(format_string):  # "%Y-%m-%d %H:%M:%S"
        return time.strftime(format_string)


def main():
    kau_id = input("kau id: ")
    kau_pass = input("kau pass: ")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS lecture "
              "(lecture_no TEXT, lecture_name TEXT, professor TEXT, time TEXT, lecture_room TEXT)")

    a = Automation()
    a.driver.get("http://kau.ac.kr/page/main.jsp")
    time.sleep(1)
    a.driver.get("http://www.kau.ac.kr/page/act_Portal_Check.jsp")
    time.sleep(1)
    a.driver.find_element_by_name("p_id").send_keys(kau_id)
    time.sleep(1)
    a.driver.find_element_by_name("p_pwd").send_keys(kau_pass)
    time.sleep(1)
    a.driver.execute_script("checkForm()")
    time.sleep(1)
    a.driver.execute_script("""
    document.getElementsByName("TF")[0].contentWindow.goPage("https://portal.kau.ac.kr/sugang/LectDeptSchTop.jsp")""")
    for i in range(2, 50):
        time.sleep(1)
        table = a.driver.execute_script("""
        table = document.getElementsByName("RF")[0].contentDocument.querySelectorAll(".table1 tr.tr_0,tr.tr_1")
        var tables = []
        table.forEach(row => {
            var cells = []
            console.log(row.querySelectorAll("td").forEach(cell => {
                cells.push(cell.innerHTML)
            }))
            tables.push(cells)
        })
        return tables
        """)
        print(table)

        for line in table:
            c.execute("INSERT INTO lecture VALUES (?, ?, ?, ?, ?)",
                      (line[1].strip(), line[2].split(">")[1].split("<")[0].strip(), line[6].strip(), " ".join(line[9].split(" <br> ")).strip(), line[10].strip()))
            conn.commit()

        time.sleep(1)
        a.driver.switch_to.frame(a.driver.find_element_by_name("RF"))
        a.driver.execute_script("""goPageTo({})""".format(i))
        a.driver.switch_to.parent_frame()

if __name__ == "__main__":
    main()
