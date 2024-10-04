### Running the Domain Checker
First build the docker image with:

```bash
docker build -t domain_checker .
```

To run the container, you can use the following command, just replace the example values:

```bash
docker run -d \
    --name domain_checker \
    -e BOT_TOKEN='your_bot_token_here' \
    -e CHAT_ID='your_chat_id_here' \
    -e SUBDOMAINS='example1.com,example2.com,example3.com' \
    domain-checker
```
