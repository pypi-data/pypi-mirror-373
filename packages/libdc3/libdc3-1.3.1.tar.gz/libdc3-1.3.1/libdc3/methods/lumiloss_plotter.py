import os
from typing import Optional

import matplotlib.pyplot as plt


class LumilossPlotter:
    def __init__(self, lumiloss: dict, unit: str, output_path: str):
        self.output_path = output_path
        self.unit = unit
        self.dcs_loss = self.sort_by_values(self.gt_thr(lumiloss["dcs_loss"], 0))
        self.subsystems_loss = self.sort_by_values(self.gt_thr(lumiloss["subsystems_loss"], 0))
        self.cms_inclusive_loss = self.sort_by_values(self.gt_thr(lumiloss["cms_inclusive_loss"], 0))
        self.cms_exclusive_loss = self.sort_by_values(self.gte_thr(lumiloss["cms_exclusive_loss"], 1e-3))
        self.cms_frac_exclusive_loss = self.sort_by_values(self.gte_thr(lumiloss["cms_frac_exclusive_loss"], 1e-2))
        self.cms_detailed_frac_exclusive_loss = self.sort_by_values(
            self.gte_thr(lumiloss["cms_detailed_frac_exclusive_loss"], 1.0)
        )
        self.detector_inclusive_loss = {
            key: self.sort_by_values(value) for key, value in lumiloss["detector_inclusive_loss"].items()
        }
        self.detector_exclusive_loss = {
            key: self.sort_by_values(value) for key, value in lumiloss["detector_exclusive_loss"].items()
        }

    @staticmethod
    def gt_thr(input_dict: dict, thr: float):
        return {key: value for key, value in input_dict.items() if value > thr}

    @staticmethod
    def gte_thr(input_dict: dict, thr: float):
        return {key: value for key, value in input_dict.items() if value >= thr}

    @staticmethod
    def sort_by_values(input_dict: dict):
        return dict(sorted(input_dict.items(), key=lambda x: x[1]))

    @staticmethod
    def bar_plot(
        data: dict,
        title: str,
        xlabel: str,
        ylabel: str,
        save_path: str,
        fontsize: int = 10,
        labelsize: int = 14,
        tick_params: bool = False,
        save_pdf: bool = False,
        save_path_pdf: Optional[str] = None,
    ):
        x_array = list(data.keys())
        y_array = list(data.values())
        if tick_params:
            plt.tick_params(axis="both", which="major", labelsize=labelsize)
        plt.barh(x_array, y_array)
        plt.title(title, fontsize=fontsize)
        plt.xlabel(xlabel, fontsize=fontsize)
        plt.ylabel(ylabel, fontsize=fontsize)
        plt.savefig(save_path, dpi=300, bbox_inches="tight")

        if save_pdf:
            plt.savefig(save_path_pdf, bbox_inches="tight", format="pdf")

        plt.close()

    def plot_subsystem_dqmflag_loss(self, save_pdf: bool = False):
        base_path = os.path.join(self.output_path, "Subsystem")
        os.makedirs(base_path, exist_ok=True)
        outpath = os.path.join(base_path, "dqmflags_loss.png")
        self.bar_plot(
            self.subsystems_loss,
            "DQM Flags vs. Inclusive Loss",
            f"Luminosity Loss ({self.unit})",
            "DQM Flag",
            outpath,
            save_pdf=save_pdf,
            save_path_pdf=os.path.join(base_path, "dqmflags_loss.pdf") if save_pdf else None,
        )

    def plot_dcs_loss(self, save_pdf: bool = False):
        base_path = os.path.join(self.output_path, "DCS")
        os.makedirs(base_path, exist_ok=True)
        outpath = os.path.join(base_path, "dcsflags_loss.png")
        self.bar_plot(
            self.dcs_loss,
            "DCS Bits vs. Inclusive Loss",
            f"Luminosity Loss ({self.unit})",
            "DCS Bit",
            outpath,
            save_pdf=save_pdf,
            save_path_pdf=os.path.join(base_path, "dcsflags_loss.pdf") if save_pdf else None,
        )

    def plot_cms_inclusive_loss(self, save_pdf: bool = False):
        base_path = os.path.join(self.output_path, "CMS")
        os.makedirs(base_path, exist_ok=True)
        outpath = os.path.join(base_path, "inclusive_loss.png")
        self.bar_plot(
            self.cms_inclusive_loss,
            "Inclusive Loss from each CMS Subsystem",
            f"Luminosity Loss ({self.unit})",
            "Subsystem",
            outpath,
            save_pdf=save_pdf,
            save_path_pdf=os.path.join(base_path, "inclusive_loss.pdf") if save_pdf else None,
        )

    def plot_cms_exclusive_loss(self, save_pdf: bool = False):
        base_path = os.path.join(self.output_path, "CMS")
        os.makedirs(base_path, exist_ok=True)
        outpath = os.path.join(base_path, "exclusive_loss.png")
        self.bar_plot(
            self.cms_exclusive_loss,
            "Exclusive Loss from Each Category",
            f"Luminosity Loss ({self.unit})",
            "Subsystem",
            outpath,
            fontsize=10 if len(self.cms_exclusive_loss) <= 12 else 6,
            save_pdf=save_pdf,
            save_path_pdf=os.path.join(base_path, "exclusive_loss.pdf") if save_pdf else None,
        )

    def plot_cms_detailed_fraction_exclusive_loss(self, save_pdf: bool = False):
        base_path = os.path.join(self.output_path, "CMS")
        os.makedirs(base_path, exist_ok=True)
        outpath = os.path.join(base_path, "detailed_fraction_exclusive_loss.png")
        self.bar_plot(
            self.cms_detailed_frac_exclusive_loss,
            "Fraction of Exclusive Loss from Each Category",
            f"Luminosity Loss ({self.unit})",
            "Percentage %",
            outpath,
            save_pdf=save_pdf,
            save_path_pdf=os.path.join(base_path, "detailed_fraction_exclusive_loss.pdf") if save_pdf else None,
        )

    def plot_inclusive_loss_by_subdetector(self, save_pdf: bool = False):
        for subdetector, inclusive_loss in self.detector_inclusive_loss.items():
            base_path = os.path.join(self.output_path, f"Subdetector/{subdetector}")
            os.makedirs(base_path, exist_ok=True)
            outpath = os.path.join(base_path, "inclusive_loss.png")
            self.bar_plot(
                inclusive_loss,
                f"Inclusive Loss of {subdetector} System",
                f"Luminosity Loss ({self.unit})",
                "Component",
                outpath,
                save_pdf=save_pdf,
                save_path_pdf=os.path.join(base_path, "inclusive_loss.pdf") if save_pdf else None,
            )

    def plot_exclusive_loss_by_subdetector(self, save_pdf: bool = False):
        for subdetector, exclusive_loss in self.detector_exclusive_loss.items():
            base_path = os.path.join(self.output_path, f"Subdetector/{subdetector}")
            os.makedirs(base_path, exist_ok=True)
            outpath = os.path.join(base_path, "exclusive_loss.png")
            self.bar_plot(
                exclusive_loss,
                f"Exclusive Loss of {subdetector} System",
                f"Luminosity Loss ({self.unit})",
                "Component",
                outpath,
                save_pdf=save_pdf,
                save_path_pdf=os.path.join(base_path, "exclusive_loss.pdf") if save_pdf else None,
            )

    def plot_fraction_of_exclusive_loss_by_subdetector(self, save_pdf: bool = False):
        base_path = os.path.join(self.output_path, "CMS")
        os.makedirs(base_path, exist_ok=True)
        outpath = os.path.join(base_path, "pie_chat_exclusive_loss.png")
        data = list(self.cms_frac_exclusive_loss.values())
        labels = list(self.cms_frac_exclusive_loss.keys())

        # Styling
        explode = [0.01 + idx * 0.01 for idx in range(len(labels))]
        colors = [
            "purple",
            "plum",
            "red",
            "pink",
            "green",
            "orange",
            "yellow",
            "blue",
            "pink",
            "orchid",
            "goldenrod",
            "gray",
            "olive",
        ]
        colors_dict = {icms: colors[idx] for idx, icms in enumerate(self.detector_inclusive_loss)}
        colors_dict["Mixed"] = "brown"

        plt.pie(
            data,
            labels=labels,
            autopct="%1.1f%%",
            explode=explode,
            normalize=True,
            colors=[colors_dict[key] for key in labels],
        )
        plt.title("Fraction of Exclusive Loss from Each Category", fontsize=10)
        plt.savefig(outpath, dpi=300, bbox_inches="tight")

        if save_pdf:
            outpath = os.path.join(base_path, "pie_chat_exclusive_loss.pdf")
            plt.savefig(outpath, bbox_inches="tight", format="pdf")

        plt.close()
