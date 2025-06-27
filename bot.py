# bot.py

import os
import time
import random
import pickle
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc

from config import *
from utils import get_random_proxy, get_random_user_agent

IS_TERMUX = 'com.termux' in os.getcwd()

class ShopeeBot:
    def __init__(self):
        self.driver = self.setup_browser()
        self.wait = WebDriverWait(self.driver, 15)

    def setup_browser(self):
        options = uc.ChromeOptions()

        if IS_TERMUX:
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.binary_location = '/data/data/com.termux/files/usr/bin/chromium'

        proxy = get_random_proxy()
        if proxy:
            options.add_argument(f'--proxy-server={proxy}')

        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument(f"user-agent={get_random_user_agent()}")

        return uc.Chrome(options=options)

    def human_like_click(self, element):
        ActionChains(self.driver).move_to_element(element).pause(random.uniform(0.1, 0.5)).click().perform()

    def save_cookies(self):
        with open(COOKIE_FILE, "wb") as f:
            pickle.dump(self.driver.get_cookies(), f)

    def load_cookies(self):
        try:
            with open(COOKIE_FILE, "rb") as f:
                cookies = pickle.load(f)
                for cookie in cookies:
                    self.driver.add_cookie(cookie)
            return True
        except:
            return False

    def login(self):
        self.driver.get(SHOPEE_URL)

        if self.load_cookies():
            self.driver.refresh()
            try:
                self.wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(., 'Beranda')]")))
                return True
            except:
                os.remove(COOKIE_FILE)

        self.driver.get(f"{SHOPEE_URL}/buyer/login")

        email_field = self.wait.until(EC.presence_of_element_located((By.NAME, "loginKey")))
        email_field.send_keys(EMAIL)
        time.sleep(random.uniform(0.5, 1.5))

        password_field = self.driver.find_element(By.NAME, "password")
        password_field.send_keys(PASSWORD)
        time.sleep(random.uniform(0.3, 1))

        login_btn = self.driver.find_element(By.XPATH, "//button[contains(., 'Log In')]")
        self.human_like_click(login_btn)

        try:
            self.wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(., 'Beranda')]")))
            self.save_cookies()
            return True
        except:
            return False

    def scrape_harga_stok(self):
        price_elem = self.driver.find_element(By.CSS_SELECTOR, ".pqTWkA")
        stock_elem = self.driver.find_element(By.CSS_SELECTOR, ".product-quantity__available")

        harga = int(price_elem.text.replace("Rp", "").replace(".", "").strip())
        stok = int(''.join(filter(str.isdigit, stock_elem.text)))

        print(f"Harga: Rp{harga} | Stok: {stok}")

        if harga > MAX_HARGA or stok < MIN_STOK:
            print("Syarat tidak sesuai. Batal beli.")
            return False
        return True

    def beli_produk(self):
        self.driver.get(FLASH_SALE_URL)
        time.sleep(2)

        target_time = time.mktime(time.strptime(WAKTU_FLASH_SALE, "%Y-%m-%d %H:%M:%S"))
        while time.time() < target_time:
            remaining = target_time - time.time()
            print(f"Menunggu {int(remaining)} detik...", end="\r")
            time.sleep(1)

        print("\nMulai Flash Sale!")
        self.driver.refresh()
        products = self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".flash-sale-item-card")))
        target_product = products[INDEX_PRODUK]

        self.driver.execute_script("arguments[0].scrollIntoView({behavior:'smooth'});", target_product)
        self.human_like_click(target_product)
        time.sleep(1)

        if not self.scrape_harga_stok():
            return

        if MODE_SIMULASI:
            print("Simulasi selesai. Tidak checkout.")
            return

        buy_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Beli Sekarang')]")))
        self.human_like_click(buy_btn)

        checkout_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Checkout')]")))
        self.human_like_click(checkout_btn)

        payment_method = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(., 'Transfer Bank')]")))
        self.human_like_click(payment_method)

        confirm_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Buat Pesanan')]")))
        self.human_like_click(confirm_btn)

        print("Pesanan berhasil dibuat!")

    def run(self):
        try:
            if self.login():
                self.beli_produk()
        finally:
            self.driver.quit()

if __name__ == "__main__":
    print("Shopee Flash Sale Bot 🚀")
    bot = ShopeeBot()
    bot.run()
