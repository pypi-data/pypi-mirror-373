import os
from datetime import datetime, timedelta
from importlib import resources
from itertools import groupby
from pathlib import Path
from typing import Optional, cast

import matplotlib.figure
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.dates import AutoDateLocator, DateFormatter
from matplotlib.font_manager import FontProperties
from matplotlib.offsetbox import AnnotationBbox, OffsetImage
from PIL import Image

from .. import assets
from ..labels import LATEX_UNITS, PARTICLE_TYPES, SQRT_S
from ..units import UNIT_PREFIXES
from ..utils import flatten_ranges


class AccLuminosityAnalyzer:
    FONT_PROPS_SUPTITLE = FontProperties(size="x-large", weight="bold", stretch="condensed")
    FONT_PROPS_TITLE = FontProperties(size="large", weight="regular")
    FONT_PROPS_AX_TITLE = FontProperties(size="x-large", weight="bold")
    FONT_PROPS_TICK_LABEL = FontProperties(size="large", weight="bold")
    DATE_FMT_STR_AXES = "%-b %d"

    # This is needed to generate PDFs without edge stripes between the bars.
    # The bar width will grow only at the lower and upper limits, i.e. first and last bars
    # consequently the middle of the plot is not affected at all, and since the
    # we are growing the original bin width of 1 day by 2.4 hours the first and last bars
    # have a very small impact.
    # If we are plotting 2 bars or 3 bars, it is easy to spot that the last bar is bigger,
    # however 4+ bars the difference becomes unoticible.
    MAGIC_OFFSET = 1.1

    # Mypy is not sure if resources.files will fully resolve to Path during runtime, so it infers it as Traversable.
    # However, we are sure that this is Path. Since, this path exists in the filesystem and is part of the git repository.
    ASSETS_TRAVERSABLE: Path = cast(Path, resources.files(assets))

    # CMS logo magic numbers
    CMS_LOGO_ZOOM = 0.8
    CMS_LOGO_XY_OFFSET = (2.0, -3.0)

    def __init__(
        self,
        dc_json: dict,
        bril_lumis: list[dict],
        bril_unit: str,
        bril_amodetag: str,
        year: int,
        plot_energy_label: str,
        output_path: str,
        target_unit: Optional[str] = None,
        additional_label_on_plot: Optional[str] = None,
    ):
        self.dc_json = dc_json
        self.bril_unit = bril_unit
        self.bril_amodetag = bril_amodetag
        self.target_unit = target_unit
        self.year = year
        self.plot_energy_label = (
            plot_energy_label  # This is something like "13.6 TeV" or "0.9 GeV" or "5.36 TeV/nucleon"
        )
        self.additional_label_on_plot = additional_label_on_plot
        self.output_path = output_path

        lumis = self.__preprocess_lumis(bril_lumis)
        self.particle_type = PARTICLE_TYPES[bril_amodetag]
        self.sqrt_s = SQRT_S[bril_amodetag]
        self.unit_label = LATEX_UNITS[target_unit or bril_unit]
        self.min_datetime = lumis[0]["datetime"]
        self.max_datetime = lumis[-1]["datetime"]
        self.data_by_day = self.agg_and_cumsum(lumis, "date")
        self.data_by_day["entries"] = self.ffill_missing_values(
            self.data_by_day["entries"], key_offset=timedelta(days=1)
        )
        self.data_by_week = self.agg_and_cumsum(lumis, "week")
        self.data_by_week["entries"] = self.ffill_missing_values(self.data_by_week["entries"], key_offset=1)

    @staticmethod
    def agg_and_cumsum(data, agg_key):
        agg_entries = []
        total_delivered = 0
        total_recorded = 0
        total_certified = 0
        groups = groupby(data, key=lambda x: x[agg_key])
        for group_key, group_items in groups:
            for item in group_items:
                total_delivered += item["delivered"]
                total_recorded += item["recorded"]
                if item["is_good"]:
                    total_certified += item["recorded"]
            agg_entries.append(
                {
                    "group_key": group_key,
                    "delivered_cumsum": total_delivered,
                    "recorded_cumsum": total_recorded,
                    "certified_cumsum": total_certified,
                }
            )

        return {
            "entries": agg_entries,
            "total_delivered": total_delivered,
            "total_recorded": total_recorded,
            "total_certified": total_certified,
        }

    @staticmethod
    def ffill_missing_values(data, key_offset):
        start_key = data[0]["group_key"]
        end_key = data[-1]["group_key"]

        filled_data = []
        current_index = 0
        last_known_values = data[0].copy()

        current = start_key
        while current <= end_key:
            if current_index < len(data) and current == data[current_index]["group_key"]:
                last_known_values = data[current_index]
                current_index += 1

            filled_data.append(
                {
                    "group_key": current,
                    "delivered_cumsum": last_known_values["delivered_cumsum"],
                    "recorded_cumsum": last_known_values["recorded_cumsum"],
                    "certified_cumsum": last_known_values["certified_cumsum"],
                }
            )

            current += key_offset

        return filled_data

    def __preprocess_lumis(self, bril_lumis: list[dict]):
        """
        Pre-process all run|ls|lumi entries and create a `bad_lumis` list
        with only lumiloss entries
        """
        lumis = []
        expanded_json = {
            run_number: list(flatten_ranges(lumi_ranges)) for run_number, lumi_ranges in self.dc_json.items()
        }

        if self.target_unit:
            bril_factor = 1 / UNIT_PREFIXES[self.bril_unit]
            target_factor = UNIT_PREFIXES[self.target_unit]
            convert_factor = bril_factor * target_factor
        else:
            convert_factor = 1

        for lumi in bril_lumis:
            run_number = lumi["run_number"]
            ls_number = lumi["ls_number"]
            good_lumisections = expanded_json.get(run_number, [])
            lumis.append(
                {
                    "datetime": lumi["datetime"],
                    "date": datetime.strptime(lumi["datetime"].strftime("%Y%m%d"), "%Y%m%d"),
                    "week": lumi["datetime"].isocalendar()[1],
                    "delivered": lumi["delivered"] * convert_factor,
                    "recorded": lumi["recorded"] * convert_factor,
                    "is_good": ls_number in good_lumisections,
                }
            )

        return sorted(lumis, key=lambda x: x["datetime"])

    def plot_acc_lumi_by_day(self, save_pdf: bool = False):
        bins = [entry["group_key"] for entry in self.data_by_day["entries"]]
        min_date = min(bins)
        max_date = max(bins)
        num_days = (max_date - min_date).days if len(bins) > 1 else 1
        bin_width = (bins[1] - bins[0]) if len(bins) > 1 else timedelta(days=0.5)
        padding = bin_width / 2

        # Create a fig and ax
        fig = plt.figure(figsize=(8.0, 6.0))
        ax = fig.add_subplot()

        # Plot stacked histogram
        total_delivered_fmt = "{0:.2f}".format(self.data_by_day["total_delivered"])  # noqa: UP030
        total_recorded_fmt = "{0:.2f}".format(self.data_by_day["total_recorded"])  # noqa: UP030
        total_certified_fmt = "{0:.2f}".format(self.data_by_day["total_certified"])  # noqa: UP030

        ax.bar(
            bins,
            [entry["delivered_cumsum"] for entry in self.data_by_day["entries"]],
            label=f"LHC Delivered: {total_delivered_fmt} {self.unit_label}",
            color=(0.0 / 255.0, 152.0 / 255.0, 212.0 / 255.0),
            width=bin_width * self.MAGIC_OFFSET,  # type: ignore[arg-type]
        )
        ax.bar(
            bins,
            [entry["recorded_cumsum"] for entry in self.data_by_day["entries"]],
            label=f"CMS Recorded: {total_recorded_fmt} {self.unit_label}",
            color=(241.0 / 255.0, 194.0 / 255.0, 40.0 / 255.0),
            width=bin_width * self.MAGIC_OFFSET,  # type: ignore[arg-type]
        )
        ax.bar(
            bins,
            [entry["certified_cumsum"] for entry in self.data_by_day["entries"]],
            label=f"CMS Certified: {total_certified_fmt} {self.unit_label}",
            color=(255.0 / 255.0, 235.0 / 255.0, 215.0 / 255.0),
            width=bin_width * self.MAGIC_OFFSET,  # type: ignore[arg-type]
        )

        # Add labels and title
        ax.set_xlabel("Date (UTC)", fontproperties=self.FONT_PROPS_AX_TITLE)
        ax.set_ylabel(f"Total Integrated Luminosity ({self.unit_label})", fontproperties=self.FONT_PROPS_AX_TITLE)
        ax.set_title(
            f"Date included from {self.min_datetime} to {self.max_datetime} UTC\n", fontproperties=self.FONT_PROPS_TITLE
        )
        leg = ax.legend(loc="upper left", bbox_to_anchor=(0.125, 0.0, 1.0, 1.01), frameon=False)
        for t in leg.get_texts():
            t.set_fontproperties(self.FONT_PROPS_TICK_LABEL)

        # Adjust x-axis limits to give some space around the bars
        ax.set_xlim(min_date - padding, max_date + padding)
        ax.tick_params(axis="x", rotation=30, direction="in")
        ax.tick_params(axis="y", direction="in")

        # Patch the number of ticks in the x-axis and apply font props
        if (max_date - min_date) < timedelta(days=1):
            locator = AutoDateLocator(minticks=1, maxticks=2)
            formatter = DateFormatter(self.DATE_FMT_STR_AXES)
        else:
            min_num_ticks = min(num_days, 5)
            max_num_ticks = min(num_days, 20)
            locator = AutoDateLocator(minticks=min_num_ticks, maxticks=max_num_ticks)
            formatter = DateFormatter(self.DATE_FMT_STR_AXES)

        ax.xaxis.set_major_locator(locator)
        ax.xaxis.set_major_formatter(formatter)
        for tick in ax.get_xticklabels():
            tick.set_fontproperties(self.FONT_PROPS_TICK_LABEL)

        # Format y axis ticks and limits
        y_ticks = ax.get_yticks()
        min_y = y_ticks.min()
        max_y = y_ticks.max()
        ax.set_ylim(min_y, max_y)
        for tick in ax.get_yticklabels():
            tick.set_fontproperties(self.FONT_PROPS_TICK_LABEL)

        # Add plot label to the plot
        if self.additional_label_on_plot:
            ax.text(
                0.02,
                0.7,
                self.additional_label_on_plot,
                verticalalignment="center",
                horizontalalignment="left",
                transform=ax.transAxes,
                color="red",
                fontsize=15,
            )

        # Create a secondary y-axis on the right
        ax2 = ax.twinx()
        ax2.set_ylim(ax.get_ylim())
        ax2.tick_params(axis="y", direction="in")
        for tick in ax2.get_yticklabels():
            tick.set_fontproperties(self.FONT_PROPS_TICK_LABEL)

        # Create a secondary x-axis on the top
        ax3 = ax.twiny()
        ax3.set_xlim(ax.get_xlim())
        ax3.tick_params(axis="x", direction="in")
        ax3.xaxis.set_major_locator(locator)
        ax3.set_xticklabels([])

        # Update fig
        suptitle = (
            f"CMS Integrated Luminosity, {self.particle_type}, {self.year}, {self.sqrt_s} {self.plot_energy_label}"
        )
        fig.suptitle(suptitle).set_fontproperties(self.FONT_PROPS_SUPTITLE)
        fig.subplots_adjust(top=0.85, bottom=0.14, left=0.13, right=0.91)

        # Load the logo image
        logo_img_path = self.ASSETS_TRAVERSABLE / "cms_logo.png"
        logo_data = Image.open(logo_img_path)

        # Add the logo
        ax_fig = ax.get_figure()
        if isinstance(ax_fig, matplotlib.figure.Figure):
            fig_dpi = ax_fig.dpi
            fig_size = ax_fig.get_size_inches()
        else:
            raise TypeError("Expected a matplotlib.figure.Figure from ax.get_figure(), got something else.")

        img_arr = np.array(logo_data)  # where `image` is your ImageFile
        zoom_factor = 0.1 / 1.2 * fig_dpi * fig_size[0] / img_arr.shape[0]
        zoom_factor *= self.CMS_LOGO_ZOOM
        logo_box = OffsetImage(img_arr, zoom=zoom_factor)
        ann_box = AnnotationBbox(
            logo_box,
            (0.0, 1.0),
            xybox=self.CMS_LOGO_XY_OFFSET,
            xycoords="axes fraction",
            boxcoords="offset points",
            box_alignment=(0.0, 1.0),
            pad=0.0,
            frameon=False,
        )
        ax.add_artist(ann_box)

        # Save fig
        outpath = os.path.join(self.output_path, "acc_integrated_luminosity_per_day.png")
        fig.savefig(outpath, dpi=300)

        if save_pdf:
            outpath = os.path.join(self.output_path, "acc_integrated_luminosity_per_day.pdf")
            fig.savefig(outpath, dpi=300, format="pdf")

        # Close the fig
        plt.close(fig)

    def plot_acc_lumi_by_week(self, save_pdf: bool = False):
        bins = [entry["group_key"] for entry in self.data_by_week["entries"]]
        min_week = min(bins)
        max_week = max(bins)
        num_weeks = (max_week - min_week) if len(bins) > 1 else 1
        bin_width = (bins[1] - bins[0]) if len(bins) > 1 else 0.5
        padding = bin_width / 2

        # Create a fig and ax
        fig = plt.figure(figsize=(8.0, 6.0))
        ax = fig.add_subplot()

        # Plot stacked histogram
        total_delivered_fmt = "{0:.2f}".format(self.data_by_week["total_delivered"])  # noqa: UP030
        total_recorded_fmt = "{0:.2f}".format(self.data_by_week["total_recorded"])  # noqa: UP030
        total_certified_fmt = "{0:.2f}".format(self.data_by_week["total_certified"])  # noqa: UP030

        ax.bar(
            bins,
            [entry["delivered_cumsum"] for entry in self.data_by_week["entries"]],
            label=f"LHC Delivered: {total_delivered_fmt} {self.unit_label}",
            color=(0.0 / 255.0, 152.0 / 255.0, 212.0 / 255.0),
            width=bin_width * self.MAGIC_OFFSET,
        )
        ax.bar(
            bins,
            [entry["recorded_cumsum"] for entry in self.data_by_week["entries"]],
            label=f"CMS Recorded: {total_recorded_fmt} {self.unit_label}",
            color=(241.0 / 255.0, 194.0 / 255.0, 40.0 / 255.0),
            width=bin_width * self.MAGIC_OFFSET,
        )
        ax.bar(
            bins,
            [entry["certified_cumsum"] for entry in self.data_by_week["entries"]],
            label=f"CMS Certified: {total_certified_fmt} {self.unit_label}",
            color=(255.0 / 255.0, 235.0 / 255.0, 215.0 / 255.0),
            width=bin_width * self.MAGIC_OFFSET,
        )

        # Add labels and title
        ax.set_xlabel("Week number", fontproperties=self.FONT_PROPS_AX_TITLE)
        ax.set_ylabel(f"Total Integrated Luminosity ({self.unit_label})", fontproperties=self.FONT_PROPS_AX_TITLE)
        ax.set_title(
            f"Date included from {self.min_datetime} to {self.max_datetime} UTC\n", fontproperties=self.FONT_PROPS_TITLE
        )
        leg = ax.legend(loc="upper left", bbox_to_anchor=(0.125, 0.0, 1.0, 1.01), frameon=False)
        for t in leg.get_texts():
            t.set_fontproperties(self.FONT_PROPS_TICK_LABEL)

        # Adjust x-axis limits to give some space around the bars
        ax.set_xlim(min_week - padding, max_week + padding)
        ax.tick_params(axis="x", rotation=30, direction="in")
        ax.tick_params(axis="y", direction="in")

        # # Patch the number of ticks in the x-axis and apply font props
        if num_weeks == 1:
            locator = AutoDateLocator(minticks=1, maxticks=2)
        else:
            min_num_ticks = min(num_weeks, 5)
            max_num_ticks = min(num_weeks, 20)
            locator = AutoDateLocator(minticks=min_num_ticks, maxticks=max_num_ticks)

        ax.xaxis.set_major_locator(locator)
        for tick in ax.get_xticklabels():
            tick.set_fontproperties(self.FONT_PROPS_TICK_LABEL)

        # Format y axis ticks and limits
        y_ticks = ax.get_yticks()
        min_y = y_ticks.min()
        max_y = y_ticks.max()
        ax.set_ylim(min_y, max_y)
        for tick in ax.get_yticklabels():
            tick.set_fontproperties(self.FONT_PROPS_TICK_LABEL)

        # Add plot label to the plot
        if self.additional_label_on_plot:
            ax.text(
                0.02,
                0.7,
                self.additional_label_on_plot,
                verticalalignment="center",
                horizontalalignment="left",
                transform=ax.transAxes,
                color="red",
                fontsize=15,
            )

        # Create a secondary y-axis on the right
        ax2 = ax.twinx()
        ax2.set_ylim(ax.get_ylim())
        ax2.tick_params(axis="y", direction="in")
        for tick in ax2.get_yticklabels():
            tick.set_fontproperties(self.FONT_PROPS_TICK_LABEL)

        # Create a secondary x-axis on the top
        ax3 = ax.twiny()
        ax3.set_xlim(ax.get_xlim())
        ax3.tick_params(axis="x", direction="in")
        ax3.xaxis.set_major_locator(locator)
        ax3.set_xticklabels([])

        # Update fig
        suptitle = (
            f"CMS Integrated Luminosity, {self.particle_type}, {self.year}, {self.sqrt_s} {self.plot_energy_label}"
        )
        fig.suptitle(suptitle).set_fontproperties(self.FONT_PROPS_SUPTITLE)
        fig.subplots_adjust(top=0.85, bottom=0.14, left=0.13, right=0.91)

        # Load the logo image
        logo_img_path = self.ASSETS_TRAVERSABLE / "cms_logo.png"
        logo_data = Image.open(logo_img_path)

        # Add the logo
        ax_fig = ax.get_figure()
        if isinstance(ax_fig, matplotlib.figure.Figure):
            fig_dpi = ax_fig.dpi
            fig_size = ax_fig.get_size_inches()
        else:
            raise TypeError("Expected a matplotlib.figure.Figure from ax.get_figure(), got something else.")

        img_arr = np.array(logo_data)  # where `image` is your ImageFile
        zoom_factor = 0.1 / 1.2 * fig_dpi * fig_size[0] / img_arr.shape[0]
        zoom_factor *= self.CMS_LOGO_ZOOM
        logo_box = OffsetImage(img_arr, zoom=zoom_factor)
        ann_box = AnnotationBbox(
            logo_box,
            (0.0, 1.0),
            xybox=self.CMS_LOGO_XY_OFFSET,
            xycoords="axes fraction",
            boxcoords="offset points",
            box_alignment=(0.0, 1.0),
            pad=0.0,
            frameon=False,
        )
        ax.add_artist(ann_box)

        # Save fig
        outpath = os.path.join(self.output_path, "acc_integrated_luminosity_per_week.png")
        fig.savefig(outpath, dpi=300)

        if save_pdf:
            outpath = os.path.join(self.output_path, "acc_integrated_luminosity_per_week.pdf")
            fig.savefig(outpath, dpi=300, format="pdf")

        # Close the fig
        plt.close(fig)
