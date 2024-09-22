from selenium import webdriver
from selenium.webdriver.common.by import By
import json


class ElectionResult:
    def __init__(self, party, candidate, votes, percentage):
        self.party = party
        self.candidate = candidate
        self.votes = votes
        self.percentage = percentage

    def __str__(self):
        return f"{self.party} - {self.candidate} - {self.votes} - {self.percentage}"


class Division:
    def __init__(self, name, url, status):
        self.name = name
        self.url = url
        self.status = status

    def to_dict(self):
        return {"name": self.name, "url": self.url, "status": self.status}


driver = webdriver.Chrome()
driver.get("https://www.results.elections.gov.lk/index.php")


# Retrieve all island cummulative results
def get_all_island_results():
    button = driver.find_element(By.ID, "toggle-collapse")
    button.click()

    h4_element = driver.find_element(
        By.XPATH, "//h4[contains(text(), 'All Island Result - Cumulative')]"
    )
    target_div = h4_element.find_element(By.XPATH, "../../following-sibling::div")
    child_elements = target_div.find_elements(By.XPATH, "./*")

    results = []
    for child in child_elements:
        try:
            result = child.text.split("\n")
            result = ElectionResult(result[0], result[1], result[2], result[3])
            results.append(result)
        except Exception as e:
            continue
            print(e)

    # write to json
    with open("./data/all-island-results.json", "w") as f:
        json.dump([result.__dict__ for result in results], f, indent=4)


def get_districts():
    target_ul = driver.find_element(By.XPATH, '//*[@id="sidebar"]/ul')
    li_elements = target_ul.find_elements(By.XPATH, "./li[position() > 2]")
    districts = dict()
    for i, li in enumerate(li_elements):
        district_name = li.text
        if district_name not in districts:
            districts[li.text] = []

    for i, district_name in enumerate(districts.keys()):
        driver.implicitly_wait(5)
        district_id = f"district{i+1:02}"

        driver.get(
            f"https://www.results.elections.gov.lk/district_results.php?district={district_name}"
        )
        h4_element = driver.find_element(
            By.XPATH, "//h4[contains(text(), 'Polling Divisions')]"
        )
        target_div = h4_element.find_element(By.XPATH, "../../following-sibling::div")
        child_elements = target_div.find_elements(By.XPATH, "./*")

        for child in child_elements:
            division_name = child.find_element(By.TAG_NAME, "p").text
            division_link = child.get_attribute("href")
            if division_link:
                status = "RELEASED"
            else:
                status = "PENDING"
            division = Division(division_name, division_link, status)
            districts[district_name].append(division.to_dict())

    # write to json
    with open("./data/districts.json", "w") as f:
        json.dump(districts, f, indent=4)


driver.quit()
