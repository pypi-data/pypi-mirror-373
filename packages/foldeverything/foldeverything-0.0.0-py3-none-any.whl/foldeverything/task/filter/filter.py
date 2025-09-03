from typing import Dict
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import shutil
from tqdm import tqdm
from matplotlib.backends.backend_pdf import PdfPages
import pandas as pd
from pathlib import Path
from Bio import Align
import numpy as np
import random
from tqdm.auto import tqdm
import time

from foldeverything.task.filter.seqplot_utils import (
    aa_composition_pie,
    cdr_logo,
    create_alignment_logo,
    plot_seq_liabilities,
)
from foldeverything.task.task import Task
from foldeverything.task.analyze.analyze import SEVERITY, compute_liability_scores


class Filter(Task):
    """
    Fast post-hoc selector that turns a directory of designs (+ metrics)
    into a ranked subset.

    metrics_override: key,value pairs where key is the metric to override and value is the value to override with. If value==None that metric is removed.
    For example:
        metrics_override = {"plip_hbonds": 1, "plip_saltbridge": 1, "delta_sasa_original": None}
    """

    def __init__(
        self,
        name: str,
        outname: str,
        outdir: str,
        design_dir: str,
        write_output: bool = True,
        write_only_top_designs: bool = True,
        budget: int = 100,
        use_affinity: bool = False,  # This changes the filtering metrics to metrics more amenable to small molecule binder design
        filter_cysteins: bool = True,  # This filters out all designs that have designed cysteins in them (prespecified cysteins in the design are not counted)
        from_inverse_folded: bool = False,  # This makes it so that we use the backbone refolding rmsd instead of the all-atom RMSD
        filter_rmsd_design: bool = True,  # We usually want this True for peptides
        filter_bindingsite: bool = False,  # This filters out everything that does not have a residue within 4A of a binding site residue
        modality: str = "peptide",  # peptide, antibody
        peptide_type: str = "linear",  # linear, cyclic
        div_budget: int = 30,
        alpha: float = 0.2,  # 0 = quality-only, 1 = diversity-only
        random_state: int = 0,
        metrics_override: Dict = None,  # overrides metrics, None values delete keys
        tim_mode: bool = False,
        num_liability_plots: int = 20,
        plot_seq_logos: bool = True,  # make sequence logo diagrams of designed sequence
    ):
        super().__init__()
        assert modality in ["peptide", "antibody"]
        assert peptide_type in ["linear", "cyclic"]
        self.name = name
        self.outname = outname
        self.design_dir = Path(design_dir)
        self.write_output = write_output
        self.write_only_top_designs = write_only_top_designs
        self.budget = budget
        self.use_affinity = use_affinity
        self.filter_cysteins = filter_cysteins
        self.from_inverse_folded = from_inverse_folded
        self.filter_rmsd_design = filter_rmsd_design
        self.filter_bindingsite = filter_bindingsite
        self.modality = modality
        self.peptide_type = peptide_type
        self.div_budget = div_budget
        self.alpha = alpha
        self.random_state = random_state
        self.tim_mode = tim_mode
        self.num_liability_plots = num_liability_plots
        self.plot_seq_logos = plot_seq_logos

        self.outdir = Path(f"{outdir}") / f"{outname}"
        self.top_dir = self.outdir / f"top_{budget}_designs"
        self.div_dir = self.outdir / f"diverse_{div_budget}_designs"
        self.outdir.mkdir(parents=True, exist_ok=True)
        self.top_dir.mkdir(parents=True, exist_ok=True)
        self.div_dir.mkdir(parents=True, exist_ok=True)

        # we want to maximize all these metrics
        self.metrics: dict = {
            "design_iptm": 1,
            "design_ptm": 1,
            "neg_min_interaction_pae": 1,
            "plip_hbonds" + ("_refolded" if from_inverse_folded else ""): 2,
            "plip_saltbridge" + ("_refolded" if from_inverse_folded else ""): 2,
            "delta_sasa_refolded" if from_inverse_folded else "delta_sasa_original": 2,
        }
        if use_affinity:
            self.metrics: dict = {
                "design_iptm": 1.1,
                "design_ptm": 1.1,
                "neg_min_interaction_pae": 1.1,
                "affinity_probability_binary1": 1,
                "plip_hbonds" + ("_refolded" if from_inverse_folded else ""): 2,
                "plip_saltbridge" + ("_refolded" if from_inverse_folded else ""): 2,
                "delta_sasa_refolded"
                if from_inverse_folded
                else "delta_sasa_original": 2,
            }
        # override metrics
        if not metrics_override is None:
            for k in metrics_override:
                if not k in self.metrics:
                    raise ValueError(
                        f"Trying to override metric {k} not found in metrics"
                    )
                if metrics_override[k] is None:
                    del self.metrics[k]
                else:
                    self.metrics[k] = metrics_override[k]

        # Define how to sort. 1
        self.sorting_criteria = [
            {"feature": "has_x", "lower_is_better": True, "importance": 20},
            {"feature": "rmsd<2.5", "lower_is_better": False, "importance": 7},
            {"feature": "secondary_rank", "lower_is_better": True, "importance": 5},
            {"feature": "design_iptm", "lower_is_better": False, "importance": 0},
        ]
        if filter_bindingsite:
            self.sorting_criteria.append(
                {
                    "feature": "bindsite_under_4rmsd",
                    "lower_is_better": False,
                    "importance": 10,
                },
            )
        if filter_cysteins:
            self.sorting_criteria.append(
                {
                    "feature": "no_CYS",
                    "lower_is_better": False,
                    "importance": 15,
                },
            )
        if filter_rmsd_design:
            self.sorting_criteria.append(
                {
                    "feature": "rmsd_design<2.5",
                    "lower_is_better": False,
                    "importance": 6,
                },
            )

        random.seed(self.random_state)
        np.random.seed(self.random_state)

    def run(self, jupyter_nb=False):
        self.load_dataframe()
        self.reset_outdir()
        self.sort_df()
        self.optimize_diversity()
        self.write_outdir()

        # Visualizations
        hist_metrics, extra_pairs, row_headers, rows, metric_rows, text = (
            self.prepare_visualization()
        )

        self.make_visualization(
            hist_metrics,
            extra_pairs,
            row_headers,
            rows,
            metric_rows,
            text,
            jupyter_nb=jupyter_nb,
        )

    def reset_outdir(self):
        if self.outdir.exists():
            shutil.rmtree(self.outdir)
        self.outdir.mkdir(parents=True, exist_ok=True)
        self.top_dir.mkdir(parents=True, exist_ok=True)
        self.div_dir.mkdir(parents=True, exist_ok=True)

    def load_dataframe(self):
        if self.tim_mode:
            df_in = pd.read_csv(self.design_dir / f"aggregate_metrics_eval_design.csv")
        else:
            df_in = pd.read_csv(self.design_dir / f"aggregate_metrics_{self.name}.csv")
        df_in = pd.read_csv(self.design_dir / f"aggregate_metrics_{self.name}.csv")
        self.df_in = df_in.copy()
        df = df_in.copy()

        if self.from_inverse_folded:
            df["rmsd<2.5"] = df["bb_rmsd"] < 2.5
            df["rmsd_design<2.5"] = df["bb_rmsd_design"] < 2.5
        else:
            df["rmsd_design<2.5"] = df["rmsd_design"] < 2.5

        df["neg_rmsd_design"] = -df["rmsd_design"]
        df["neg_min_interaction_pae"] = -df["min_interaction_pae"]
        self.df = df

        print(
            f"""
            Total: {len(self.df):>5} 
            Complex RMSD<2.5: {self.df["rmsd<2.5"].sum():>5} 
            Design RMSD<2.5: {self.df["rmsd_design<2.5"].sum():>5} 
            pTM>0.8: {(self.df["design_ptm"] > 0.8).sum():>5} 
            RMSD<2.5 & pTM>0.8: {((self.df["rmsd<2.5"]) & (self.df["design_ptm"] > 0.8)).sum():>5}
            """
        )

    def sort_df(self):
        rank_df = pd.DataFrame(index=self.df.index)

        # 1. For each row, compute its rank according to each metric
        # Scale the ranks by importance (divide by inverse_importance)
        for col, inverse_importance in self.metrics.items():
            if self.metrics[col] is None:
                continue
            rank_df[col] = (
                self.df[col].rank(method="min", ascending=False) / inverse_importance
            )

        # 2. For each row, find the max (worst) rank across the metrics.
        # This single value determines its final rank group.
        self.df["max_rank"] = rank_df.max(axis=1)

        # 3. Sort by this new max_rank and then create the final dense rank,
        # which is equivalent to the original 'rank_counter'.
        self.df = self.df.sort_values("max_rank")
        self.df["secondary_rank"] = self.df["max_rank"].rank(method="dense").astype(int)

        # Since the DataFrame is sorted, this keeps the best-ranked version of each sequence.
        self.df = self.df.drop_duplicates(subset="designed_sequence", keep="first")

        # compute additional metrics
        self.df["has_x"] = self.df["designed_sequence"].str.contains("X")
        self.df["no_CYS"] = self.df["design_CYS"] == 0.0

        self.criteria_df = pd.DataFrame(self.sorting_criteria)
        self.criteria_df = self.criteria_df.sort_values(
            by="importance", ascending=False
        )

        self.df = self.df.sort_values(
            by=list(self.criteria_df["feature"]),
            ascending=list(self.criteria_df["lower_is_better"]),
        )

        self.df["final_rank"] = np.arange(1, len(self.df) + 1)
        self.df["quality_score"] = 1 - (self.df["final_rank"] - 1) / (len(self.df) - 1)

        # Reorder columns
        priority_col_candidates = [
            "id",
            "final_rank",
            "secondary_rank",
            "quality_score",
            "designed_sequence",
            "num_design",
            "affinity_probability_binary1",
            "rmsd<2.5",
            "design_ptm",
            "design_iptm",
            "min_interaction_pae",
            "rmsd",
            "plip_saltbridge" + ("_refolded" if self.from_inverse_folded else ""),
            "plip_hbonds" + ("_refolded" if self.from_inverse_folded else ""),
            "plip_hydrophobic" + ("_refolded" if self.from_inverse_folded else ""),
            "delta_sasa_original",
            "delta_sasa_refolded",
            "loop",
            "helix",
            "sheet",
            "design_largest_hydrophobic_patch",
            "cluster_07_seqidentity",
            "clusters_05_tmscore",
        ]
        priority_cols = [c for c in priority_col_candidates if c in self.df.columns]

        other_cols = [col for col in self.df.columns if col not in priority_cols]
        new_column_order = priority_cols + other_cols
        self.df = self.df[new_column_order]

    def write_outdir(self):
        num_digits = len(str(len(self.df)))

        top_dir2 = self.top_dir / "aaa_refolded"
        top_dir2.mkdir(parents=True, exist_ok=True)
        for i, (idx, row) in tqdm(
            enumerate(self.df.iterrows()), desc="copy top design files"
        ):
            filename = row["file_name"]
            new_filename = f"qualityrank{i:0{num_digits}d}_{filename}"
            src = self.design_dir / filename
            dst = self.outdir / new_filename
            if not self.write_only_top_designs:
                shutil.copy2(src, dst)
            if i < self.budget:
                dst = self.top_dir / new_filename
                shutil.copy2(src, dst)

                src = self.design_dir / "refold_cif" / filename
                dst = top_dir2 / new_filename
                shutil.copy2(src, dst)

        # save to output/diverse_* directory
        self.div_dir.mkdir(parents=True, exist_ok=True)
        div_dir2 = self.div_dir / "aaa_refolded"
        div_dir2.mkdir(parents=True, exist_ok=True)
        for i in tqdm(self.diverse_selection, desc="copy diversity files"):
            src = self.design_dir / self.df_m.loc[i, "file_name"]
            qualityrank = self.df_m.loc[i, "final_rank"]
            filename = src.name
            new_filename = f"qualityrank{qualityrank:0{num_digits}d}_{filename}"
            shutil.copy2(src, self.div_dir / new_filename)

            src = self.design_dir / "refold_cif" / self.df_m.loc[i, "file_name"]
            shutil.copy2(src, div_dir2 / new_filename)
        self.df_div.to_csv(
            self.outdir / f"diverse_selected_{self.div_budget}.csv", index=False
        )
        print("Files + CSV saved to", self.outdir)

        self.df.to_csv(self.outdir / f"metrics_{self.name}.csv", index=False)

    def optimize_diversity(self):
        # Load structures and sequences to compute similarities
        seq_path = self.design_dir / "ca_coords_sequences.pkl.gz"
        if not seq_path.exists():
            raise FileNotFoundError(f"Expected {seq_path} to exist")
        df_seq = pd.read_pickle(seq_path)[["id", "sequence"]]

        self.df_m = pd.merge(self.df, df_seq, on="id", how="inner").reset_index(
            drop=True
        )
        seqs = self.df_m["sequence"].tolist()
        quality = self.df_m["quality_score"].to_numpy()

        # sequence-only similarity
        aligner = Align.PairwiseAligner()
        pid_cache = {}

        def sim_fn(i, j):
            if i == j:
                return 1.0
            key = tuple(sorted((i, j)))
            if key not in pid_cache:
                aln = aligner.align(seqs[i], seqs[j])[0]
                pid_cache[key] = aln.score / max(len(seqs[i]), len(seqs[j]))
            return pid_cache[key]

        random.seed(self.random_state)
        np.random.seed(self.random_state)
        diverse_selection = self.select_lazy_greedy(self.div_budget, quality, sim_fn)
        print(f"Diverse selections are ranks: {diverse_selection}")
        self.diverse_selection = diverse_selection
        self.df_div = self.df_m.iloc[diverse_selection].reset_index(drop=True)

    def select_lazy_greedy(self, k, quality, sim_fn):
        selected = [int(np.argmax(quality))]
        remaining = set(range(len(quality))) - set(selected)

        import heapq, statistics

        heap = []
        for i in remaining:
            div = 1 - sim_fn(i, selected[0])
            gain = (1 - self.alpha) * quality[i] + self.alpha * div
            heapq.heappush(heap, (-gain, i))

        timings = []
        for _ in tqdm(range(k - 1), desc="Diversity optimization lazy greedy."):
            t0 = time.perf_counter()
            while True:
                neg_gain, cand = heapq.heappop(heap)
                true_div = 1 - max(sim_fn(cand, j) for j in selected)
                true_g = (1 - self.alpha) * quality[cand] + self.alpha * true_div
                heapq.heappush(heap, (-true_g, cand))
                if heap[0][1] == cand:
                    heapq.heappop(heap)
                    selected.append(cand)
                    remaining.remove(cand)
                    break
            timings.append(time.perf_counter() - t0)
        return selected

    def prepare_visualization(self):
        summary_metrics = [
            "num_design",
            "rmsd" if not self.from_inverse_folded else "bb_rmsd",
            "design_ptm",
            "design_iptm",
            "min_interaction_pae",
            "delta_sasa_refolded"
            if self.from_inverse_folded
            else "delta_sasa_original",
            "plip_saltbridge" + ("_refolded" if self.from_inverse_folded else ""),
            "plip_hbonds" + ("_refolded" if self.from_inverse_folded else ""),
            "plip_hydrophobic" + ("_refolded" if self.from_inverse_folded else ""),
        ]

        # Scatter pairs (each will be one page)
        extra_pairs = [
            ("num_design", "rank"),
            (
                "num_design",
                "plip_saltbridge" + ("_refolded" if self.from_inverse_folded else ""),
            ),
            (
                "num_design",
                "plip_hbond" + ("_refolded" if self.from_inverse_folded else ""),
            ),
            ("num_design", "plip_hydrophobic"),
            ("plip_hbonds", "plip_hbonds_refolded"),
        ]
        if not self.from_inverse_folded:
            extra_pairs.append(("delta_sasa_refolded", "delta_sasa_original"))
            extra_pairs.append(("plip_saltbridge", "delta_sasa_original"))

        # Histograms with selected overlay
        hist_metrics = [
            "num_design",
            "rmsd" if not self.from_inverse_folded else "bb_rmsd",
            "design_ptm",
            "design_iptm",
            "min_interaction_pae",
            "plip_saltbridge",
            "plip_hbonds",
            "plip_hydrophobic",
            "delta_sasa_refolded",
        ]
        if not self.from_inverse_folded:
            hist_metrics.append("delta_sasa_original")

        if self.use_affinity:
            summary_metrics.insert(2, "affinity_probability_binary1")
            hist_metrics.insert(2, "affinity_probability_binary1")

        avail = [m for m in summary_metrics if m in self.df.columns]
        base_rows = [
            ["Num designs", len(self.df), "-"],
            ["Num rmsd<2.5", (self.df["rmsd<2.5"]).sum(), "-"],
            [
                "Num rmsd<2.5 & design_ptm>0.8",
                (self.df["rmsd<2.5"] & (self.df["design_ptm"] > 0.8)).sum(),
                "-",
            ],
            ["Num design_ptm>0.8", (self.df["design_ptm"] > 0.8).sum(), "-"],
        ]

        extra_mean = (
            [
                m,
                f"{self.df[m].mean():.3f}",  # mean of ALL
                f"{self.df[: self.budget][m].mean():.3f}",  # mean of red set
                f"{self.df_div[m].mean():.3f}",  # mean of BLUE set
            ]
            for m in avail
        )

        for row in base_rows:
            row.append("-")

        rows = base_rows + list(extra_mean)

        row_headers = [
            "Metric",
            f"Mean",
            f"Mean top {self.budget}",
            f"Mean top {self.div_budget} diverse",
        ]

        metric_rows = [[k, v] for k, v in self.metrics.items()]

        text = f"""
        Results Overview: {self.name}

        We make {len(self.df)} designs and then filter them down to the best {self.budget} which can be found in the top_{self.budget}_designs directory. These designs correspond to the red dots in the plots below.
        {"" if not self.from_inverse_folded else "Since you are using inverse folding, please look at the .cif files in aaa_refolded if you want to analyze structures with sidechains."}
        
        Blue dots mark the {self.div_budget} designs obtained with quality–diversity optimisation (alpha = {self.alpha},
        sequence-identity similarity).
        These diversity optimized designs and CSV with them are saved in the directory 'diverse_{self.div_budget}_designs/' inside the output folder.


        The rows in the .csv file are ordered by the quality of the designs. The best designs/rows are at the top.
        The ranking is performed based on the metrics in the table with Inverse Importances below.


        Some columns of the csv file explained:

        "id": filename to retrieve the file
        "design_sequence": the amino acids that were designed (potentially not the whole sequence).
        "designed_chain_sequence": all amino acids of the chain that contained designed amino acids. This is likely what you should choose from to synthesize your designs.
        "num_design": number of designed residues
        "secondary_rank": a ranking from an intermediate rank computation step
        "rmsd<2.5": True/False the RMSD between the generated structure and the structure that Boltz2 predicts for the generated sequence is less than 2.5

        "design_ptm": predicted TM score confidence for all PTMs between designed residues: higher is better
        "design_iptm": predicted TM score confidence for all PTMs between designed and target residues: higher is better
        "min_interaction_pae": minimum of all pae's between the design and the target: **lower is better**

        "plip_saltbridge": Number of saltbridges (negative charges interacting with positive charges)
        "plip_hbonds": Num hbonds
        "plip_hydrophobic": Num hydrophobic interactions
        "delta_sasa_original": The difference in the solvent accessible surface area when the binder is present vs. when it is not present
        "delta_sasa_refolded": Same as delta_sasa_original, but computed for the structure as refolded by Boltz2

        "loop": Fraction of loop residues
        "helix": Fraction of helix residues
        "sheet": Fraction of sheet residues
        "design_largest_hydrophobic_patch": Surface area of the largest hydrophobic path in the design
        "cluster_07_seqidentity": cluster ID when clustering by 70% sequence identity
        "clusters_05_tmscore": cluster ID when clustering by 0.5 tm score
        """

        return hist_metrics, extra_pairs, row_headers, rows, metric_rows, text

    def make_visualization(
        self,
        hist_metrics,
        extra_pairs,
        row_headers,
        rows,
        metric_rows,
        text,
        jupyter_nb=False,
    ):
        num_rmsd_success = (self.df["rmsd<2.5"]).sum()
        pdf_path = self.outdir / f"results_overview_{self.name}.pdf"
        pdf = PdfPages(pdf_path)

        def show(fig):
            plt.tight_layout()
            pdf.savefig(fig)
            if jupyter_nb:
                plt.show(fig)
            plt.close(fig)

        fig, ax = plt.subplots(figsize=(8.5, 11))
        ax.axis("off")
        ax.text(0.05, 0.95, text, fontsize=12, va="top", ha="left", wrap=True)
        show(fig)

        ## Table for sorting criteria
        fig, ax = plt.subplots(figsize=(6, 0.4 * len(metric_rows) + 1))
        ax.axis("off")
        ax.text(
            0.5,
            1.0,
            "Sorting Criteria",
            fontsize=14,
            ha="center",
            va="bottom",
            transform=ax.transAxes,
        )
        table = ax.table(
            cellText=metric_rows,
            colLabels=["Metric", "Inverse Importance"],
            loc="center",
        )
        table.auto_set_font_size(False)
        table.set_fontsize(8)
        table.scale(1, 1.2)
        show(fig)

        ## Table for filtering criteria
        fig_height = 0.4 * len(self.criteria_df) + 2  # extra space for title
        fig, ax = plt.subplots(figsize=(8.5, fig_height))
        ax.axis("off")
        ax.text(
            0.5,
            1.0,
            "Filtering Criteria",
            fontsize=14,
            ha="center",
            va="bottom",
            transform=ax.transAxes,
        )
        table = ax.table(
            cellText=self.criteria_df.values,
            colLabels=self.criteria_df.columns.tolist(),
            loc="center",
        )
        table.auto_set_font_size(False)
        table.set_fontsize(8)
        table.scale(1, 1.2)
        show(fig)

        ## Table for results summary
        if rows:
            fig, ax = plt.subplots(figsize=(8.5, 0.4 * len(rows) + 1))
            ax.axis("off")
            table = ax.table(
                cellText=rows,
                colLabels=row_headers,
                loc="center",
            )
            table.auto_set_font_size(False)
            table.set_fontsize(8)
            table.scale(1, 1.2)
            show(fig)

        # Plot sequence logos and amino acid composition pies
        vis = (
            "designed_sequence"
            if (
                self.df["designed_chain_sequence"].str.len().mean()
                > 1.5 * self.df["designed_sequence"].str.len().mean()
            )
            else "designed_chain_sequence"
        )
        seq_sets = [
            (
                f"All {len(self.df)} {vis}",
                self.df[vis].tolist(),
            ),
            (
                f"Top {self.budget} {vis}",
                self.df[vis].tolist()[: self.budget],
            ),
            (
                f"Diverse {self.div_budget} {vis}",
                self.df_div[vis].tolist(),
            ),
        ]
        if self.plot_seq_logos:
            for name, sequences in seq_sets:
                show(create_alignment_logo(sequences, name))
            for name, sequences in seq_sets:
                show(aa_composition_pie(sequences, name))

            if self.modality == "antibody":
                for name, sequences in seq_sets:
                    show(cdr_logo(sequences, name))

        # Make scatter plots
        for x, y in extra_pairs:
            if x in self.df.columns and y in self.df.columns:
                fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
                self._scatter_plus(ax1, x, y, len(self.df), "All samples")
                if num_rmsd_success > 0:
                    self._scatter_plus(ax2, x, y, num_rmsd_success, "RMSD<2.5")
                show(fig)

        # Make histograms
        for m in hist_metrics:
            if m not in self.df.columns:
                continue
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
            self._hist_plus(
                ax1, self.df[m], self.df[: self.budget][m], self.df_div[m], m, ""
            )
            if num_rmsd_success > 0:
                self._hist_plus(
                    ax2,
                    self.df[:num_rmsd_success][m],
                    self.df[: self.budget][m],
                    self.df_div[m],
                    m,
                    " (RMSD<2.5)",
                )
            show(fig)

        # Plot Liability Heatmaps for Top-budget subset
        for idx, row in tqdm(
            enumerate(self.df[: self.num_liability_plots].itertuples(index=False)),
            desc=f"Making liability plots for top {self.num_liability_plots} sequences.",
        ):
            seq = row.designed_sequence
            try:
                res = compute_liability_scores(
                    [seq], modality=self.modality, peptide_type=self.peptide_type
                )
                liab = res.get(seq, {"score": None, "violations": []})
                fig = plot_seq_liabilities(
                    seq,
                    f"Qualityrank {idx} {row.id}",
                    liab["violations"],
                    total_score=liab["score"],
                )
                show(fig)
            except Exception as e:
                print(f"  Error processing  {seq[:20]}: {e}")
                plt.close("all")
                continue

        pdf.close()
        print("Saved additional quality plots to", pdf_path)

    def _scatter_plus(self, ax, x, y, num_samples, title=""):
        ax.scatter(
            self.df[:num_samples][x],
            self.df[:num_samples][y],
            color="lightgray",
            alpha=0.4,
            s=14,
            zorder=1,
        )

        ax.scatter(
            self.df[: self.budget][x],
            self.df[: self.budget][y],
            facecolors="none",
            edgecolors="red",
            linewidth=1.5,
            s=30,
            zorder=2,
            alpha=0.5,
            label="top-quality",
        )

        if not self.df_div.empty:
            ax.scatter(
                self.df_div[x],
                self.df_div[y],
                facecolors="none",
                edgecolors="blue",
                linewidth=1.5,
                s=50,  #  ← slightly larger
                zorder=3,
                alpha=0.5,
                label="quality+diversity",
            )

        ax.set_xlabel(x)
        ax.set_ylabel(y)
        ax.set_title(title)
        ax.legend()

    def _hist_plus(self, ax, data_all, data_red, data_blue, metric, suffix):
        # Check if data contains valid values for histogram
        if data_all is None or len(data_all) == 0 or data_all.isna().all():
            ax.text(
                0.5,
                0.5,
                f"No valid data for {metric}",
                ha="center",
                va="center",
                transform=ax.transAxes,
            )
            ax.set_xlabel(metric)
            ax.set_ylabel("count")
            ax.set_title(f"{metric}{suffix} (No data)")
            return

        # Filter out NaN values for histogram plotting
        valid_data_all = data_all.dropna()
        valid_data_red = (
            data_red.dropna() if data_red is not None else pd.Series(dtype=float)
        )
        valid_data_blue = (
            data_blue.dropna() if data_blue is not None else pd.Series(dtype=float)
        )

        if len(valid_data_all) == 0:
            ax.text(
                0.5,
                0.5,
                f"No valid data for {metric}",
                ha="center",
                va="center",
                transform=ax.transAxes,
            )
            ax.set_xlabel(metric)
            ax.set_ylabel("count")
            ax.set_title(f"{metric}{suffix} (No data)")
            return

        # Create histogram with valid data
        ax.hist(valid_data_all, bins=30, color="lightgray", alpha=0.6, label="all")

        if len(valid_data_red) > 0:
            ax.hist(
                valid_data_red,
                bins=30,
                histtype="step",
                linewidth=1.7,
                color="red",
                label="top-quality",
            )
        if len(data_blue) and len(valid_data_blue) > 0:
            ax.hist(
                valid_data_blue,
                bins=30,
                histtype="step",
                linewidth=1.7,
                color="blue",
                linestyle="--",
                label="quality+diversity",
            )

        ax.set_xlabel(metric)
        ax.set_ylabel("count")
        ax.set_title(f"{metric}{suffix}")
        ax.legend()
