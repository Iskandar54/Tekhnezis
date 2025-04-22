
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium_stealth import stealth
from webdriver_manager.chrome import ChromeDriverManager

def setup_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("start-maximized")
    options.add_argument('--log-level=1')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(options=options, service=service)
    stealth(driver=driver,
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.53 Safari/537.36',
        languages=["ru-RU", "ru"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
        run_on_insecure_origins=True,)
    return driver

def get_yandex_price(driver, url, xpath):
    driver.get(url)
    
    try:
        price_element = driver.find_element(By.XPATH, xpath)
        return price_element.text.strip()
    except NoSuchElementException as e:
        print(f'Ошибка: элемент не найден {e}')
        return None

async def start_parser_yandex(url, xpath):
    driver = setup_driver()
    try:
        price = get_yandex_price(driver, url, xpath)
        if price:
            return price
        else:
            print("Не удалось получить цену Яндекс.Маркет")
    finally:
        if driver:
            driver.quit()