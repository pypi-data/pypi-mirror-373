from typing import Optional

from ..config import dc3_config
from ..services.caf.client import CAF
from ..services.dqmgui.client import DQMGUI
from .bril_actions import BrilActions
from .rr_actions import RunRegistryActions


class NextCallError(Exception):
    pass


class NextCallGenerator:
    def __init__(
        self,
        rr_class_name: str,
        rr_dataset_name: str,
        bril_brilws_version: str,
        bril_unit: str,
        bril_low_lumi_thr: float,
        gui_lookup_datasets: list[str],
        bril_beamstatus: Optional[str] = None,
        bril_amodetag: Optional[str] = None,
        bril_normtag: Optional[str] = None,
        bril_datatag: Optional[str] = None,
        refresh_runs_if_needed: bool = False,
    ):
        self.rr_class_name = rr_class_name
        self.gui_lookup_datasets = gui_lookup_datasets
        self.refresh_runs_if_needed = refresh_runs_if_needed
        self.rr_actions = RunRegistryActions(rr_class_name, rr_dataset_name)
        self.bril_actions = BrilActions(
            bril_brilws_version,
            bril_unit,
            bril_low_lumi_thr,
            bril_beamstatus,
            bril_amodetag,
            bril_normtag,
            bril_datatag,
        )

    def get_initial_run_list(self):
        """
        Fetch the initial list of runs by fetching any open
        dataset in run registry and filtering all runs in every cycle
        """
        ignore_runs = self.rr_actions.fetch_runs_from_all_cycles()
        open_datasets = self.rr_actions.fetch_open_datasets(ignore_runs)
        return [run["run_number"] for run in open_datasets]

    def check_and_fix_online_rr_oms_mismatches(self, run_list: list[int]):
        """
        Check which runs in online RR need to fetch OMS updates
        and refresh them if instructed
        """
        mismatches = self.rr_actions.fetch_runs_that_need_update(run_list)
        if self.refresh_runs_if_needed and len(mismatches) > 0:
            self.rr_actions.refresh_runs(mismatches)
        return mismatches

    def get_bril_lumis_by_run(self, run_list: list[int]):
        """
        Fetch bril runs by lumisection and aggregate by run
        """
        bril_output = self.bril_actions.fetch_lumis(begin=min(run_list), end=max(run_list)).get("detailed")
        used_keys = ["run_number", "ls_number", "delivered", "recorded", "datetime"]
        bril_output = [{key: value for key, value in item.items() if key in used_keys} for item in bril_output]
        bril_output = self.bril_actions.agg_by_run(bril_output)
        return [by_run for by_run in bril_output if by_run["run_number"] in run_list]

    def check_rr_oms_bril_mismatches(self, run_list: list[int], bril_by_run: list[dict]):
        """
        Check for mismatched between many cases:
            - offline rr ls count X oms last cms active number
            - oms ls count X online rr ls count
            - oms ls count X offline rr ls count
            - oms ls count X bril ls count
        """
        online_rr_lumi_count = self.rr_actions.multi_count_online_rr_lumis(run_list)
        offline_rr_lumi_count = self.rr_actions.multi_count_offline_rr_lumis(run_list)
        oms_count = self.rr_actions.multi_count_oms_lumis(run_list)
        oms_lumi_count = {run: count["total"] for run, count in oms_count.items()}
        oms_last_cms_active_ls = {run: count["last_cms_active_ls"] for run, count in oms_count.items()}
        bril_lumi_count = {r["run_number"]: r["ls_count"] for r in bril_by_run}
        mismatches_forced_inequality = []
        mismatches_loose = []
        for run_number in run_list:
            is_mismatch_force_inequality = (
                offline_rr_lumi_count[run_number] < oms_last_cms_active_ls[run_number]
                or oms_lumi_count[run_number] != online_rr_lumi_count[run_number]
                or oms_lumi_count[run_number] != offline_rr_lumi_count[run_number]
                or oms_lumi_count[run_number] != bril_lumi_count[run_number]
            )
            is_mismatch_loose = (
                offline_rr_lumi_count[run_number] < oms_last_cms_active_ls[run_number]
                or oms_lumi_count[run_number] != online_rr_lumi_count[run_number]
                or oms_lumi_count[run_number] != offline_rr_lumi_count[run_number]
                or oms_lumi_count[run_number] < bril_lumi_count[run_number]
            )
            mismatch = {
                "run_number": run_number,
                "online_rr": online_rr_lumi_count[run_number],
                "offline_rr": offline_rr_lumi_count[run_number],
                "oms": oms_lumi_count[run_number],
                "oms_last_cms_active_ls": oms_last_cms_active_ls[run_number],
                "bril": bril_lumi_count[run_number],
            }
            if is_mismatch_force_inequality:
                mismatches_forced_inequality.append(mismatch)
            if is_mismatch_loose:
                mismatches_loose.append(mismatch)

        return mismatches_forced_inequality, mismatches_loose

    def check_runs_not_in_bril(self, run_list: list[int], bril_by_run: list[dict]):
        """
        Given a list of runs and a list of bril runs,
        check which runs are not returned by bril
        """
        bril_runs = [r["run_number"] for r in bril_by_run]
        return [run for run in run_list if run not in bril_runs]

    def check_low_lumi_runs(self, bril_by_run: list[dict]):
        """
        Given a list of bril runs,
        check which runs are classified as having low luminosity
        """
        return [run for run in bril_by_run if run["has_low_recorded"]]

    def check_dcs_json(self, run_list: list[int]):
        """
        Given a run list, check which runs *are not*
        present in the latest DCS-only json.
        """
        caf = CAF(self.rr_class_name, kind="dcs")
        dcs_json = caf.download(latest=True)
        runs_not_in_dcs_json = [run for run in run_list if str(run) not in dcs_json.keys()]
        return {"filename": caf.latest.get("name"), "run_numbers": runs_not_in_dcs_json}

    def check_runs_not_in_dqmgui(self, run_list: list[int]):
        """
        Given a list of run, check which runs
        are not in DQMGUI for each dataset.
        """
        dc3_config.validate_x509cert()
        if dc3_config.AUTH_CERT is None or dc3_config.AUTH_CERT_KEY is None:
            raise RuntimeError("dc3_config.AUTH_CERT or dc3_config.AUTH_CERT_KEY cannot be None")

        dqmgui = DQMGUI(dc3_config.AUTH_CERT, dc3_config.AUTH_CERT_KEY)
        return {dt: dqmgui.check_if_runs_are_present(dt, run_list) for dt in self.gui_lookup_datasets}

    def generate(self):
        """
        Run next call analysis
        """
        # First step: get initial run list from RR only
        initial_run_list = self.get_initial_run_list()
        if len(initial_run_list) == 0:
            raise NextCallError("Initial run list is empty")

        final_run_list = initial_run_list.copy()

        # Second step: check if any run needs to be updated
        online_rr_oms_mismatches = self.check_and_fix_online_rr_oms_mismatches(initial_run_list)

        # Third step: get bril data that will be used later
        bril_by_run = self.get_bril_lumis_by_run(initial_run_list)

        # Fourth step: check runs not in Bril yet
        runs_not_in_bril = self.check_runs_not_in_bril(initial_run_list, bril_by_run)
        for run_not_in_bril in runs_not_in_bril:
            final_run_list.remove(run_not_in_bril)

        # Fifth step: check for bril x rr x oms mismatches
        rr_oms_bril_mismatches_forced_inequality, rr_oms_bril_mismatches_loose = self.check_rr_oms_bril_mismatches(
            final_run_list, bril_by_run
        )

        # Sixth step: check low lumi runs
        low_lumi_runs = self.check_low_lumi_runs(bril_by_run)
        for low_lumi_run in low_lumi_runs:
            final_run_list.remove(low_lumi_run["run_number"])

        # Seventh: filter out runs not in DCS json
        not_in_dcs_runs = self.check_dcs_json(final_run_list)
        for not_in_dcs_run in not_in_dcs_runs["run_numbers"]:
            final_run_list.remove(not_in_dcs_run)

        # Eighth: filter out runs not in DQMGUI
        not_in_dqmgui_datasets = self.check_runs_not_in_dqmgui(final_run_list)
        for not_in_dqmgui_runs in not_in_dqmgui_datasets.values():
            for not_in_dqmgui_run in not_in_dqmgui_runs:
                # We need to catch the ValueError
                # since multiple datasets might try to remove the same run
                try:
                    final_run_list.remove(not_in_dqmgui_run)
                except ValueError:
                    pass

        return {
            "initial_run_list": initial_run_list,
            "online_rr_oms_mismatches": online_rr_oms_mismatches,
            "runs_not_in_bril": runs_not_in_bril,
            "rr_oms_bril_mismatches_forced_inequality": rr_oms_bril_mismatches_forced_inequality,
            "rr_oms_bril_mismatches_loose": rr_oms_bril_mismatches_loose,
            "low_lumi_runs": low_lumi_runs,
            "not_in_dcs_runs": not_in_dcs_runs,
            "not_in_dqmgui_datasets": not_in_dqmgui_datasets,
            "final_run_list": final_run_list,
        }
