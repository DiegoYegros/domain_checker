import os
import requests
import logging
from time import sleep

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler('subdomain_checker.log'),
                        logging.StreamHandler()  # Sends log to stdout to see logs with docker logs.
                    ])

# Telegram Bot Token and Chat ID
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
TELEGRAM_API_URL = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'

SUBDOMAINS = os.getenv('SUBDOMAINS', '').split(',')
RETRIES = int(os.getenv('RETRIES', 3))
SLEEP_TIME = int(os.getenv('SLEEP_TIME', 60))
DELAY_BEFORE_RETRYING = int(os.getenv('DELAY_BEFORE_RETRYING', 60))
print(f"Sleep time: {SLEEP_TIME}, Retries: {RETRIES}, Delay before retrying: {DELAY_BEFORE_RETRYING}, Subdomains: {SUBDOMAINS}")
def check_subdomain(subdomain, retries=RETRIES, delay=DELAY_BEFORE_RETRYING):
    """Check if the subdomain is accessible."""
    attempt = 0
    while attempt < retries:
        try:
            response = requests.get(f'http://{subdomain}', timeout=5)
            if response.status_code == 200:
                logging.info(f'Subdomain {subdomain} is UP.')
                return True
            else:
                logging.warning(f'Subdomain {subdomain} is DOWN with status code {response.status_code}.')
        except requests.exceptions.RequestException as e:
            logging.error(f'Subdomain {subdomain} is DOWN. Exception: {str(e)}')
        attempt += 1
        logging.info(f"Retrying subdomain {subdomain} in {delay} seconds... (Attempt {attempt}/{retries})")
        sleep(delay)
    logging.error(f"Subdomain {subdomain} is DOWN after {retries} attempts.")
    return False

def send_alert(subdomain):
    """Send an alert to the user via Telegram."""
    message = f"⚠️ Alert: Subdomain {subdomain} is DOWN!"
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
    while True:
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
    main(SUBDOMAINS)