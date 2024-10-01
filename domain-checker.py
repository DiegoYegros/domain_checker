import os
import requests
import logging
from time import sleep

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler('subdomain_checker.log'),
                        logging.StreamHandler() # sends log to stdout in order to  see logs with docker logs.
                        ])

# Telegram Bot Token and Chat ID
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
TELEGRAM_API_URL = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'

SUBDOMAINS = os.getenv('SUBDOMAINS', '').split(',')
def check_subdomain(subdomain, retries=3):
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
        sleep(5) # delay before retrying
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

def main(subdomains):
    """Main function to check subdomains and send alerts."""
    while True:
        for subdomain in subdomains:
            if not check_subdomain(subdomain):
                send_alert(subdomain)
        sleep(60)  # Wait for 60 seconds before checking again

if __name__ == "__main__":
    if not SUBDOMAINS:
        logging.error("Not subdomains provided. Exiting.")
        exit(1)
    logging.info("Subdomain checker started.")
    main(SUBDOMAINS)

