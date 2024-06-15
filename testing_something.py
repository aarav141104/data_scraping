from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urljoin, urlparse
from selenium.webdriver.common.keys import Keys
import pandas as pd
import pdfkit
import os
from selenium.common.exceptions import NoSuchElementException, TimeoutException

url = "https://maharera.maharashtra.gov.in/agents-search-result"
service = Service(executable_path="./chromedriver")
driver = webdriver.Chrome(service=service)
driver.get(url)

links = []  ## to store the links


## This function extracts the links of the view details button from each rera agent
def extract_links(soup):
    global links, df_scraped
    for index, row in enumerate(soup.find("tbody").find_all("tr")):
        cols = row.find_all("td")
        view_details = cols[3].find("a")["href"]
        links.append(view_details)

while True:
    try:
        table = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (By.XPATH, '//div[@class="tableBox"]//div[@class="tableOuter"]//table')
            )
        )
        html_content = table.get_attribute("outerHTML")
        soup = BeautifulSoup(html_content, "html.parser")
        extract_links(soup)
        try: