import requests
from twilio.rest import Client
import os
from dotenv import load_dotenv

load_dotenv()

STOCK_API = os.getenv("STOCK_API")
NEWS_API = os.getenv("NEWS_API")
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH = os.getenv("TWILIO_AUTH")
TWILIO_FROM = os.getenv("TWILIO_FROM")
TO_NUMBER = os.getenv("TO_NUMBER")


STOCK_NAME = "TSLA"
COMPANY_NAME = "Tesla Inc"

STOCK_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"

stock_params = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK_NAME,
    "apikey": STOCK_API,
}

response = requests.get(STOCK_ENDPOINT, params=stock_params)
response.raise_for_status()
data = response.json()["Time Series (Daily)"]

#getting yesterday's and day-before yesterday's closing
dates = sorted(data.keys(), reverse=True)
yesterday_close = float(data[dates[0]]["4. close"])
day_before_close = float(data[dates[1]]["4. close"])

diff = yesterday_close - day_before_close
up_down = "🔺" if diff > 0 else "🔻"
change_percent = (abs(diff) / day_before_close) * 100

if change_percent >= 5:
    news_params = {
        "qInTitle": "Tesla",
        "from": dates[1],
        "sortBy": "publishedAt",
        "language": "en",
        "apiKey": NEWS_API,
    }

    response = requests.get(NEWS_ENDPOINT, params=news_params)
    response.raise_for_status()
    article_data = response.json()["articles"][:3]

    message_body = f"{STOCK_NAME}: {up_down}{change_percent:.2f}% change\n\n"

    for i, article in enumerate(article_data, 1):
        message_body += f"{i}. {article['title']}\n"
        message_body += f"{article['description']}\n"
        message_body += f"Read more: {article['url']}\n\n"

    # send through Twilio
    client = Client(TWILIO_SID, TWILIO_AUTH)
    message = client.messages.create(
        body=message_body,
        from_=TWILIO_FROM,
        to=TO_NUMBER
    )
else:
    pass

