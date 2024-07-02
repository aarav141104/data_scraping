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

visited_urls = set()
counter = 0
while True:
    try:
        # elements_to_click = driver.find_elements(By.CLASS_NAME, "srpBlock")
        elements = driver.find_elements(
            By.XPATH, "//span[contains(@class,'seeProDetail')]/a[1]"
        )
        urls_of_each_page = [element.get_attribute("href") for element in elements]
        print(len(urls_of_each_page))
        for url in urls_of_each_page:
            details = {}
            local_driver = webdriver.Chrome(
                service=Service(executable_path="./chromedriver"), options=options
            )
            if url not in visited_urls:
                local_driver.get(url)
            else:
                continue
            WebDriverWait(local_driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            ##FUCK THESE LINES BELOW
            # try:
            #     more_data_buttons = local_driver.find_elements(By.CLASS_NAME, "moreData")
            # except NoSuchElementException:
            #     print("Error while extracting the more buttons")
            # if "showFullAboutVeriAgent();" in more_data_buttons[0].get_attribute(
            #     "onclick"
            # ):
            #     more_data_buttons[0].click()
            #####TILL HERE
            first_case = None
            try:
                more_button = local_driver.find_element(
                    By.XPATH,
                    "//div[contains(text(),'About the Agent')]/following-sibling::div[1]/a[1]",
                )
                try:
                    first_case = local_driver.find_element(
                        By.XPATH, '//span[contains(@id,"shortDescVre")]'
                    ).text
                    first_case += local_driver.find_element(
                        By.XPATH, '//span[contains(@id,"fullDescvery")]'
                    ).text
                    details["About Company"] = first_case
                except NoSuchElementException:
                    pass
                if not first_case:
                    try:
                        second_case = local_driver.find_element(
                            By.XPATH, "//span[contains(@id,'fullDesc')]"
                        ).text
                        details["About Company"] = second_case
                    except NoSuchElementException:
                        pass
            except NoSuchElementException as e:
                details["About Company"] = local_driver.find_element(
                    By.XPATH,
                    "//div[contains(text(),'About the Agent')]/following-sibling::div[1]/span[1]",
                ).text

            # first_case = None
            # second_case = None
            # third_case = None
            # try:
            #     first_case = local_driver.find_element(
            #         By.XPATH, '//span[contains(@id,"shortDescVre")]'
            #     ).text
            #     first_case += local_driver.find_element(
            #         By.XPATH, '//span[contains(@id,"fullDescvery")]'
            #     ).text
            # except NoSuchElementException:
            #     print("The more button did not exist")
            # try:
            #     second_case = local_driver.find_element(
            #         By.XPATH, "//span[contains(@id,'fullDesc')]"
            #     ).text
            # except NoSuchElementException:
            #     pass
            # try:
            #     third_case = local_driver.find_element(
            #         By.XPATH, "//div[contains(text(),'About the Agent')]//span[1]"
            #     )
            #     if third_case.get_attribute("id"):
            #         third_case = None
            #     else:
            #         third_case = third_case.text
            # except NoSuchElementException:
            #     pass
            # if first_case:
            #     details["About Company"] = first_case
            # elif second_case:
            #     details["About Company"] = second_case
            # elif third_case:
            #     details["About Company"] = third_case
            try:
                details["Deals in"] = local_driver.find_element(
                    By.XPATH,
                    '//div[contains(text(),"Dealing In")]/following-sibling::div[1]',
                ).text
            except NoSuchElementException:
                print("some issue with extracting deals in")
            try:
                details["Company Name"] = local_driver.find_element(
                    By.CLASS_NAME, "agentName"
                ).text
            except NoSuchElementException:
                details["Company Name"] = "N/A"
            try:
                details["RERA ID"] = local_driver.current_url.split("-")[-1]
            except IndexError:
                details["RERA ID"] = "N/A"
            try:
                details["Name"] = local_driver.find_element(
                    By.CLASS_NAME, "agntName"
                ).text
            except NoSuchElementException:
                details["Name"] = "N/A"
            try:
                details["Operating since"] = local_driver.find_element(
                    By.XPATH,
                    '//div[contains(text(),"Operating Since")]/following-sibling::div[1]',
                ).text
            except NoSuchElementException:
                details["Operating since"] = "N/A"
            try:
                details["Properties For Sale"] = local_driver.find_element(
                    By.XPATH,
                    "//div[contains(text(),'Properties for Sale')]/following-sibling::div[1]",
                ).text
            except NoSuchElementException:
                details["Properties For Sale"] = "N/A"
            try:
                details["Properties For rent"] = local_driver.find_element(
                    By.XPATH,
                    "//div[contains(text(),'Properties for Rent')]/following-sibling::div[1]",
                ).text
            except NoSuchElementException:
                details["Properties For rent"] = "N/A"
            # details["Address"] = local_driver.find_element(
            #     By.XPATH, "//span[contains(@class,'mapAddress')]"
            # ).text
            df.loc[counter] = details
            counter += 1
            local_driver.quit()
            save_progress(df)
    except Exception as e:
        print(e)
        traceback.print_exc()
