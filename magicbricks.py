from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import pdfkit
import os

service = Service(executable_path="./chromedriver")
driver = webdriver.Chrome(service=service)
url = "https://www.magicbricks.com/residential-real-estate-agents-in-mumbai-pppagent"
xpath = "//span[contains(@class,'seeProDetail')]//a"
df = pd.read_excel("CP data fields to be scraped (1).xlsx", sheet_name="Portals Data")
magicbricks_fields = df.iloc[:, 0].dropna().tolist()  # Fields for Magicbricks
df_magic = pd.DataFrame(columns=magicbricks_fields)
magic_dict = {field: None for field in magicbricks_fields}
driver.get(url)
see_details = WebDriverWait(driver, 6).until(
    EC.presence_of_all_elements_located((By.XPATH, xpath))
)


for idx, see_detail in enumerate(see_details):
    detail_url = see_detail.get_attribute("href")
    driver.get(detail_url)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    try:
        magic_dict["Name"] = driver.find_element(
            By.XPATH,
            '//div[@class="fedImg"]/following-sibling::span[@class="agntName"]',
        ).text
    except:
        magic_dict["Name"] = "N/A"

    try:
        magic_dict["Company Name"] = driver.find_element(
            By.XPATH, '//div[@class="agentNameLoc"]//div[@class="agentName"]'
        ).text
    except:
        magic_dict["Company Name"] = "N/A"

    magic_dict["RERA ID"] = detail_url.split("-")[-1]

    try:
        magic_dict["Operating since"] = driver.find_element(
            By.XPATH,
            '//div[contains(text(),"Operating Since")]/following-sibling::div[1]',
        ).text
    except:
        magic_dict["Operating since"] = "N/A"

    try:
        first = driver.find_element(
            By.XPATH,
            '//div[contains(text(),"Properties for Sale") and contains(@class,"column_1")]/following-sibling::div[1]',
        )
        properties_for_sale = first.text + " ("
        for span in first.find_elements(By.TAG_NAME, "span"):
            properties_for_sale += span.text
        properties_for_sale += ")"
        magic_dict["Properties For Sale"] = properties_for_sale
    except:
        magic_dict["Properties For Sale"] = "N/A"

    try:
        first = driver.find_element(
            By.XPATH,
            '//div[contains(text(),"Properties for Rent") and contains(@class,"column_1")]/following-sibling::div[1]',
        )
        properties_for_rent = first.text + " ("
        for span in first.find_elements(By.TAG_NAME, "span"):
            properties_for_rent += span.text
        properties_for_rent += ")"
        magic_dict["Properties For rent"] = properties_for_rent
    except:
        magic_dict["Properties For rent"] = "N/A"

    try:
        first = driver.find_element(
            By.XPATH,
            '//div[contains(text(),"Address") and contains(@class,"column_1")]/following-sibling::div[1]',
        )
        second = first.find_element(
            By.XPATH, "./following-sibling::br[1]/following-sibling::text()"
        )
        magic_dict["Address"] = first.text + "\n" + second
    except:
        magic_dict["Address"] = "N/A"

    try:
        magic_dict["Deals in"] = driver.find_element(
            By.XPATH,
            '//div[contains(text(),"Dealing In") and contains(@class,"column_1")]/following-sibling::div[1]',
        ).text
    except:
        magic_dict["Deals in"] = "N/A"

    try:
        more_button = driver.find_element(
            By.XPATH,
            '//div[contains(text(),"Operating In") and contains(@class,"column_1")]/following-sibling::div[1]//span[1]//a[contains(text(),"+ more")]',
        )
        more_button.click()
        operates_in = driver.find_element(
            By.XPATH,
            '//div[contains(text(),"Operating In") and contains(@class,"column_1")]/following-sibling::div[1]//span[2]',
        )
        operates_in_data = ""
        for item in operates_in.find_elements(By.XPATH, ".//a"):
            if item.find_element(By.XPATH, "./following-sibling::*[1]").tag_name != "a":
                break
            operates_in_data += item.text + ","
        magic_dict["Operates in"] = operates_in_data
    except:
        magic_dict["Operates in"] = "N/A"

    try:
        more_button = driver.find_element(
            By.XPATH,
            '//div[contains(text(),"About the Agent")]/following-sibling::div[1]//a[1]',
        )
        more_button.click()
        first = driver.find_element(
            By.XPATH,
            '//div[contains(text(),"About the Agent")]/following-sibling::div[1]//span[1]',
        ).text
        second = driver.find_element(
            By.XPATH,
            '//div[contains(text(),"About the Agent")]/following-sibling::div[1]//span[2]',
        ).text
        magic_dict["About Company"] = first + second
    except:
        magic_dict["About Company"] = "N/A"

    for key, value in magic_dict.items():
        if key in df_magic.columns:
            df_magic.at[idx, key] = value
    break


def save_file_to_pdf(df, pdf_filename):
    html_content = df.to_html()
    html_with_style = f"""
    <html>
    <head>
    <style>
    table {{ 
        width: 100%; 
        border-collapse: collapse; 
        font-size: 8px; 
    }}
    table, th, td {{ 
        border: 1px solid black; 
        text-align: left; 
        padding: 5px;
    }}
    </style>
    </head>
    <body>
    {html_content}
    </body>
    </html>
    """
    with open("temp.html", "w") as f:
        f.write(html_with_style)
    options = {"page-size": "A3", "orientation": "Landscape"}
    pdfkit.from_file("temp.html", pdf_filename, options=options)
    if os.path.exists("temp.html"):
        os.remove("temp.html")


# Save the DataFrame to PDF
save_file_to_pdf(df_magic, "output.pdf")

driver.quit()
