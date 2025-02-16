import yfinance as yf
import datetime
from lib.tasty_operations import MyTasty
from lib.TTOrder import *
from tastytrade_sdk import Quote
import time
from lib.TTApi import *


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

    def get_occ(self, symbol, expiration:datetime, strike_price):
        return "{eq}   {dt}C{strike_price:05d}000".format(eq=symbol, dt=expiration.strftime('%y%m%d'),
                                                          strike_price=strike_price)

    # symbol here is the options OCC symbol
    def get_number_of_options(self, symbol: str):
        return len(self.mytasty.tasty.api.get(
            '/instruments/equity-options',
            params=[('symbol[]', symbol)]
        )['data']['items'])

    def get_occ_symbols(self):
        # if we encounter that there are no options for this expiration, add a day
        # do this max of 5 times
        max_times = 5
        strike_price_buy, strike_price_sell = self.get_strikes()
        while (self.get_number_of_options(self.get_occ(self.EQUITY_SYMBOL, self.expiration, strike_price_buy)) < 1 and max_times > 0):
            self.expiration += datetime.timedelta(days=1)
            max_times -= 1
        buyOCC = self.get_occ(self.EQUITY_SYMBOL, self.expiration, strike_price_buy)
        sellOCC = self.get_occ(self.EQUITY_SYMBOL, self.expiration, strike_price_sell)
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
        time.sleep(2)
        subscription.close()

    def buy(self, dryrun: bool = True):
        if(self.buyQuote == None):
            self.get_quotes()
        [buyOCC, sellOCC] = self.occ
        order = TTOrder(order_type=TTOrderType.LIMIT, tif=TTTimeInForce.GTC, price=0.1,
                        price_effect=TTPriceEffect.DEBIT)
        order.add_leg(symbol=buyOCC, quantity=1.0, instrument_type=TTInstrumentType.EQUITY_OPTION,
                      action=TTLegAction.BTO)
        order.add_leg(symbol=sellOCC, quantity=1.0, instrument_type=TTInstrumentType.EQUITY_OPTION,
                      action=TTLegAction.STO)
        ttapi = TTApi()
        ttapi.login()
        if(dryrun):
            ttapi.simple_order('5WT37921', order)
        else:
            ttapi.real_order(password="", account='5WT37921', order=order)

    def get_naive_cost(self):
        self.get_quotes()
        cost = round(self.buyQuote.ask_price - self.sellQuote.bid_price, 2)
        print("The price of {0} naive is {1}".format(self.EQUITY_SYMBOL, cost))
        return cost

def main():
    eqs = [ "IWM" ]
    eqs = ["SPY", "QQQ", "IWM"]
    for eq in eqs:
        n = Naive(eq)
        n.get_naive_cost()
        #n.buy(dryrun=False)

if __name__ == "__main__":
    main()