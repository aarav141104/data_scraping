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
df = pd.read_excel(
    "CP data fields to be scraped (1).xlsx", sheet_name="RERA Agent Data"
)
key_names = df.iloc[:, 0].tolist()
df_scraped = pd.DataFrame(columns=key_names)


## This function extracts the links of the view details button from each rera agent
def extract_links(soup):
    global links, df_scraped
    for index, row in enumerate(soup.find("tbody").find_all("tr")):
        cols = row.find_all("td")
        df_scraped.loc[index] = {
            "_id": index,
            "Professional_Rera_certificate_no": cols[2].text.strip(),
        }
        view_details = cols[3].find("a")["href"]
        links.append(view_details)


##This function gets the text of the required field and returns the next element
def find_text(label, soup):
    element = soup.find(string=label)
    if element:
        next_element = element.find_next()
        return next_element.text.strip() if next_element else None


def save_dataframe_to_pdf(df, pdf_filename):
    html_string = df.to_html()
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
    {html_string}
    </body>
    </html>
    """
    with open("temp.html", "w") as f:
        f.write(html_with_style)
    options = {"page-size": "A3", "orientation": "Landscape"}
    pdfkit.from_file("temp.html", pdf_filename, options=options)
    if os.path.exists("temp.html"):
        os.remove("temp.html")


page_num = 1
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
            soup = BeautifulSoup(driver.page_source, "html.parser")
            next_button = soup.find("a", {"class": "next"})
            if next_button and "disabled" in next_button.get("class", []):
                print("No more pages to explore")
                break
            # If the next button exists and is not disabled, click it
            if next_button:
                next_button_href = next_button["href"]
                driver.get(next_button_href)
                # Wait for the next page to load
                WebDriverWait(driver, 20).until(EC.staleness_of(table))
                # Increment page number
                page_num += 1
            else:
                print("No next button found")
                break
        except Exception as e:
            print("error while finding or clicking the next button")
        break
    except:
        print("error during table extraction")
        break


for idx, link in enumerate(links):
    driver.get(link)
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )
    soup = BeautifulSoup(driver.page_source, "html.parser")
    details = {
        "Information_Type": find_text("Information Type", soup),
        "First_Name": find_text("First Name", soup),
        "Middle_Name": find_text("Middle Name", soup),
        "Last_Name": find_text("Last Name", soup),
        "Any_criminal_or_police_case_cases_pending": find_text(
            "Any criminal or police case/ cases pending", soup
        ),
        "Father_Full_Name": find_text("Father Full Name", soup),
        "Do_you_have_any_Past_Experience": find_text(
            " Do you have any Past Experience ? ", soup
        ),
        "House_Number": find_text("House Number", soup),
        "Building_Name": find_text("Building Name", soup),
        "Street_Name": find_text("Street Name", soup),
        "Locality": find_text("Locality", soup),
        "Landmark": find_text("Land mark", soup),
        "State": find_text("State/UT", soup),
        "Division": find_text("Division", soup),
        "District": find_text("District", soup),
        "Taluka": find_text("Taluka", soup),
        "Village": find_text("Village", soup),
        "PinCode": find_text("Pin Code", soup),
        "Office_Number": find_text("Office Number", soup),
        "Website_URL": find_text("Website URL", soup),
        "ProjectName": find_text("Name", soup),
        "Type Of Project": find_text("Organization Type", soup),
        "Agent_Registration_in_Other_State": driver.find_element(
            By.XPATH, '//div//h2[contains(text(),"Agent Registration in Other State")]'
        ),
        "Sr.No.": [],
        "Branch_Name": [],
        "LandLine_Number": [],
        "Branch_Address": [],
        "Email_ID": [],
        "Fax_Number": [],
        "Promoter_Name": [],
        "Project_Name": [],
        "Promoted_Certificate_Number": [],
    }
    ## Below is the past experience table extraction
    try:
        table = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    '//h2[contains(text(),"Past Experience Details")]/following-sibling::div[@id="DataGrid"]//table',
                )
            )
        )
        soup = BeautifulSoup(table.get_attribute("outerHTML"), "html.parser")
        number_of_past_experience = None
        for row in soup.find("tbody").find_all("tr"):
            if row.find_next().name != "tr":
                number_of_past_experience = row.find_all("td")[0].text
        if number_of_past_experience:
            details["Past_Experience_Projects_Count"] = number_of_past_experience
    except (TimeoutException, NoSuchElementException) as e:
        details["Past_Experience_Projects_Count"] = 0

    try:
        table = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    '//h2[contains(text(),"Branch Details")]/../following-sibling::div[1]//div[1]//div[1]//table',
                )
            )
        )
        soup = BeautifulSoup(table.get_attribute("outerHTML"), "html.parser")
        for row in soup.find("tbody").find_all("tr"):
            cols = row.find_all("td")
            details["Sr.No."].append(cols[0].text)
            details["Branch_Name"].append(cols[1].text)
            details["LandLine_Number"].append(cols[2].text)
            details["Branch_Address"].append(cols[3].text)
            details["Email_ID"].append(cols[4].text)
            details["Fax_Number"].append(cols[5].text)
            details["Multiple_Branches"] = "Yes"
    except (TimeoutException, NoSuchElementException) as e:
        details["Sr.No."] = "Not Available"
        details["Branch_Name"] = "Not Available"
        details["Landline_Number"] = "Not Available"
        details["Branch_Address"] = "Not Available"
        details["Email_ID"] = "Not Available"
        details["Fax_Number"] = "Not Available"
        details["Multiple_Branches"] = "No"
    details["Sr.No."] = ",".join(details["Sr.No."])
    details["Branch_Name"] = ",".join(details["Branch_Name"])
    details["LandLine_Number"] = ",".join(details["LandLine_Number"])
    details["Branch_Address"] = ",".join(details["Branch_Address"])
    details["Email_ID"] = ",".join(details["Email_ID"])
    details["Fax_Number"] = ",".join(details["Fax_Number"])
    for key, value in details.items():
        if key in df_scraped.columns:
            df_scraped.at[idx, key] = value
    try:
        table = driver.find_element(
            By.XPATH,
            '//h3[contains(text(),"Promoter Details")]/../../following-sibling::div[1]//div//table',
        )
        soup = BeautifulSoup(table.get_attribute("outerHTML"), "html.parser")
        for row in soup.find("tbody").find_all("tr"):
            cols = row.find_all("td")
            details["Promoter_Name"].append(cols[0].text)
            details["Project_Name"].append(cols[1].text)
            details["Promoted_Certificate_Number"].append(cols[2].text)
    except NoSuchElementException as e:
        details["Promoter_Name"] = "Not Available"
        details["Project_Name"] = "Not Available"
        details["Promoted_Certificate_Number"] = "Not Available"


# print(df_scraped.head(10))
save_dataframe_to_pdf(df_scraped, "output.pdf")

driver.quit()
