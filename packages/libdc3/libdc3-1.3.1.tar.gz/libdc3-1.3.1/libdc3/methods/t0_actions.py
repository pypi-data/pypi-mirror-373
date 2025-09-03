from ..config import dc3_config
from ..services.t0.client import T0WM


class T0Actions:
    def __init__(self):
        dc3_config.validate_x509cert()
        self.client = T0WM(dc3_config.AUTH_CERT, dc3_config.AUTH_CERT_KEY)

    def eras_history(self, era: str):
        eras = self.client.get_era_history(era=era)
        return sorted(eras["result"], key=lambda x: x["era"])
