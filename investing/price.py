import decimal
import requests
from bs4 import BeautifulSoup
import re
from .models import Investment
from sqlalchemy import desc


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


class GroupStats:
    def __init__(self, group):
        # Maps stock symbol to current price {ticker, current price}
        self.stocks = {}

        # History of investments in reverse chronological order
        self.history = (
            Investment.query.filter_by(group_id=group.id)
            .order_by(desc(Investment.date))
            .all()
        )

        # Maps user to stock investments stats
        # {user id, {stock, (shares, amount invested)}}
        self.user_invests = {}

        # Maps user to share of group balance {user id, share of balance}
        self.user_shares = {}

        # Total balance of the group
        self.balance = 0

        # Get stock prices and user investments per stock
        for investment in group.investments:
            if investment.ticker not in self.stocks:
                self.stocks[investment.ticker] = decimal.Decimal(
                    get_price(investment.ticker)
                )
            stats = self.user_invests.get(investment.user_id, {})
            total = stats.get(investment.ticker, (0, 0))
            stats[investment.ticker] = (
                total[0] + investment.amount,
                total[1] + investment.shares,
            )
            self.user_invests[investment.user_id] = stats

        # Get user balances and total group balance
        if len(group.investments) > 0:
            for user in group.users:
                user_balance = 0
                for ticker, (shares, amount) in self.user_invests[user.id].items():
                    stock_balance = shares * self.stocks[ticker]
                    user_balance += stock_balance
                    self.balance += stock_balance
                self.user_shares[user.id] = user_balance
