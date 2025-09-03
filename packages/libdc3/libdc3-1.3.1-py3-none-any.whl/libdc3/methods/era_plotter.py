import os

import matplotlib.pyplot as plt


class EraPlotter:
    def __init__(self, eras_statistics: list[dict], year: int, output_path: str):
        self.eras_statistics = eras_statistics
        self.year = year
        self.output_path = output_path
        self.__add_all_in()

    def __add_all_in(self):
        start_run = 9999999999999
        end_run = 0
        sum_lhc_delivered = 0.0
        sum_cms_recorded = 0.0
        sum_total_low_lumi = 0.0
        sum_total_ignore_runs = 0.0
        sum_total_not_stable_beams = 0.0
        sum_total_not_in_oms_rr = 0.0
        sum_dc_processed = 0.0
        sum_total_loss = 0.0
        sum_dc_certified = 0.0
        for stats in self.eras_statistics:
            start_run = min(start_run, stats["start_run"])
            end_run = max(end_run, stats["end_run"])
            sum_lhc_delivered += stats["lhc_delivered"]
            sum_cms_recorded += stats["cms_recorded"]
            sum_total_low_lumi += stats["total_low_lumi"]
            sum_total_ignore_runs += stats["total_ignore_runs"]
            sum_total_not_stable_beams += stats["total_not_stable_beams"]
            sum_total_not_in_oms_rr += stats["total_not_in_oms_rr"]
            sum_dc_processed += stats["dc_processed"]
            sum_total_loss += stats["total_loss"]
            sum_dc_certified += stats["dc_certified"]

        self.eras_statistics.append(
            {
                "era": "ALL IN",
                "start_run": start_run,
                "end_run": end_run,
                "lhc_delivered": sum_lhc_delivered,
                "cms_recorded": sum_cms_recorded,
                "total_low_lumi": sum_total_low_lumi,
                "total_ignore_runs": sum_total_ignore_runs,
                "total_not_stable_beams": sum_total_not_stable_beams,
                "total_not_in_oms_rr": sum_total_not_in_oms_rr,
                "dc_processed": sum_dc_processed,
                "total_loss": sum_total_loss,
                "dc_certified": sum_dc_certified,
                "processed_eff": sum_dc_certified / sum_dc_processed,
                "data_taking_eff": sum_cms_recorded / sum_lhc_delivered,
                "recorded_eff": sum_dc_certified / sum_cms_recorded,
            }
        )

    def plot_dc_efficiency_by_processed_per_era(self, save_pdf: bool = True):
        fig, ax = plt.subplots()

        for era in self.eras_statistics:
            percent_eff = 100 * era["processed_eff"]
            label = f"{era['era']} - {percent_eff:.1f}%"
            ax.bar(era["era"], percent_eff, label=label)

        # Format axis
        ax.set_ylabel("% DC Performance")
        ax.set_xlabel("ERAS")
        ax.set_ylim((0, 100))
        ax.set_title(f"{self.year} Performance of Data Certification per ERA")
        ax.tick_params(axis="x", rotation=30)
        ax.legend(scatterpoints=1, loc="lower left", ncol=2, fontsize=8)

        # Fix layout
        fig.tight_layout()

        # Save fig
        outpath = os.path.join(self.output_path, "dc_efficiency_by_processed_per_era.png")
        fig.savefig(outpath, dpi=300)

        if save_pdf:
            outpath = os.path.join(self.output_path, "dc_efficiency_by_processed_per_era.pdf")
            fig.savefig(outpath, format="pdf")

        # Close fig
        plt.close()

    def plot_dc_efficiency_by_recorded_per_era(self, save_pdf: bool = False):
        fig, ax = plt.subplots()

        for era in self.eras_statistics:
            percent_eff = 100 * era["recorded_eff"]
            label = f"{era['era']} - {percent_eff:.1f}%"
            ax.bar(era["era"], percent_eff, label=label)

        # Format axis
        ax.set_ylabel("% DC Performance")
        ax.set_xlabel("ERAS")
        ax.set_ylim((0, 100))
        ax.set_title(f"{self.year} Fraction of Recorded Data for Physics Analysis per ERA")
        ax.tick_params(axis="x", rotation=30)
        ax.legend(scatterpoints=1, loc="lower left", ncol=2, fontsize=8)

        # Fix layout
        fig.tight_layout()

        # Save fig
        outpath = os.path.join(self.output_path, "dc_efficiency_by_recorded_per_era.png")
        fig.savefig(outpath, dpi=300)

        if save_pdf:
            outpath = os.path.join(self.output_path, "dc_efficiency_by_recorded_per_era.pdf")
            fig.savefig(outpath, format="pdf")

        # Close fig
        plt.close()
