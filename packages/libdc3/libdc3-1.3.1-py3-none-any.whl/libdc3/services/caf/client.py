import re
from typing import Any, ClassVar, Optional

from bs4 import BeautifulSoup, Tag
from requests import Session
from requests.adapters import HTTPAdapter, Retry


TIMEOUT = 30


class CAF:
    CAF_URL = "https://cms-service-dqmdc.web.cern.ch/CAF/certification/"
    DCS_PATTERNS: ClassVar[dict[str, str]] = {
        "default": r"Collisions(.*)_(.*)_(\d{6})_(\d{6})_DCSOnly_TkPx\.json",
        "Collisions22": r"Cert_Collisions(.*)_(\d{6})_(\d{6})_(.*)_DCSOnly_TkPx\.json",
    }
    ENDPOINTS: ClassVar[dict[str, dict[str, Any]]] = {
        "muon": {
            "endpoint": "/",
            "lookup_pattern": r"Cert_Collisions(.*)_(\d{6})_(\d{6})_Muon.json",
        },
        "golden": {
            "endpoint": "/",
            "lookup_pattern": r"Cert_Collisions(.*)_(\d{6})_(\d{6})_Golden.json",
        },
        "dcs": {
            "endpoint": "/DCSOnly_JSONS/dailyDCSOnlyJSON/",
            "lookup_pattern": DCS_PATTERNS,
        },
    }

    def __init__(self, class_name: str, kind: str):
        self.base_url = self.CAF_URL + class_name + self.ENDPOINTS[kind]["endpoint"]
        self.lookup_pattern = self.ENDPOINTS[kind]["lookup_pattern"]

        if kind == "dcs":
            if class_name in self.DCS_PATTERNS:
                self.lookup_pattern = self.lookup_pattern[class_name]
            else:
                self.lookup_pattern = self.lookup_pattern["default"]

        self.options = self.__get_options()
        self.latest = self.__select_latest()

    def __parse_html(self, text: str):
        soup = BeautifulSoup(text, "html.parser")
        rows = soup.find_all("img", alt="[   ]")
        response = []
        for row in rows:
            link = row.find_next("a")
            if link is None or not isinstance(link, Tag):
                continue

            name = link.text
            if not re.match(self.lookup_pattern, name):
                continue

            try:
                href = link["href"]
            except KeyError:
                continue

            sibling = link.next_sibling
            if not sibling or not isinstance(sibling, str):
                continue

            details = sibling.strip().split()
            if len(details) < 3:
                continue

            date = f"{details[0]} {details[1]}"
            size = details[2]
            response.append({"name": name, "url": self.base_url + href, "last_modified": date, "size": size})

        return response

    def __get_retry_forbidden(self, url, timeout):
        retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[403])
        with Session() as s:
            s.mount(self.CAF_URL, HTTPAdapter(max_retries=retries))
            response = s.get(url, timeout=timeout)

        return response

    def __get_options(self):
        response = self.__get_retry_forbidden(self.base_url, timeout=TIMEOUT)
        response.raise_for_status()
        return self.__parse_html(response.text)

    def __select_latest(self):
        return sorted(self.options, key=lambda x: x["last_modified"])[-1]

    def download(self, name: Optional[str] = None, latest: bool = False):
        url = next(filter(lambda x: x["name"] == name, self.options))["url"] if name else self.latest["url"]
        response = self.__get_retry_forbidden(url, timeout=TIMEOUT)
        response.raise_for_status()
        return response.json()
