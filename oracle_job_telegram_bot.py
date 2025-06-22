
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import time
import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
AUTHORIZED_USER_ID = int(os.getenv("AUTHORIZED_USER_ID", "0"))

def apply_jobs():
    driver = webdriver.Chrome()
    try:
        driver.get("https://www.naukri.com/")
        input("Log in to Naukri manually, then press Enter here...")

        search_box = driver.find_element(By.ID, "qsb-keyword-sugg")
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
            except Exception as e:
                print(f"Naukri Error: {e}")
                driver.switch_to.window(driver.window_handles[0])

        driver.get("https://www.linkedin.com/jobs")
        input("Log in to LinkedIn manually, then press Enter here...")

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
            except Exception as e:
                print(f"LinkedIn Error: {e}")

    finally:
        driver.quit()

def start(update, context):
    update.message.reply_text("🤖 Ready to apply for Oracle jobs. Send 'Apply now' to begin.")

def handle_message(update, context):
    user_id = update.message.chat_id
    if user_id != AUTHORIZED_USER_ID:
        update.message.reply_text("⛔ Unauthorized user.")
        return

    text = update.message.text.lower()
    if "apply" in text:
        update.message.reply_text("✅ Starting job application process...")
        apply_jobs()
        update.message.reply_text("🎯 Jobs applied.")
    else:
        update.message.reply_text("Send 'Apply now' to trigger job applications.")

def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
# Add at the top with other imports
from flask import Flask
import threading

# Your existing main() stays as is
def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    updater.start_polling()
    updater.idle()

# Dummy web server so Render thinks this is a "web service"
app = Flask(__name__)

@app.route("/")
def status():
    return "✅ Telegram bot is running"

if __name__ == '__main__':
    # Run Flask in a background thread
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=8000)).start()
    # Start the bot
    main()
