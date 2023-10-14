from lib.TTConfig import TTConfig
from tastytrade_sdk import Tastytrade
from lib.TTOrder import *
from lib.TTApi import TTApi

ttconfig = TTConfig()
print(ttconfig.use_prod)

tasty = Tastytrade()
if ttconfig.use_prod:
    tasty.login(
        login=ttconfig.username,
        password=ttconfig.password
    )
else:
    tasty = Tastytrade(ttconfig.cert_uri.replace("https://",""))
    tasty.login(
        login=ttconfig.cert_username,
        password=ttconfig.cert_password
    )

order = TTOrder(order_type=TTOrderType.LIMIT, tif=TTTimeInForce.GTC, price=1.0,
    price_effect=TTPriceEffect.CREDIT)
order.add_leg(symbol="AAPL", quantity=1.0, instrument_type=TTInstrumentType.EQUITY_OPTION,
    action=TTLegAction.BTO)
ttapi = TTApi()
ttapi.login()
accounts = ttapi.fetch_accounts()
ttapi.simple_order("account", order)
