from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def setup_driver():
    options = Options()
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--headless")
    options.add_argument('--log-level=1')
    options.add_argument('--no-sandbox')    
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    return driver

def get_ozon_price(driver, url):
    try:
        driver.get(url)

        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, "//div[@data-widget='webPrice']")))
        
        price_selectors = [
            "//span[contains(@class, 'l7o')]",
            "//*[contains(text(), '₽')]",
            "//div[@data-widget='webPrice']//span[contains(@class, 'tsHeadline')]"
        ]
        
        for selector in price_selectors:
            try:
                price_element = WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.XPATH, selector)))
                price = price_element.text.strip()  
                if price:  
                    return price
            except:
                continue
        else:
            raise Exception("Цена не найдена ни по одному селектору")

    except Exception as e:
        print(f"Ошибка: {str(e)}")
        driver.save_screenshot("ozon_error.png")
        return None

async def start_parser_ozon(url, xpath):
    driver = setup_driver()
    try:
        price = get_ozon_price(driver, url)
        if price:
            return price
        else:
            print("Не удалось получить цену Ozon")
    finally:
        if driver:
            driver.quit()