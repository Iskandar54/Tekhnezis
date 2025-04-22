from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def setup_driver():
    options = Options()
    
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--headless")
    options.add_argument("--enable-unsafe-swiftshader")
    options.add_argument('--log-level=1')
    
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    return driver

def get_wildberries_price(driver, url):
    try:
        driver.get(url)
        
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.product-page__grid")))
        
        try:
            elements = driver.find_elements(By.XPATH, "//*[contains(text(), '₽')]")
            for element in elements:
                if element.is_displayed():
                    price = element.text.strip()
                    break
        except:
            pass
        
        if price:
            price = price.replace(' ', '').replace('\n', '').replace('\xa0', '')
            return price
        else:
            raise Exception("Цена не найдена ни одним из способов")
            
    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")
        driver.save_screenshot('wildberries_error.png')
        return None

async def start_parser_wb(url, xpath):    
    driver = setup_driver()
    try:
        price = get_wildberries_price(driver, url)
        if price:
            return price
        else:
            print("Не удалось получить цену WB")
    finally:
        if driver:
            driver.quit()