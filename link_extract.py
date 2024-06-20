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

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

links = []


def save_links_to_file(links, filename="links.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(links, f)
    logging.info(f"Links saved to {filename}")


def extract_link(page_num):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service("./chromedriver"), options=options)
    try:
        driver.get(
            f"https://maharera.maharashtra.gov.in/agents-search-result?agent_name=&agent_project_name=&agent_location=&agent_state=27&agent_division=&agent_district=&page={page_num}&op=Search"
        )
        driver.implicitly_wait(10)
        logging.info(f"Extracting links from page {page_num}")
        view_details = driver.find_elements(By.XPATH, "td//a[1]").get_attribute("href")
        print(len(view_details) + "4")
        links.extend(view_details)
        save_links_to_file(links)
        logging.info(f"Extracted {len(links)} links so far")
    except:
        print("Something went wrong in page number : {page_num}")
    finally:
        driver.quit()


# with concurrent.futures.ThreadPoolExecutor(max_workers=25) as executor:
#     executor.map(extract_link, range(1, 4733))
extract_link(1)
