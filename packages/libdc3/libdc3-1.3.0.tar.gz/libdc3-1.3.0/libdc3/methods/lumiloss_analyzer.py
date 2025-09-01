from typing import Optional

from ..units import UNIT_PREFIXES
from ..utils import flatten_ranges


class LumilossAnalyzer:
    def __init__(
        self,
        rr_oms_lumis: list[dict],
        bril_lumis: list[dict],
        pre_json: dict,
        dc_json: dict,
        low_lumi_runs: list,
        ignore_runs: list,
        bril_unit: str,
        target_unit: Optional[str] = None,
    ):
        self.final_unit = target_unit or bril_unit

        # Totals
        self.total_delivered = 0.0
        self.total_recorded = 0.0
        self.total_low_lumi = 0.0
        self.total_ignore_runs = 0.0
        self.total_not_stable_beams = 0.0
        self.total_not_in_oms_rr = 0.0
        self.total_processed = 0.0
        self.total_loss = 0.0
        self.total_certified = 0.0
        self.data_taking_eff = 0.0
        self.recorded_eff = 0.0
        self.processed_eff = 0.0

        # Bad lumis
        self.bad_lumis = self.parse_and_merge_lumis(
            rr_oms_lumis, bril_lumis, pre_json, dc_json, ignore_runs, low_lumi_runs, bril_unit, target_unit
        )

    def parse_and_merge_lumis(
        self, rr_oms_lumis, bril_lumis, pre_json, dc_json, ignore_runs, low_lumi_runs, bril_unit, target_unit
    ):
        rr_oms_indexed = {(lumi["run_number"], lumi["ls_number"]): lumi for lumi in rr_oms_lumis}
        expanded_json = {run_number: list(flatten_ranges(lumi_ranges)) for run_number, lumi_ranges in dc_json.items()}
        expanded_pre_json = {
            run_number: list(flatten_ranges(lumi_ranges)) for run_number, lumi_ranges in pre_json.items()
        }

        if bril_unit and target_unit:
            bril_factor = 1 / UNIT_PREFIXES[bril_unit]
            target_factor = UNIT_PREFIXES[target_unit]
            convert_factor = bril_factor * target_factor
        else:
            convert_factor = 1

        bad_lumis = []
        for bril_lumi in bril_lumis:
            run_number = bril_lumi["run_number"]
            ls_number = bril_lumi["ls_number"]
            delivered = bril_lumi["delivered"] * convert_factor
            recorded = bril_lumi["recorded"] * convert_factor
            self.total_delivered += delivered
            self.total_recorded += recorded

            if run_number in low_lumi_runs:
                self.total_low_lumi += recorded
                continue
            if run_number in ignore_runs:
                self.total_ignore_runs += recorded
                continue

            # Filter out lumis not in preJSON
            pre_json_lumisections = expanded_pre_json.get(run_number, [])
            if ls_number not in pre_json_lumisections:
                self.total_not_stable_beams += recorded
                continue

            # if bril has more lumisections than rr_oms, skip
            rr_oms_lumi = rr_oms_indexed.get((run_number, ls_number))
            if rr_oms_lumi is None:
                self.total_not_in_oms_rr += recorded
                continue

            # If lumisection reached this stage it is DC Processed
            self.total_processed += recorded

            # Let's check if is in dc json to classify it as good/bad
            # If run number is not in expanded_json, it means there are no good lumis
            # this happens with runs not in DCS json
            good_lumisections = expanded_json.get(run_number, [])
            if ls_number not in good_lumisections:
                bad_lumis.append(
                    {
                        "datetime": bril_lumi["datetime"],
                        "run_number": run_number,
                        "ls_number": ls_number,
                        "delivered": delivered,
                        "recorded": recorded,
                        **rr_oms_lumi,
                    }
                )
                self.total_loss += recorded
            else:
                self.total_certified += recorded

        return bad_lumis

    @staticmethod
    def __add_subsystem_loss(lumi: dict, subsystems_loss: dict):
        """
        In a given lumi entry, verify all RR subsystems flags and collect
        their inclusive contribution to the global lumiloss
        """
        for subsystem in subsystems_loss:
            if lumi.get(subsystem) is False:  # GOOD = True, else = False
                subsystems_loss[subsystem] += lumi["recorded"]

    @staticmethod
    def __add_dcs_loss(lumi: dict, dcs_loss: dict):
        """
        In a given lumi entry, verify all OMS flags and collect their
        inclusive contribution to the global lumiloss
        """
        for bit in dcs_loss:
            if lumi.get(bit) is False:
                dcs_loss[bit] += lumi["recorded"]

    @staticmethod
    def __blame_subdetectors(lumi: dict, subdetectors: dict[str, list]):
        """
        In a given lumi entry, verify all flags that identifies a subdetector
        and collect which subdetectors + flags failed for that given lumi
        """
        blamed_subdetectors = {}
        for subdetector, flags in subdetectors.items():
            bad_flags = [flag for flag in flags if lumi.get(flag) is False]
            if len(bad_flags) > 0:
                blamed_subdetectors[subdetector] = bad_flags
        return blamed_subdetectors

    @staticmethod
    def __add_cms_inclusive_loss_by_subdetector(lumi: dict, blamed_subdetector: str, cms_inclusive_loss):
        """
        In a given lumi entry, add a blamed subdetector inclusive contribution
        for the global loss
        """
        cms_inclusive_loss[blamed_subdetector] += lumi["recorded"]

    @staticmethod
    def __add_subsystem_run_inclusive_loss_by_subdetector(
        lumi: dict, blamed_subdetector: str, bad_flags: list[str], subsystem_run_inclusive_loss
    ):
        """
        In a given lumi entry, add a blamed subdetector inclusive contribution
        for the global loss discriminated by the run_number and ls_number
        """
        run_number = lumi["run_number"]
        ls_number = lumi["ls_number"]

        if run_number not in subsystem_run_inclusive_loss[blamed_subdetector]:
            subsystem_run_inclusive_loss[blamed_subdetector][run_number] = {"total_loss": 0, "by_lumisection": []}

        subsystem_run_inclusive_loss[blamed_subdetector][run_number]["total_loss"] += lumi["recorded"]
        subsystem_run_inclusive_loss[blamed_subdetector][run_number]["by_lumisection"].append(
            {"ls_number": ls_number, "bad_flags": bad_flags, "loss": lumi["recorded"]}
        )

    @staticmethod
    def __add_subdetector_inclusive_loss(
        lumi: dict, blamed_subdetector: str, bad_flags: list[str], detector_inclusive_loss
    ):
        """
        In a given lumi entry, add each subdetector component inclusive
        loss contribution for the global loss
        """
        for bad_flag in bad_flags:
            detector_inclusive_loss[blamed_subdetector][bad_flag] += lumi["recorded"]

    @staticmethod
    def __add_subdetector_exclusive_loss(
        lumi: dict, blamed_subdetector: str, bad_flags: list[str], detector_exclusive_loss
    ):
        """
        In a given lumi entry, add each subdetector component exclusive
        loss contribution for the global loss
        """
        if len(bad_flags) == 1:
            detector_exclusive_loss[blamed_subdetector][bad_flags[0]] += lumi["recorded"]
        elif len(bad_flags) > 1:
            detector_exclusive_loss[blamed_subdetector]["Mixed"] += lumi["recorded"]

    @staticmethod
    def __add_subsystem_run_exclusive_loss(
        lumi: dict, blamed_subdetectors_dict: dict[str, list[str]], subsystem_run_exclusive_loss
    ):
        run_number = lumi["run_number"]
        ls_number = lumi["ls_number"]
        joined_detectors = " ".join(blamed_subdetectors_dict.keys())
        joined_flags = [flag for flags in blamed_subdetectors_dict.values() for flag in flags]

        if joined_detectors not in subsystem_run_exclusive_loss:
            subsystem_run_exclusive_loss[joined_detectors] = {}
        if run_number not in subsystem_run_exclusive_loss[joined_detectors]:
            subsystem_run_exclusive_loss[joined_detectors][run_number] = {"total_loss": 0, "by_lumisection": []}

        subsystem_run_exclusive_loss[joined_detectors][run_number]["total_loss"] += lumi["recorded"]
        subsystem_run_exclusive_loss[joined_detectors][run_number]["by_lumisection"].append(
            {"ls_number": ls_number, "bad_flags": joined_flags, "loss": lumi["recorded"]}
        )

    @staticmethod
    def __add_cms_numerator_exclusive_loss(lumi, blamed_subdetectors, cms_numerator_exclusive_loss):
        # If more than one subdetector is blamed or L1T or HLT is blamed, assign lumiloss to Mixed
        l1t_or_hlt_blamed = "L1T" in blamed_subdetectors or "HLT" in blamed_subdetectors

        if len(blamed_subdetectors) > 1 or l1t_or_hlt_blamed:
            cms_numerator_exclusive_loss["Mixed"] += lumi["recorded"]
        elif len(blamed_subdetectors) == 1:
            cms_numerator_exclusive_loss[blamed_subdetectors[0]] += lumi["recorded"]

    @staticmethod
    def __add_cms_exclusive_loss(lumi, blamed_subdetectors, cms_exclusive_loss):
        # If (only L1T or only HLT) or only (L1T and HLT), append + detectors to blamed string
        joined_detectors = " ".join(blamed_subdetectors)
        l1t_or_hlt_blamed = "L1T" in blamed_subdetectors or "HLT" in blamed_subdetectors
        l1t_and_hlt_blamed = "L1T" in blamed_subdetectors and "HLT" in blamed_subdetectors

        if len(blamed_subdetectors) == 1 and l1t_or_hlt_blamed:
            joined_detectors = joined_detectors + " + detectors"
        elif len(blamed_subdetectors) == 2 and l1t_and_hlt_blamed:
            joined_detectors = joined_detectors + " + detectors"

        if joined_detectors not in cms_exclusive_loss:
            cms_exclusive_loss[joined_detectors] = 0

        cms_exclusive_loss[joined_detectors] += lumi["recorded"]

    def analyze(self, dcs, subsystems, subdetectors):
        # Creating empty objects to hold lumiloss
        dcs_loss = {bit: 0 for bit in dcs}
        subsystems_loss = {subsystem: 0 for subsystem in subsystems}
        detector_inclusive_loss = {
            subdetector: {flag: 0 for flag in flags} for subdetector, flags in subdetectors.items()
        }
        detector_exclusive_loss = {
            subdetector: {flag: 0 for flag in flags} for subdetector, flags in subdetectors.items()
        }
        detector_exclusive_loss = {
            subdetector: {**flags, "Mixed": 0} for subdetector, flags in detector_exclusive_loss.items()
        }
        cms_inclusive_loss = {subdetector: 0 for subdetector in subdetectors}
        cms_numerator_exclusive_loss = {subdetector: 0 for subdetector in subdetectors}
        cms_numerator_exclusive_loss = {**cms_numerator_exclusive_loss, "Mixed": 0}
        cms_exclusive_loss = {}
        subsystem_run_inclusive_loss = {subdetector: {} for subdetector in subdetectors}
        subsystem_run_exclusive_loss = {}

        for lumi in self.bad_lumis:
            blamed_subdetectors_dict = self.__blame_subdetectors(lumi, subdetectors)
            blamed_subdetectors_list = list(blamed_subdetectors_dict.keys())
            self.__add_dcs_loss(lumi, dcs_loss)
            self.__add_subsystem_loss(lumi, subsystems_loss)

            for blamed_subdetector, bad_flags in blamed_subdetectors_dict.items():
                self.__add_cms_inclusive_loss_by_subdetector(lumi, blamed_subdetector, cms_inclusive_loss)
                self.__add_subsystem_run_inclusive_loss_by_subdetector(
                    lumi, blamed_subdetector, bad_flags, subsystem_run_inclusive_loss
                )
                self.__add_subdetector_inclusive_loss(lumi, blamed_subdetector, bad_flags, detector_inclusive_loss)
                self.__add_subdetector_exclusive_loss(lumi, blamed_subdetector, bad_flags, detector_exclusive_loss)

            self.__add_subsystem_run_exclusive_loss(lumi, blamed_subdetectors_dict, subsystem_run_exclusive_loss)
            self.__add_cms_numerator_exclusive_loss(lumi, blamed_subdetectors_list, cms_numerator_exclusive_loss)
            self.__add_cms_exclusive_loss(lumi, blamed_subdetectors_list, cms_exclusive_loss)

        if self.total_loss > 0:
            cms_frac_exclusive_loss = {
                key: value / self.total_loss for key, value in cms_numerator_exclusive_loss.items()
            }
            cms_detailed_frac_exclusive_loss = {
                key: (100 * value) / self.total_loss for key, value in cms_exclusive_loss.items()
            }
        else:
            cms_frac_exclusive_loss = {}
            cms_detailed_frac_exclusive_loss = {}

        self.data_taking_eff = self.total_recorded / self.total_delivered
        self.recorded_eff = self.total_certified / self.total_recorded
        self.processed_eff = self.total_certified / self.total_processed

        stats = {
            "unit": self.final_unit,
            "total_delivered": self.total_delivered,
            "total_recorded": self.total_recorded,
            "total_low_lumi": self.total_low_lumi,
            "total_ignore_runs": self.total_ignore_runs,
            "total_not_stable_beams": self.total_not_stable_beams,
            "total_not_in_oms_rr": self.total_not_in_oms_rr,
            "total_processed": self.total_processed,
            "total_loss": self.total_loss,
            "total_certified": self.total_certified,
            "data_taking_eff": self.data_taking_eff,
            "recorded_eff": self.recorded_eff,
            "processed_eff": self.processed_eff,
        }

        return {
            "stats": stats,
            "dcs_loss": dcs_loss,
            "subsystems_loss": subsystems_loss,
            "cms_inclusive_loss": cms_inclusive_loss,
            "cms_exclusive_loss": cms_exclusive_loss,
            "cms_numerator_exclusive_loss": cms_numerator_exclusive_loss,
            "cms_frac_exclusive_loss": cms_frac_exclusive_loss,
            "cms_detailed_frac_exclusive_loss": cms_detailed_frac_exclusive_loss,
            "detector_inclusive_loss": detector_inclusive_loss,
            "detector_exclusive_loss": detector_exclusive_loss,
            "subsystem_run_inclusive_loss": subsystem_run_inclusive_loss,
            "subsystem_run_exclusive_loss": subsystem_run_exclusive_loss,
        }

    def format_lumiloss_by_run(self, data: dict):
        text = ""
        text += f"Luminosity unit: {self.final_unit}\n\n"
        for subdetector, run_obj in data.items():
            text += f"Subdetector: {subdetector}\n"
            text += "-----------------------------"
            for run_number, lumi_obj in run_obj.items():
                text += "-----------------------------\n"
                text += f"Run number: {run_number} (total loss: {lumi_obj['total_loss']})\n"
                for lumi in lumi_obj["by_lumisection"]:
                    text += str(lumi)
                    text += "\n"
            text += "\n\n\n"
        return text
