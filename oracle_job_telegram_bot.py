
import os
import time
import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import error as tg_error
from flask import Flask
import threading

# === Telegram Auth ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
AUTHORIZED_USER_ID = int(os.getenv("AUTHORIZED_USER_ID", "0"))

# === Job Application Logic ===
def apply_jobs():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    chrome_service = Service(executable_path="/usr/bin/chromedriver")
    driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

    try:
        print("🔐 Opening Naukri...")
        driver.get("https://www.naukri.com/")
        print("⏳ Waiting for search box...")
        wait = WebDriverWait(driver, 15)
        search_box = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//input[contains(@placeholder, 'Skills, Designations, Companies')]")
        ))
        search_box.send_keys("Oracle Techno-Functional Consultant")
        search_box.send_keys(Keys.RETURN)
        time.sleep(5)

        jobs = driver.find_elements(By.CLASS_NAME, "jobTuple")[:5]
        for job in jobs:
            try:
                job.click()
                time.sleep(3)
                driver.switch_to.window(driver.window_handles[1])
                apply_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Apply')]")
                apply_btn.click()
                time.sleep(2)
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                print("✅ Applied to a Naukri job.")
            except Exception as e:
                print(f"❌ Naukri Job Error: {e}")
                driver.switch_to.window(driver.window_handles[0])

        print("🔐 Opening LinkedIn...")
        driver.get("https://www.linkedin.com/jobs")
        print("⏳ Waiting 10 seconds for LinkedIn to load...")
        time.sleep(10)

        search_box = driver.find_element(By.XPATH, "//input[contains(@class,'jobs-search-box__text-input')]")
        search_box.send_keys("Oracle Techno-Functional Consultant")
        search_box.send_keys(Keys.RETURN)
        time.sleep(5)

        job_cards = driver.find_elements(By.CLASS_NAME, "job-card-container")[:5]
        for job in job_cards:
            try:
                job.click()
                time.sleep(3)
                easy_apply = driver.find_element(By.XPATH, "//button[contains(text(), 'Easy Apply')]")
                easy_apply.click()
                time.sleep(2)
                print("✅ Applied to a LinkedIn job.")
            except Exception as e:
                print(f"❌ LinkedIn Job Error: {e}")

    finally:
        driver.quit()
        print("🛑 Browser closed.")

# === Telegram Handlers ===
def start(update, context):
    update.message.reply_text("🤖 Bot is live. Send 'Apply now' to trigger applications.")

def handle_message(update, context):
    user_id = update.message.chat_id
    if user_id != AUTHORIZED_USER_ID:
        update.message.reply_text("⛔ Unauthorized user.")
        return
    if "apply" in update.message.text.lower():
        update.message.reply_text("✅ Starting job application process...")
        try:
            start_time = time.time()
            apply_jobs()
            duration = round(time.time() - start_time, 1)
            update.message.reply_text(f"🎯 Jobs applied in {duration} seconds.")
        except Exception as e:
            print("❌ Bot Error:", traceback.format_exc())
            update.message.reply_text(f"❌ Bot crashed:\n{e}")
    else:
        update.message.reply_text("Send 'Apply now' to apply.")

# === Flask Dummy Server ===
app = Flask(__name__)

@app.route('/')
def index():
    return "✅ Telegram bot is running via Flask."

def run_flask():
    app.run(host="0.0.0.0", port=8000)

def run_telegram_bot():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    try:
        updater.start_polling()
        updater.idle()
    except tg_error.Conflict:
        print("❌ Another instance of the bot is already running. Stop it first.")

# === Main ===
if __name__ == '__main__':
    threading.Thread(target=run_flask).start()
    run_telegram_bot()
