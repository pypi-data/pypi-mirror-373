class Config:
    KEYTAB_USR = None
    KEYTAB_PWD = None
    AUTH_CERT = None
    AUTH_CERT_KEY = None

    def set_keytab_usr(self, value: str):
        self.KEYTAB_USR = value

    def set_keytab_pwd(self, value: str):
        self.KEYTAB_PWD = value

    def set_auth_cert_path(self, value: str):
        self.AUTH_CERT = value

    def set_auth_key_path(self, value: str):
        self.AUTH_CERT_KEY = value

    def validate_x509cert(self):
        if self.AUTH_CERT is None or self.AUTH_CERT_KEY is None:
            raise ValueError("AUTH_CERT and/or AUTH_CERT_KEY shouldn't be None.")


dc3_config = Config()
