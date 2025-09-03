import requests
import urllib3
from requests.exceptions import SSLError


class T0WM:
    T0_URL = "https://cmsweb.cern.ch/t0wmadatasvc/prod"

    def __init__(self, cert: str, key: str, timeout: int = 30):
        self.cert = (cert, key)
        self.timeout = timeout

    def get_era_history(self, era: str):
        url = self.T0_URL + "/era_history"
        params = {"era": era}

        try:
            response = requests.get(url, params=params, cert=self.cert, timeout=self.timeout)
        except SSLError:
            # Running this curl request from LXPlus works without -k flag
            # This is here for local testing and for Openshift deployment
            with urllib3.warnings.catch_warnings():
                urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
                response = requests.get(
                    url,
                    params=params,
                    cert=self.cert,
                    timeout=self.timeout,
                    verify=False,  # noqa: S501
                )

        response.raise_for_status()
        return response.json()
