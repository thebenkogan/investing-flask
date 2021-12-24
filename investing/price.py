import requests
from bs4 import BeautifulSoup
import re


# Returns the current stock/fund price of 'ticker', None if no price found.
def get_price(ticker):
    url = f"https://www.marketwatch.com/investing/stock/{ticker}"
    r = requests.get(url)

    soup = BeautifulSoup(r.text, "html.parser")
    try:
        results = soup.find_all(class_="intraday__price")
        price = float(re.findall("\d*\.?\d+", results[0].text)[0])
    except Exception:
        price = None

    return price
