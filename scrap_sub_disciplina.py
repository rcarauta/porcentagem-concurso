from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pymongo
import re 

# Initialize the Selenium WebDriver
driver = webdriver.Chrome()
title_url = 'tecnologia-da-informacao-nocoes-de-informatica'
disciplina = 'nocoesInformatica'
driver.get("https://www.qconcursos.com/questoes-de-concursos/disciplinas/"+title_url)

client = pymongo.MongoClient("mongodb://root:example@localhost:27017/")
db = client["qconcursos"]  # Database name
collection = db["subtopics"]

try:
    wait = WebDriverWait(driver, 260)
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "q-subject-group-list")))

    main_subjects = []
    panels = driver.find_elements(By.CSS_SELECTOR, '.q-subject-group-item')

    for panel in panels:
        main_subject = {}

        try:
            panel_heading = panel.find_element(By.CSS_SELECTOR, '.panel-heading .q-title')
            main_subject['name'] = re.sub(r'^[0-9.]{1,4}', '', panel_heading.text).strip()
        except Exception as e:
            print(f"Error extracting main subject title: {e}")

        nested_subjects = []
        try:
            nested_subject_div = panel.find_element(By.CSS_SELECTOR, '.q-nested-subjects')
            if nested_subject_div.is_displayed():
                nested_items = nested_subject_div.find_elements(By.CSS_SELECTOR, '.list-group-item')
                
                for nested_item in nested_items:
                    nested_subject_data = {}

                    nested_title = nested_item.find_element(By.CSS_SELECTOR, '.q-title a')
                    nested_subject_data['name'] = re.sub(r'^[0-9.]{1,4}', '', nested_title.text).strip()

                    subitems = []
                    items = nested_item.find_elements(By.CSS_SELECTOR, '.q-items .q-item')
                    for item in items:
                        try:
                            caption_tag = item.find_element(By.CSS_SELECTOR, '.q-caption')
                            value_tag = item.find_element(By.CSS_SELECTOR, '.q-value a')
                            subitems.append({
                                'caption': caption_tag.text.strip(),
                                'value': value_tag.text.strip()
                            })
                        except Exception as e:
                            print(f"Error extracting subitem: {e}")

                    nested_subject_data['subitems'] = subitems
                    nested_subjects.append(nested_subject_data)

        except Exception as e:
            print(f"Error extracting nested subjects: {e}")

        if nested_subjects:
            main_subject['nested_subjects'] = nested_subjects

        main_subjects.append(main_subject)

    print("Scraped Subjects Data:")
    document = {disciplina: main_subjects}
    collection.insert_one(document)
    for subject in main_subjects:
      
       print(subject)

finally:
    driver.quit()
