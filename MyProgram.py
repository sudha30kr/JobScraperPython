from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import csv
from time import sleep

APIKEY = 'YOUR_API_KEY'
indeed_url = "https://www.indeed.com/jobs?q=software+developer&l=Las+Vegas"

proxy_url = f"http://scraperapi.render=true.country_code=us:{APIKEY}@proxy-server.scraperapi.com:8001"
options = Options()
options.add_argument("--disable-blink-features=AutomationControlled")


options.add_argument(f'--proxy-server={proxy_url}')
service=Service(ChromeDriverManager().install())
driver=webdriver.Chrome(service=service, options=options)
print(f"Fetching URL: {indeed_url}")
driver.get(indeed_url)

print("Waiting for page to load...")
sleep(20)

try:
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.ID, "mosaic-jobResults"))
    )
except:
    print("Could not locate job results")
    driver.quit()
    exit()

soup = BeautifulSoup(driver.page_source, 'html.parser')
driver.quit()

job_results = soup.find("div", attrs={"id": "mosaic-jobResults"})
job_elements = job_results.find_all("li", class_="css-1ac2h1w eu4oa1w0") if job_results else []

jobs_data = []
for job_element in job_elements:
    job_title_tag = job_element.find("a", class_="jcs-JobTitle css-1baag51 eu4oa1w0")
    job_title = job_title_tag.find("span").text if job_title_tag else "N/A"

    company_element = job_element.find("span", class_="css-1h7lukg eu4oa1w0")
    company_name = company_element.text.strip() if company_element else "N/A"

    location_element = job_element.find("div", class_="css-1restlb eu4oa1w0")
    job_location = location_element.text.strip() if location_element else "N/A"

    job_type_element = job_element.find("h2", class_="css-1rqpxry e1tiznh50")
    job_type = job_type_element.text.strip() if job_type_element else "N/A"

    salary_element = job_element.find("div", class_="css-18z4q2i eu4oa1w0")
    salary = salary_element.text.strip() if salary_element else "N/A"

    job_link = f"https://www.indeed.com{job_title_tag['href']}" if job_title_tag and job_title_tag.has_attr(
        "href") else "N/A"

    jobs_data.append([job_title, company_name, job_location, salary, job_type, job_link])

if jobs_data:
    with open("indeed_jobs.csv", "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["Title", "Company", "Location", "Salary", "Job Type", "Job Link"])
        writer.writerows(jobs_data)
    print("Saved job posting(s) to 'indeed_jobs.csv'")

print("Scraping session complete.")
