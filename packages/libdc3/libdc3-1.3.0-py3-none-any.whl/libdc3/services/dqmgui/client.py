import requests
import urllib3
from requests.exceptions import SSLError


class DQMGUI:
    OFFLINE_SAMPLES_URL = "https://cmsweb.cern.ch/dqm/offline"

    def __init__(self, cert: str, key: str, timeout: int = 30):
        self.cert = (cert, key)
        self.timeout = timeout

    def get_samples(self, dataset_name: str, run_number: str):
        url = self.OFFLINE_SAMPLES_URL + "/data/json/samples"
        params = {"match": dataset_name, "run": run_number}

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

    def check_if_runs_are_present(self, dataset_name: str, run_numbers: list[int]):
        runs = f"({'|'.join(str(run) for run in run_numbers)})"
        dts_in_gui = self.get_samples(dataset_name, runs)
        runs_in_gui = (
            [int(item["run"]) for item in dts_in_gui["samples"][0]["items"]] if len(dts_in_gui["samples"]) > 0 else []
        )
        return [run for run in run_numbers if run not in runs_in_gui]
