from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd

# Initialize the WebDriver (e.g., Chrome)
driver = webdriver.Chrome(executable_path="/path/to/chromedriver")

# Navigate to the web page
url = "https://example.com"
driver.get(url)

# Wait for the parent div to be present
parent_div = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "parent-div"))
)

# Now find the table within the parent div
table = parent_div.find_element(By.TAG_NAME, "table")

# Extract the HTML of the table and parse it with BeautifulSoup
html_source = table.get_attribute("outerHTML")
soup = BeautifulSoup(html_source, "html.parser")

# Extract table headers
headers = [header.text.strip() for header in soup.find_all("th")]

# Extract table rows
rows = []
for row in soup.find("tbody").find_all("tr"):
    cols = row.find_all("td")
    cols = [col.text.strip() for col in cols]
    rows.append(cols)

# Create a DataFrame from the extracted data
table_data = pd.DataFrame(rows, columns=headers)

# Save the table data to a CSV file (optional)
table_data.to_csv("extracted_table.csv", index=False)
print("Table data saved to extracted_table.csv")

# Click the buttons under the "View Details" column and scrape data from the resulting page
details_list = []
for index, row in enumerate(
    driver.find_elements(By.XPATH, "//div[@id='parent-div']//table/tbody/tr")
):
    # Adjust the column index (e.g., 1) based on the actual position of the "View Details" column
    view_details_button = row.find_elements(By.TAG_NAME, "td")[1].find_element(
        By.TAG_NAME, "button"
    )

    # Click the "View Details" button
    view_details_button.click()

    # Wait for the new content to load (adjust the condition as necessary)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "details-section"))
    )

    # Extract additional details from the new page or modal
    details_section = driver.find_element(By.ID, "details-section")
    details_html = details_section.get_attribute("outerHTML")
    details_soup = BeautifulSoup(details_html, "html.parser")

    # Extract specific details (example)
    details_data = details_soup.find("div", class_="details-info").text.strip()
    details_list.append(details_data)

    # Optionally, navigate back to the main page or table
    driver.back()

# Save the details data to a CSV file (optional)
details_df = pd.DataFrame(details_list, columns=["Details"])
details_df.to_csv("details_data.csv", index=False)
print("Details data saved to details_data.csv")

# Close the WebDriver
driver.quit()
