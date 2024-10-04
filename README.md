### Running the Domain Checker
First build the docker image with:

```bash
docker build -t domain-checker .
```

To run the container, you can use the following command, just replace the example values:
#### Default Values
RETRIES=3
SLEEP_TIME=60
DELAY_BEFORE_RETRYING=60

```bash
docker run -d \
    --name domain-checker \
    -e BOT_TOKEN='your_bot_token_here' \
    -e CHAT_ID='your_chat_id_here' \
    -e RETRIES='retries_amount_here' \
    -e SLEEP_TIME='sleep_time_here' \
    -e DELAY_BEFORE_RETRYING='delay_time_here' \
    -e SUBDOMAINS='example1.com,example2.com,example3.com' \
    domain-checker
```