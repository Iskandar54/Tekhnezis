import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


def setup_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument('--log-level=3')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    service = Service(
        ChromeDriverManager().install(),
        service_args=['--silent'],  
        log_path=os.devnull,       
    )
    return webdriver.Chrome(service=service, options=options)

def get_generic_price(driver, url, xpath=None):
    driver.get(url)
    try:
        if xpath:
            try:
                element = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, xpath)))
                return element.text.strip()
            except:
                pass
        
        elements = driver.find_elements(By.XPATH, "//*[contains(text(), '₽')]")
        for el in elements:
            if el.is_displayed():
                return el.text.strip()
        
        elements = driver.find_elements(By.XPATH, "//span[contains(@class, 'price')]")
        for el in elements:
            if el.is_displayed():
                return el.text.strip()
        
        raise Exception("Цена не найдена")
    except Exception as e:
        return None

async def start_parser_generic(url, xpath):
    driver = setup_driver()
    try:
        return get_generic_price(driver, url, xpath)
    finally:
        driver.quit()
