# pip install selenium webdriver-manager
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import os

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--use-fake-ui-for-media-stream")
chrome_options.add_argument("--headless=new")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# 👉 Netlify URL
website = "https://rajeeva.netlify.app"
driver.get(website)

rec_file = os.path.join(os.getcwd(), "input.txt")


def listen():
    try:
        # wait for start button
        start_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, 'startButton'))
        )
        start_button.click()
        print("Listening...")

        prev_line = ""

        while True:
            try:
                output_element = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.ID, 'output'))
                )
                current_text = output_element.text.strip()

                # sirf last line uthao (agar multiple line aa rahi ho to)
                if "\n" in current_text:
                    last_line = current_text.splitlines()[-1].strip()
                else:
                    last_line = current_text

                if last_line and last_line != prev_line:
                    prev_line = last_line
                    with open(rec_file, "a", encoding="utf-8") as file:  # append mode
                        file.write(last_line.lower() + "\n")
                    print("USER :", last_line)

            except Exception:
                pass

            time.sleep(0.5)

    except KeyboardInterrupt:
        print("Stopped by user.")
        driver.quit()
    except Exception as e:
        print("Error:", e)
        driver.quit()


listen()
