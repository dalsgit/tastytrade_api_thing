import yfinance as yf
import datetime
from lib.tasty_operations import MyTasty
from lib.TTOrder import *
from tastytrade_sdk import Quote
import time

class Naive:
    EQUITY_SYMBOL = ""
    PERCENT_CHANGE = .01
    DTE = datetime.timedelta(days=7)
    expiration = datetime.date.today() + DTE
    buyQuote, sellQuote = None, None
    occ = []
    strikes = []
    def __init__(self, eq="SPY"):
        self.EQUITY_SYMBOL = eq #'IWM'  # 'QQQ' #'SPY'
        self.mytasty = MyTasty()
    def get_current_price(self, symbol=EQUITY_SYMBOL):
        eq = yf.Ticker(symbol)
        return eq.history(period='1d')['Close'].iloc[-1]

    def get_strikes(self, increment=1):
        current_price = self.get_current_price(self.EQUITY_SYMBOL)
        strike_price_buy = round(current_price * (1 + self.PERCENT_CHANGE))
        strike_price_sell = strike_price_buy + increment
        self.strikes = [strike_price_buy, strike_price_sell]
        return self.strikes

    def get_occ(self, symbol, strike_price):
        return "{eq}   {dt}C{strike_price:05d}000".format(eq=symbol, dt=self.expiration.strftime('%y%m%d'),
                                                          strike_price=strike_price)

    def get_number_of_options(self, strike_price):
        return len(self.mytasty.tasty.api.get(
            '/instruments/equity-options',
            params=[('symbol[]', self.EQUITY_SYMBOL), ('expiration[]', self.expiration.strftime('%y%m%d')),
                    ('strike_price[]', strike_price)]
        ))

    def get_occ_symbols(self):
        # if we encounter that there are no options for this expiration, add a day
        # do this max of 5 times
        max_times = 5
        strike_price_buy, strike_price_sell = self.get_strikes()
        while (self.get_number_of_options(strike_price_buy) < 1 and max_times > 0):
            self.expiration += datetime.timedelta(days=1)
            occ = self.get_occ(self.EQUITY_SYMBOL, self.expiration, strike_price_buy)
            options = self.mytasty.tasty.api.get(
                '/instruments/equity-options',
                params=[('symbol[]', occ)]  # example: 'SPY   231017C00434000'
            )
            max_times -= 1

        buyOCC = self.get_occ(self.EQUITY_SYMBOL, strike_price_buy)
        sellOCC = self.get_occ(self.EQUITY_SYMBOL, strike_price_sell)
        print("Buy OCC: {occ}".format(occ=buyOCC))
        print("Sell OCC: {occ}".format(occ=sellOCC))
        self.occ = [buyOCC, sellOCC]
        return self.occ

    def on_quote(self, quote: Quote):
        [buyOCC, sellOCC] = self.occ
        if (quote.symbol == buyOCC):
            print("Buy option expiry {0} , strike {strike} at bid {bid}"
                  .format(self.expiration, strike=0, bid=quote.ask_price))
            self.buyQuote = quote
        elif (quote.symbol == sellOCC):
            print(
                "Sell option expiry {0}, strike {strike} at bid {bid}"
                .format(self.expiration, strike=0, bid=quote.bid_price))
            self.sellQuote = quote

    def get_quotes(self):
        symbols = self.get_occ_symbols()
        subscription = self.mytasty.tasty.market_data.subscribe(symbols=symbols, on_quote=self.on_quote)
        subscription.open()
        time.sleep(1)
        subscription.close()

    def get_naive_cost(self):
        self.get_quotes()
        cost = round(self.buyQuote.ask_price - self.sellQuote.bid_price, 2)
        print("The price of {0} naive is {1}".format(self.EQUITY_SYMBOL, cost))
        return cost
def main():
    eqs = ["SPY", "QQQ", "IWM"]
    for eq in eqs:
        n = Naive(eq)
        n.get_naive_cost()

if __name__ == "__main__":
    main()