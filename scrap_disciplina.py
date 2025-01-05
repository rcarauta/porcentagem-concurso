from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pymongo
import re

driver = webdriver.Chrome()
title_url = 'direito-direito-eleitoral'
disciplina = 'direitoEleitoral'
driver.get("https://www.qconcursos.com/questoes-de-concursos/disciplinas/"+title_url)

client = pymongo.MongoClient("mongodb://root:example@localhost:27017/")
db = client["qconcursos"]  # Database name
collection = db["topics"]  # Collection name

try:
    wait = WebDriverWait(driver, 260)  # Increased wait time
    # Check for the main content
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "q-subject-group-list")))

    # Extract data
    questoes_xpath = "//div[contains(@class, 'q-caption') and text()='Questões']/following-sibling::div[contains(@class, 'q-value')]/a"
    questoes_count_element = driver.find_element(By.XPATH, questoes_xpath)
    questoes_count = questoes_count_element.text
    print(f"Total Questões: {questoes_count}")

    topics_data = []
    topics = driver.find_elements(By.CSS_SELECTOR, ".q-subject-group-item")

    for topic in topics:
        try:
            topic_title_element = topic.find_element(By.CSS_SELECTOR, ".q-title a.q-number")
            topic_title = re.sub(r'^[0-9.]{1,4}', '', topic_title_element.text).strip()
            topic_url = topic_title_element.get_attribute("href")

            topic_questoes_xpath = ".//div[contains(@class, 'q-caption') and text()='Questões']/following-sibling::div[contains(@class, 'q-value')]/a"
            topic_questoes_element = topic.find_element(By.XPATH, topic_questoes_xpath)
            topic_questoes_count = topic_questoes_element.text.strip()

            topic_data = {
                "title": topic_title,
                "questoes_count": topic_questoes_count
            }

            topics_data.append(topic_data)
        except Exception as e:
            print(f"Error scraping topic: {e}")

    print("Scraped Topics Data:")
    document = {disciplina: topics_data}
    collection.insert_one(document)
    #save each line not print
    for topic in topics_data:
        print(topic)

finally:
    driver.quit()
