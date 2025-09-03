from datetime import datetime
from itertools import groupby
from typing import Optional, Union

from ..config import dc3_config
from ..services.bril.client import Brilcalc


class BrilActions:
    def __init__(
        self,
        brilws_version: str,
        unit: str,
        low_lumi_thr: float,
        beamstatus: Optional[str] = None,
        amodetag: Optional[str] = None,
        normtag: Optional[str] = None,
        datatag: Optional[str] = None,
    ):
        self.brilws_version = brilws_version
        self.unit = unit
        self.low_lumi_thr = low_lumi_thr
        self.beamstatus = beamstatus
        self.amodetag = amodetag
        self.normtag = normtag
        self.datatag = datatag

    def fetch_lumis(
        self,
        run_number: Optional[int] = None,
        begin: Optional[Union[int, str]] = None,
        end: Optional[Union[int, str]] = None,
    ):
        if run_number is None and begin is None and end is None:
            raise ValueError("A run number or begin and end must be specific")
        elif run_number:
            begin = None
            end = None
        elif begin is None or end is None:
            raise ValueError("If run number is not specified, begin and end should be specified")

        brilcalc = Brilcalc(dc3_config.KEYTAB_USR, dc3_config.KEYTAB_PWD, brilws_version=self.brilws_version)
        lumis = brilcalc.lumi(
            connect="web",
            beamstatus=self.beamstatus,
            unit=self.unit,
            amodetag=self.amodetag,
            normtag=self.normtag,
            runnumber=run_number,
            begin=begin,
            end=end,
            output_style="html",
            byls=True,
            datatag=self.datatag,
        )
        lumis["detailed"] = sorted(lumis["detailed"], key=lambda x: (x["run"], x["ls_number"]))

        for lumi in lumis["detailed"]:
            lumi["run_number"] = lumi.pop("run")
            lumi["datetime"] = datetime.strptime(lumi["time"], "%m/%d/%y %H:%M:%S")
            lumi["delivered"] = lumi.pop(f"delivered({self.unit})")
            lumi["recorded"] = lumi.pop(f"recorded({self.unit})")

        return lumis

    def agg_by_run(self, bril_detailed: list[dict]) -> list[dict]:
        by_run = []
        groups = groupby(bril_detailed, key=lambda x: x["run_number"])
        for run_number, lumis in groups:
            ls_count = 0
            run_delivered = 0.0
            run_recorded = 0.0
            for lumi in lumis:
                ls_count += 1
                run_delivered += lumi["delivered"]
                run_recorded += lumi["recorded"]
            by_run.append(
                {
                    "run_number": run_number,
                    "delivered": run_delivered,
                    "recorded": run_recorded,
                    "unit": self.unit,
                    "ls_count": ls_count,
                    "has_low_recorded": run_recorded <= self.low_lumi_thr,
                }
            )

        return by_run
