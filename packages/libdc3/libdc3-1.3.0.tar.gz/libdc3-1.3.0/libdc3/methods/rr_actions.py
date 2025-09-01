import os
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Optional

import runregistry as rr


class RunRegistryActions:
    def __init__(self, class_name: str, dataset_name: str):
        self.__validate_tokens()
        self.class_name = class_name
        self.dataset_name = dataset_name

    def __validate_tokens(self):
        if os.getenv("SSO_CLIENT_ID") is None or os.getenv("SSO_CLIENT_SECRET") is None:
            raise ValueError(
                "Environment variables SSO_CLIENT_ID and/or SSO_CLIENT_SECRET shouldn't be None for runregistry python package."
            )

    def fetch_runs_from_all_cycles(self) -> list[int]:
        cycles = rr.get_cycles()
        runs_in_cycles = [cd["run_number"] for cycle in cycles for cd in cycle["CycleDataset"]]
        return sorted(set(runs_in_cycles))

    def fetch_runs_in_cycles(self, cycles_list: list[str]):
        cycles = rr.get_cycles()
        cycles = [cycle for cycle in cycles if cycle["cycle_name"] in cycles_list]
        runs_in_cycles = [cd["run_number"] for cycle in cycles for cd in cycle["CycleDataset"]]
        return sorted(set(runs_in_cycles))

    def fetch_open_datasets(self, ignore_runs: Optional[list[int]] = None) -> list[int]:
        """
        Fetch all OPEN runs in Offline RR editable datasets of given
        <class_name> and <dataset_name> optionally filtering out a run list
        """
        filter_: dict[str, Any] = {
            "and": [
                {"rr_attributes.class": {"=": self.class_name}},
                {"name": {"=": self.dataset_name}},
                {"dataset_attributes.global_state": {"=": "OPEN"}},
            ],
            "name": {"and": [{"<>": "online"}]},
            "dataset_attributes.global_state": {"and": [{"or": [{"=": "OPEN"}, {"=": "SIGNOFF"}, {"=": "COMPLETED"}]}]},
        }
        if ignore_runs:
            apfilt = {"and": [{"run_number": {"<>": rn}} for rn in ignore_runs]}
            filter_["and"].append(apfilt)

        return rr.get_datasets(
            filter=filter_,
            ignore_filter_transformation=True,
        )

    def fetch_datasets(
        self, min_run: Optional[int] = None, max_run: Optional[int] = None, ignore_runs: Optional[list[int]] = None
    ) -> list[int]:
        """
        Fetch all OPEN runs in Offline RR editable datasets of given
        <class_name> and <dataset_name> optionally filtering out a run list
        """
        filter_: dict[str, Any] = {
            "and": [
                {"rr_attributes.class": {"=": self.class_name}},
                {"name": {"=": self.dataset_name}},
            ],
            "name": {"and": [{"<>": "online"}]},
            "dataset_attributes.global_state": {"and": [{"or": [{"=": "OPEN"}, {"=": "SIGNOFF"}, {"=": "COMPLETED"}]}]},
        }
        if ignore_runs:
            apfilt = {"and": [{"run_number": {"<>": rn}} for rn in ignore_runs]}
            filter_["and"].append(apfilt)
        if min_run and max_run:
            mmfilt = [
                {"run_number": {"<=": max_run}},
                {"run_number": {">=": min_run}},
            ]
            filter_["and"].extend(mmfilt)

        return rr.get_datasets(
            filter=filter_,
            ignore_filter_transformation=True,
        )

    def fetch_runs(
        self,
        run_list: Optional[list[int]] = None,
        min_run: Optional[int] = None,
        max_run: Optional[int] = None,
        b_field: float = 3.7,
    ):
        filter_dict: dict[str, Any] = {"class": {"=": self.class_name}, "oms_attributes.b_field": {">=": b_field}}
        if run_list:
            filter_dict["run_number"] = {"or": run_list}
        elif min_run and max_run:
            filter_dict["run_number"] = {"and": [{">=": min_run}, {"<=": max_run}]}
        else:
            raise ValueError("A list of runs or a minimum and maximum run should be specified")

        runs = rr.get_runs(filter=filter_dict)
        return [run["run_number"] for run in runs]

    def fetch_runs_that_need_update(self, run_list: list[int]) -> list[dict]:
        """
        Fetch all runs in the <run_list> in the Online RR Runs
        that the attribute 'runs_needs_to_be_updated_manually' is marked as True
        i.e., there is updates to be fetched from OMS
        """
        online_runs = rr.get_runs(filter={"run_needs_to_be_updated_manually": True, "run_number": {"or": run_list}})
        online_runs = [{"run_number": run["run_number"], "state": run["state"]} for run in online_runs]
        return sorted(online_runs, key=lambda x: ["run_number"])

    def count_offline_rr_lumis(self, run_number: int):
        joint_ranges = rr.get_lumisection_ranges(run_number, self.dataset_name)
        return joint_ranges[-1]["end"]

    def count_online_rr_lumis(self, run_number: int):
        joint_ranges = rr.get_lumisection_ranges(run_number, "online")
        return joint_ranges[-1]["end"]

    def count_oms_lumis(self, run_number: int):
        joint_ranges = rr.get_oms_lumisection_ranges(run_number)
        last_lumisection_number = 1
        for joint_range in joint_ranges:
            if joint_range["cms_active"]:
                last_lumisection_number = joint_range["end"]
        return joint_ranges[-1]["end"], last_lumisection_number

    def multi_count_offline_rr_lumis(self, run_list: list[int]):
        with ThreadPoolExecutor(max_workers=5) as executor:
            iterator = executor.map(self.count_offline_rr_lumis, run_list)
            results = list(iterator)
        return {run_list[idx]: results[idx] for idx in range(len(run_list))}

    def multi_count_online_rr_lumis(self, run_list: list[int]):
        with ThreadPoolExecutor(max_workers=5) as executor:
            iterator = executor.map(self.count_online_rr_lumis, run_list)
            results = list(iterator)
        return {run_list[idx]: results[idx] for idx in range(len(run_list))}

    def multi_count_oms_lumis(self, run_list: list[int]):
        with ThreadPoolExecutor(max_workers=5) as executor:
            iterator = executor.map(self.count_oms_lumis, run_list)
            results = list(iterator)
        return {
            run_list[idx]: {"total": results[idx][0], "last_cms_active_ls": results[idx][1]}
            for idx in range(len(run_list))
        }

    def multi_fetch_rr_oms_joint_lumis(self, run_list: list[int]):
        lumisections = []
        with ThreadPoolExecutor(max_workers=5) as executor:
            iterator = executor.map(rr.get_joint_lumisection_ranges, run_list, [self.dataset_name for _ in run_list])
            results = list(iterator)

        for run, joint_ranges in zip(run_list, results):
            for joint_range in joint_ranges:
                # Cleanup extra keys in rr lumis, since we only care about the status key
                for key, value in joint_range.items():
                    if isinstance(value, dict) and "status" in value.keys():
                        joint_range[key] = value["status"] == "GOOD"

                # Repeat the flags for the same range
                start_ls = joint_range.pop("start")
                end_ls = joint_range.pop("end")
                for ls_number in range(start_ls, end_ls + 1):
                    lumisections.append({"run_number": run, "ls_number": ls_number, **joint_range})

        return lumisections

    def fetch_rr_oms_joint_lumis(self, run_list: list[int]):
        lumisections = []
        for run in run_list:
            joint_ranges = rr.get_joint_lumisection_ranges(run, self.dataset_name)
            for joint_range in joint_ranges:
                # Cleanup extra keys in rr lumis, since we only care about the status key
                for key, value in joint_range.items():
                    if isinstance(value, dict) and "status" in value.keys():
                        joint_range[key] = value["status"] == "GOOD"

                # Repeat the flags for the same range
                start_ls = joint_range.pop("start")
                end_ls = joint_range.pop("end")
                for ls_number in range(start_ls, end_ls + 1):
                    lumisections.append({"run_number": run, "ls_number": ls_number, **joint_range})

        return lumisections

    def refresh_runs(self, runobj_list: list[dict]):
        """
        Given a list of runs, perform the following operations:
        1. Online: SIGNOFF the run if it is OPEN
        2. Online: OPEN the run
        3. Online: manually refresh components
        4. Online: SIGNOFF the run
        5. Offline: Move to OPEN (from WAITING DQM GUI) GLOBAL workspace
        """
        for run in runobj_list:
            current_state = run["state"]

            # If run is OPEN in online, sign it off first
            if run["state"] == "OPEN":
                rr.move_runs(run=run["run_number"], from_=run["state"], to_="SIGNOFF")
                current_state = "SIGNOFF"

            rr.move_runs(run=run["run_number"], from_=current_state, to_="OPEN")
            rr.manually_refresh_components_statuses_for_runs(runs=[run["run_number"]])
            rr.move_runs(run=run["run_number"], from_="OPEN", to_=current_state)
            rr.move_datasets("waiting dqm gui", "OPEN", self.dataset_name, workspace="global", run=run["run_number"])
