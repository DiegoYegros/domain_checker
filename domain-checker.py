import os
import requests
import logging
import datetime
from time import sleep

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler('subdomain_checker.log'),
                        logging.StreamHandler()  # Sends log to stdout to see logs with docker logs.
                    ])


# Initialize counters
total_requests = 0
successful_requests = 0
failed_requests = 0
last_report_time = datetime.datetime.now()

# Telegram Bot Token and Chat ID
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
SUBDOMAINS = os.getenv('SUBDOMAINS', '').split(',')
RETRIES = int(os.getenv('RETRIES', 3))
SLEEP_TIME = int(os.getenv('SLEEP_TIME', 60))
REPORT_INTERVAL = int(os.getenv('REPORT_INTERVAL', 86400))  # 24hs in seconds
DELAY_BEFORE_RETRYING = int(os.getenv('DELAY_BEFORE_RETRYING', 60))

TELEGRAM_API_URL = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'


def check_subdomain(subdomain, retries=RETRIES, delay=DELAY_BEFORE_RETRYING):
    """Check if the subdomain is accessible."""
    global total_requests, successful_requests, failed_requests
    attempt = 0

    if not subdomain.startswith(('http://', 'https://')):
        subdomain = f'http://{subdomain}'

    while attempt < retries:
        total_requests += 1
        try:
            response = requests.get(subdomain, timeout=5)
            if response.status_code == 200:
                logging.info(f'Subdomain {subdomain} is UP.')
                successful_requests += 1
                return True
            else:
                logging.warning(f'Subdomain {subdomain} is DOWN with status code {response.status_code}.')
        except requests.exceptions.RequestException as e:
            logging.error(f'Subdomain {subdomain} is DOWN. Exception: {str(e)}')
            failed_requests += 1
        attempt += 1
        logging.info(f"Retrying subdomain {subdomain} in {delay} seconds... (Attempt {attempt}/{retries})")
        sleep(delay)
    logging.error(f"Subdomain {subdomain} is DOWN after {retries} attempts.")
    failed_requests += 1
    return False

def send_report():
    global total_requests
    global successful_requests
    global failed_requests
    message = (f"📊 Report:\n"
               f"Total Requests: {total_requests}\n"
               f"✅ Successful: {successful_requests}\n"
               f"❌ Failed: {failed_requests}"
               f"Sending next report in {REPORT_INTERVAL} seconds.")
    payload = {
        'chat_id': CHAT_ID,
        'text': message
    }
    try:
        response = requests.post(TELEGRAM_API_URL, data=payload)
        if response.status_code == 200:
            logging.info('Successfully sent report.')
        else:
            logging.error(f'Failed to send report. Status code: {response.status_code}')
        total_requests = 0
        successful_requests = 0
        failed_requests = 0
    except requests.exceptions.RequestException as e:
        logging.error(f'Failed to send report. Exception: {str(e)}')

def send_alert(subdomain):
    """Send an alert to the user via Telegram."""
    message = f"⚠️ Alert: {subdomain} is DOWN!"
    payload = {
        'chat_id': CHAT_ID,
        'text': message
    }
    try:
        response = requests.post(TELEGRAM_API_URL, data=payload)
        if response.status_code == 200:
            logging.info(f'Successfully sent alert for {subdomain}.')
        else:
            logging.error(f'Failed to send alert for {subdomain}. Status code: {response.status_code}')
    except requests.exceptions.RequestException as e:
        logging.error(f'Failed to send alert for {subdomain}. Exception: {str(e)}')

def main(subdomains, retries=RETRIES, sleep_time=SLEEP_TIME, delay=DELAY_BEFORE_RETRYING):
    """Main function to check subdomains and send alerts."""
    global last_report_time
    while True:
        current_time = datetime.datetime.now()
        if last_report_time is not None and (current_time - last_report_time).total_seconds() >= REPORT_INTERVAL:
            send_report()
            last_report_time = current_time
        for subdomain in subdomains:
            if not check_subdomain(subdomain, retries, delay):
                send_alert(subdomain)
        logging.info(f"Sleeping for {sleep_time} seconds before the next check...")
        sleep(sleep_time)

if __name__ == "__main__":
    if not SUBDOMAINS:
        logging.error("No subdomains provided. Exiting.")
        exit(1)
    logging.info("Subdomain checker started.")
    logging.info(f"Sleep time: {SLEEP_TIME}, Retries: {RETRIES}, Delay before retrying: {DELAY_BEFORE_RETRYING}, Subdomains: {SUBDOMAINS}, Report Interval: {REPORT_INTERVAL}")

    main(SUBDOMAINS)