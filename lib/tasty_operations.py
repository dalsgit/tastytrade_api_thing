import sys
from lib.TTConfig import TTConfig
from lib.TTOrder import *
from tastytrade_sdk import Tastytrade

class MyTasty:

    def __init__(self, ttconfig=TTConfig()):
        self.ttconfig = ttconfig
        self.tasty = Tastytrade()
        if ttconfig.use_prod:
            self.tasty.login(
                login=ttconfig.username,
                password=ttconfig.password
            )
        else:
            self.tasty = Tastytrade(ttconfig.cert_uri.replace("https://", ""))
            self.tasty.login(
                login=ttconfig.cert_username,
                password=ttconfig.cert_password
            )
