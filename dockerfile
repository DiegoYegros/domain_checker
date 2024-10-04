FROM python:3.11-slim

WORKDIR /app

COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install cron
RUN apt-get update && apt-get install -y cron

# Create the log file
RUN touch /var/log/cron.log

ENV BOT_TOKEN=''
ENV CHAT_ID=''
ENV DOMAINS=''
ENV RETRIES=''
ENV SLEEP_TIME=''
ENV DELAY_BEFORE_RETRYING=''
CMD ["python", "/app/domain-checker.py"]