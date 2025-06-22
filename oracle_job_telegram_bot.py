
import os
import time
import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from telegram import Bot, InputFile, error as tg_error
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from flask import Flask
import threading

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
AUTHORIZED_USER_ID = int(os.getenv("AUTHORIZED_USER_ID", "0"))

def apply_jobs(bot):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    chrome_service = Service(executable_path="/usr/bin/chromedriver")
    driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

    try:
        print("🔐 Opening Naukri direct search page...")
        driver.get("https://www.naukri.com/oracle-techno-functional-consultant-jobs-in-delhi-ncr")
        time.sleep(10)

        jobs = driver.find_elements(By.CLASS_NAME, "jobTuple")[:5]
        if not jobs:
            raise Exception("No jobs found on Naukri page.")
        for job in jobs:
            try:
                job.click()
                time.sleep(3)
                driver.switch_to.window(driver.window_handles[1])
                apply_btns = driver.find_elements(By.XPATH, "//button[contains(text(), 'Apply')]")
                if apply_btns:
                    apply_btns[0].click()
                    time.sleep(2)
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                print("✅ Applied to a Naukri job.")
            except Exception as e:
                print(f"❌ Naukri Job Error: {e}")
                driver.switch_to.window(driver.window_handles[0])

        print("🔐 Opening LinkedIn...")
        driver.get("https://www.linkedin.com/jobs")
        time.sleep(10)

        search_box = driver.find_element(By.XPATH, "//input[contains(@class,'jobs-search-box__text-input')]")
        search_box.send_keys("Oracle Techno-Functional Consultant")
        search_box.submit()
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
    except Exception as e:
        print("❌ Error during job apply:", e)
        screenshot_path = "error_screenshot.png"
        driver.save_screenshot(screenshot_path)
        if bot:
            try:
                with open(screenshot_path, "rb") as img:
                    bot.send_photo(chat_id=AUTHORIZED_USER_ID, photo=InputFile(img), caption="❌ Error screenshot during job apply")
            except Exception as send_err:
                print("❌ Failed to send screenshot:", send_err)
        raise
    finally:
        driver.quit()
        print("🛑 Browser closed.")

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
            apply_jobs(context.bot)
            duration = round(time.time() - start_time, 1)
            update.message.reply_text(f"🎯 Jobs applied in {duration} seconds.")
        except Exception as e:
            error_details = traceback.format_exc()
            print("❌ Bot crashed:\n", error_details)
            update.message.reply_text(f"❌ Bot crashed:\n{e}")
    else:
        update.message.reply_text("Send 'Apply now' to apply.")

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

if __name__ == '__main__':
    threading.Thread(target=run_flask).start()
    run_telegram_bot()
