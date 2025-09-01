from itertools import groupby
from typing import Optional

from ..utils import yield_range


class JsonProducer:
    def __init__(self, rr_oms_lumis: list[dict], ignore_hlt_emergency: bool = False):
        self.lumis = self.__group_lumis_by_run(rr_oms_lumis)
        self.ignore_hlt_emergency = ignore_hlt_emergency

    @staticmethod
    def __group_lumis_by_run(rr_oms_lumis: list[dict]):
        rr_oms_lumis.sort(key=lambda x: x["run_number"])
        return {run_number: list(lumis) for run_number, lumis in groupby(rr_oms_lumis, key=lambda x: x["run_number"])}

    def __is_hlt_on_emergency(self, oms_lumisection: dict):
        return oms_lumisection.get("prescale_name") == "Emergency" and oms_lumisection.get("prescale_index") == 0

    def __is_good_lumi_oms(self, run_number: int, flags_to_check: list[str], lumi_flags: dict):
        # corner_case for call_7, OMS beam1_present and beam2_present flags are not correct
        if run_number > 355100 and run_number <= 355208:
            flags_to_check = flags_to_check.copy()  # Create a new object in the function scope to avoid modifying the original flags list during the iteration
            if "beam1_present" in flags_to_check:
                flags_to_check.remove("beam1_present")
            if "beam2_present" in flags_to_check:
                flags_to_check.remove("beam2_present")

        considered_flags = [lumi_flags.get(flag, False) for flag in flags_to_check]
        considered_flags = [False if flag is None else flag for flag in considered_flags]
        return sum(considered_flags) == len(considered_flags)

    def __is_good_lumi_rr(self, flags_to_check: list[str], lumi_flags: dict):
        considered_flags = [lumi_flags.get(flag, False) for flag in flags_to_check]
        considered_flags = [False if flag is None else flag for flag in considered_flags]
        return sum(considered_flags) == len(considered_flags)

    def generate(self, oms_flags: list[str], rr_flags: Optional[list[str]] = None):
        compact_json = {}
        for run_number, lumis in self.lumis.items():
            good_lumis = []
            for lumi_flags in lumis:
                is_good_lumi = self.__is_good_lumi_oms(run_number, oms_flags, lumi_flags)
                if rr_flags:
                    is_good_lumi = is_good_lumi and self.__is_good_lumi_rr(rr_flags, lumi_flags)
                else:
                    # If rr_flags is not given (a.k.a preview), we can check hlt emergency
                    if self.ignore_hlt_emergency is False:
                        is_good_lumi = is_good_lumi and not self.__is_hlt_on_emergency(lumi_flags)

                if is_good_lumi:
                    good_lumis.append(lumi_flags["ls_number"])

            good_lumis = list(yield_range(good_lumis))
            if len(good_lumis) > 0:
                compact_json[run_number] = good_lumis

        return compact_json
