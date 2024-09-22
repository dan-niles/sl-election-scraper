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
