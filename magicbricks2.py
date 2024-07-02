import concurrent.futures
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import pickle
import logging
import requests
import traceback


def adjust_column_width(file_path):
    wb = load_workbook(file_path)
    ws = wb.active
    for column in ws.columns:
        max_length = 0
        column = list(column)
        for cell in column:
            if cell.value:
                max_length = max(max_length, len(str(cell.value)))
        adjusted_width = min(max_length + 2, 50)
        column_letter = get_column_letter(column[0].column)
        ws.column_dimensions[column_letter].width = adjusted_width
    wb.save(file_path)


def save_progress(df):
    df.to_excel("magicbricks.xlsx", index=False)
    adjust_column_width("magicbricks.xlsx")


options = Options()
# options.add_argument("--headless")
options.add_argument("--no-sandbox")

url = "https://www.magicbricks.com/residential-real-estate-agents-in-mumbai-pppagent"
driver = webdriver.Chrome(
    service=Service(executable_path="./chromedriver"), options=options
)
driver.get(url)
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

df = pd.DataFrame(
    columns=[
        "About Company",
        "Deals in",
        "Company Name",
        "RERA ID",
        "Name",
        "Operating since",
        "Properties For Sale",
        "Properties For Rent",
        "Address",
    ]
)

seeProDetail
stopPage = true
visited_urls = set()
counter = 0
while True:
    try:
        # elements_to_click = driver.find_elements(By.CLASS_NAME, "srpBlock")
        urls_of_each_page = driver.find_elements(
            By.XPATH, "//span[contains(@class,'seeProDetail')]/a[1]"
        )
        print(len(elements_to_click))
        for element in elements_to_click:
            details = {}
            element.click()
            WebDriverWait(driver, 30).until(EC.number_of_windows_to_be(2))
            driver.switch_to.window(driver.window_handles[-1])
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            ##FUCK THESE LINES BELOW
            # try:
            #     more_data_buttons = driver.find_elements(By.CLASS_NAME, "moreData")
            # except NoSuchElementException:
            #     print("Error while extracting the more buttons")
            # if "showFullAboutVeriAgent();" in more_data_buttons[0].get_attribute(
            #     "onclick"
            # ):
            #     more_data_buttons[0].click()
            #####TILL HERE
            try:
                details["About Company"] = driver.find_element(
                    By.XPATH, '//span[contains(@id,"shortDescVre")]'
                ).text
                details["About Company"] += driver.find_element(
                    By.XPATH, '//span[contains(@id,"fullDescvery")]'
                ).text
            except NoSuchElementException:
                print("The more button did not exist")
            try:
                details["About Company"] = driver.find_element(
                    By.XPATH, "//span[contains(@id,'fullDesc')]"
                ).text
            except NoSuchElementException:
                pass
            try:
                about_the_agent = driver.find_element(
                    By.XPATH, "//div[contains(text(),'About the Agent')]//span[1]"
                )
                if not about_the_agent.get_attribute("id"):
                    details["About Company"] = about_the_agent.text
            except NoSuchElementException:
                pass
            try:
                details["Deals in"] = driver.find_element(
                    By.XPATH,
                    '//div[contains(text(),"Dealing In")]/following-sibling::div[1]',
                ).text
            except NoSuchElementException:
                print("some issue with extracting deals in")
            try:
                details["Company Name"] = driver.find_element(
                    By.CLASS_NAME, "agentName"
                ).text
            except NoSuchElementException:
                details["Company Name"] = "N/A"
            try:
                details["RERA ID"] = driver.current_url.split("-")[-1]
            except IndexError:
                details["RERA ID"] = "N/A"
            try:
                details["Name"] = driver.find_element(By.CLASS_NAME, "agntName").text
            except NoSuchElementException:
                details["Name"] = "N/A"
            try:
                details["Operating since"] = driver.find_element(
                    By.XPATH,
                    '//div[contains(text(),"Operating Since")]/following-sibling::div[1]',
                ).text
            except NoSuchElementException:
                details["Operating since"] = "N/A"
            try:
                details["Properties For Sale"] = driver.find_element(
                    By.XPATH,
                    "//div[contains(text(),'Properties for Sale')]/following-sibling::div[1]",
                ).text
            except NoSuchElementException:
                details["Properties For Sale"] = "N/A"
            try:
                details["Properties For rent"] = driver.find_element(
                    By.XPATH,
                    "//div[contains(text(),'Properties for Rent')]/following-sibling::div[1]",
                ).text
            except NoSuchElementException:
                details["Properties For rent"] = "N/A"
            # details["Address"] = driver.find_element(By.CLASS_NAME, "mapAddress").text
            df.loc[counter] = details
            counter += 1
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            save_progress(df)
    except Exception as e:
        print(e)
        traceback.print_exc()
