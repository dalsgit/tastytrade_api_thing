import configparser
class TTConfig:
    config: configparser.ConfigParser = configparser.ConfigParser()
    use_prod: bool = False
    use_mfa: bool = False
    username: str = None
    password: str = None
    cert_username: str = None
    cert_password: str = None
    cert_uri: str = None
    prod_uri: str = None
    cert_wss: str = None
    prod_wss: str = None
    def __init__(self, path: str = "./", filename: str = "tt.config") -> None:
        self.config.read(f"{path}/{filename}")
        self.use_prod = self.config.get("Config", "use_prod") in (
            "True",
            "true",
            "yes",
            "t",
            "1",
            "y",
            "on",
        )
        self.use_mfa = self.config.get("Config", "use_mfa") in (
            "True",
            "true",
            "yes",
            "t",
            "1",
            "y",
            "on",
        )
        self.username = self.config.get("Credentials", "username")
        self.password = self.config.get("Credentials", "password")
        self.cert_username = self.config.get("Credentials", "cert.username")
        self.cert_password = self.config.get("Credentials", "cert.password")
        if(not self.use_prod):
            self.username = self.cert_username
            self.password = self.cert_password
        self.cert_uri = self.config.get("URI", "cert")
        self.prod_uri = self.config.get("URI", "prod")
        self.cert_wss = self.config.get("WSS", "cert")
        self.prod_wss = self.config.get("WSS", "prod")

