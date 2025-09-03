"""
plot_evolution.py

A module that generates a series of plots based on JSON logs produced
by an evolutionary optimization process. The script plots various
statistics (objectives, features, stall counts, dataset sizes, etc.)
over multiple generations, and also produces nearest-neighbor heatmaps
in 2D PCA feature space for each objective dimension.

Modified to include explicit statements indicating each plot’s
save location after it is generated.
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from collections import defaultdict
from scipy.spatial import cKDTree
import warnings, os

def pad_ragged_list_of_lists(list_of_lists, fill_value=np.nan):
    r"""
    Convert a ragged (uneven) list of sequences into a 2D NumPy array by padding.

    Given a sequence of lists or 1D arrays 
    :math:`\{L_i\}_{i=1}^N` where each 
    :math:`L_i` has length :math:`|L_i|`, define
    the maximum row length

    .. math::
       M \;=\; \max_{1 \le i \le N} |L_i|.

    The output is an array 
    :math:`A \in \mathbb{R}^{N\times M}` with entries

    .. math::
       A_{i j} = 
       \begin{cases}
         (L_i)_j, & 0 \le j < |L_i|,\\
         v_{\mathrm{fill}}, & |L_i| \le j < M,
       \end{cases}

    where 
    :math:`(L_i)_j` is the :math:`j`th element of :math:`L_i`, and 
    :math:`v_{\mathrm{fill}}` is the specified `fill_value`.

    Parameters
    ----------
    list_of_lists : List[List[float] or np.ndarray]
        A list of 1D sequences (lists or arrays) of potentially varying lengths.
        Each inner sequence :math:`L_i` may have a different length :math:`|L_i|`.
    fill_value : float, optional
        Value used to pad shorter rows out to the common length :math:`M`.
        Defaults to :obj:`numpy.nan`.

    Returns
    -------
    np.ndarray
        A 2D array of shape :math:`(N, M)`, where :math:`N = \len(list_of_lists)`
        and :math:`M = \max_i |L_i|`.  Rows shorter than :math:`M` are padded
        on the right with `fill_value`.

    Examples
    --------
    >>> pad_ragged_list_of_lists([[1, 2, 3], [4], [5, 6]], fill_value=0)
    array([[1., 2., 3.],
           [4., 0., 0.],
           [5., 6., 0.]])
    """
    
    if not list_of_lists:
        return np.array([])

    # Find the length of the longest sublist
    max_length = max(len(sublist) for sublist in list_of_lists)
    num_rows = len(list_of_lists)

    # Initialize a 2D array of fill_values
    padded = np.full((num_rows, max_length), fill_value, dtype=float)

    # Overwrite with real values
    for i, sublist in enumerate(list_of_lists):
        length = len(sublist)
        padded[i, :length] = sublist

    return padded

class EvolutionPlotter:
    """
    A class to load, parse, and visualize evolutionary optimization data
    from JSON logs produced during a multi-generation search/optimization.

    Attributes
    ----------
    logger_dir : str
        Path to the directory containing JSON logs (named generation_data_genX.json).
    output_dir : str
        Directory where all output plot images (PNG files) will be saved.

    Methods
    -------
    generate_all_plots():
        Orchestrates the entire data parsing and plotting process, saving
        the resulting figures to disk.
    """

    def __init__(self, logger_dir: str=None, output_dir: str=None):
        """
        Initializes the EvolutionPlotter with paths to the logger directory
        and the desired output directory for plots.

        Parameters
        ----------
        logger_dir : str
            Directory containing the JSON log files: "generation_data_genX.json".
        output_dir : str
            Directory in which to save all generated plots.
        """
        self.logger_dir = logger_dir
        self.output_dir = output_dir

        # Internal data structures to hold parsed information
        self.generations = []
        self.stall_counts = []

        self.stall_count_objetive = []
        self.novelty_history = []
        self.novelty_thresh_history = []
        self.stall_count_information = []

        self.dataset_sizes = []
        self.mean_objectives_series = []
        self.min_objectives_series = []
        self.mean_features_series = []
        self.std_features_series = []

        self.mutation_rate_series = []
        self.mutation_probabilities = []
        self.mutation_attempt_counts = []
        self.mutation_fails_counts = []
        self.mutation_success_counts = []
        self.mutation_unsuccess_counts = []
        self.mutation_hashcolition_counts = []
        self.mutation_outofdoe_counts = []

        self.crossover_rate_series = []
        self.crossover_probabilities = []
        self.crossover_attempt_counts = []
        self.crossover_fails_counts = []
        self.crossover_success_counts = []
        self.crossover_unsuccess_counts = []
        self.crossover_hashcolition_counts = []
        self.crossover_outofdoe_counts = []

        self.time_log = {}

        self.supercell_map = {}
        self.lineage_map = {}

        self.gen_features = {}
        self.gen_objectives = {}
        self.objectives_series_history = {}

        self.model_evolution_info_history = {}

        self.T = [] 

        # For PCA
        self.all_feat_list = []
        self.all_obj_list = []
        self.last_gen_key = None
        self.pca_global = None
        self.pca_global_2d = None

        self.save_dat = True

        # Utility: create output directory if it doesn't exist
    def _save_xy_data(self,
                      x: np.ndarray,
                      y: np.ndarray,
                      filename: str,
                      header: str = None) -> None:
        """
        Save one or more y‐series against a common x‐axis to a .dat file.
        Parameters
        ----------
        x : np.ndarray
            1D array of x‐values.
        y : np.ndarray
            1D (shape=(N,)) or 2D (shape=(N, M)) array of y‐values.
        filename : str
            Base filename (without extension). Will write filename + '.dat'.
        header : str, optional
            Header line to insert at top of file (e.g. 'x mean min max').
        """
        # ensure 2D
        y_arr = np.atleast_2d(y)
        y_arr = y_arr if y_arr.shape[0] == x.shape[0] else y_arr.T
        data = np.column_stack([x, y_arr])
        outpath = os.path.join(self.output_dir, filename + ".dat")
        # use fmt='% .6e' or whatever precision you like
        np.savetxt(outpath,
                   data,
                   header=header or "",
                   comments='',
                   fmt="%.6e")
        print(f"Saved data '{filename}.dat' to: {outpath}")

    def _parse_json_logs(self) -> None:
        """
        Parses all JSON logs named "generation_data_genX.json" in self.logger_dir,
        extracting relevant data for subsequent plotting.
        """
        # ---------------------------------------------------------------------
        # Gather all JSON files named "generation_data_gen*.json"
        # ---------------------------------------------------------------------
        json_files = []
        for fname in os.listdir(self.logger_dir):
            if fname.startswith("generation_data_gen") and fname.endswith(".json"):
                json_files.append(fname)

        if not json_files:
            print(f"No JSON logs found in {self.logger_dir}. Aborting plots.")
            return

        def extract_gen_number(filename: str) -> int:
            """
            Extract the generation number from a filename of the form:
            'generation_data_genX.json' -> X
            """
            base = filename.replace("generation_data_gen", "").replace(".json", "")
            return int(base)

        json_files.sort(key=extract_gen_number)

        # ---------------------------------------------------------------------
        # Initialize local structures to store generation-based data
        # ---------------------------------------------------------------------
        for filename in json_files:
            path = os.path.join(self.logger_dir, filename)
            with open(path, 'r') as infile:
                data = json.load(infile)

            if data.get("features", 0) is None:
                continue

            gen = data.get("generation", 0)
            self.generations.append(gen)

            stall_count = data.get("stall_count", 0)
            self.stall_counts.append(stall_count)
            novelty_history = data.get("novelty_history", 0)
            self.novelty_history.append(novelty_history)
            novelty_thresh_history = data.get("novelty_thresh_history", 0)
            self.novelty_thresh_history.append(novelty_thresh_history)
            stall_count_information = data.get("stall_count_information", 0)
            self.stall_count_information.append(stall_count_information)
            stall_count_objetive = data.get("stall_count_objetive", 0)
            self.stall_count_objetive.append(stall_count_objetive)

            n_dataset = data.get("num_structures_in_dataset", 0)
            self.dataset_sizes.append(n_dataset)

            obj_list = data.get("objectives", [])
            obj_arr = (
                np.array(obj_list, dtype=float) if obj_list else np.zeros((0,))
            )

            time_log_i = data.get("time_log", {})
            for key, item in time_log_i.items():
                self.time_log.setdefault(key, []).append(item)
            self.supercell_map[gen] = data.get("supercell_repeat", None)
            self.lineage_map[gen] = data.get("lineage_data", [])

            self.mutation_rate_series.append(data.get("mutation_rate_history", []))
            self.mutation_probabilities.append(data.get("mutation_probabilities", []))
            self.mutation_attempt_counts.append(data.get("mutation_attempt_counts", []))
            self.mutation_fails_counts.append(data.get("mutation_fails_counts", []))
            self.mutation_success_counts.append(data.get("mutation_success_counts", []))
            self.mutation_unsuccess_counts.append(data.get("mutation_unsuccess_counts", []))
            self.mutation_hashcolition_counts.append(data.get("mutation_hashcolition_counts", []))
            self.mutation_outofdoe_counts.append(data.get("mutation_outofdoe_counts", []))

            self.crossover_rate_series.append(data.get("crossover_rate_history", []))
            self.crossover_probabilities.append(data.get("crossover_probabilities", []))
            self.crossover_attempt_counts.append(data.get("crossover_attempt_counts", []))
            self.crossover_fails_counts.append(data.get("crossover_fails_counts", []))
            self.crossover_success_counts.append(data.get("crossover_success_counts", []))
            self.crossover_unsuccess_counts.append(data.get("crossover_unsuccess_counts", []))
            self.crossover_hashcolition_counts.append(data.get("crossover_hashcolition_counts", []))
            self.crossover_outofdoe_counts.append(data.get("crossover_outofdoe_counts", []))


            self.T.append(data.get("T", []))

            # Reshape objectives if only one dimension
            if obj_arr.ndim == 1 and obj_arr.size > 0:
                obj_arr = obj_arr.reshape(-1, 1)

            # Compute mean and min objective if valid
            if obj_arr.size > 0 and obj_arr.ndim == 2:
                mean_obj = np.mean(obj_arr, axis=0)
                min_obj = np.min(obj_arr, axis=0)
            else:
                mean_obj = np.array([])
                min_obj = np.array([])

            self.mean_objectives_series.append(mean_obj)
            self.min_objectives_series.append(min_obj)
            self.gen_objectives[gen] = obj_arr

            # Append to global objective list
            for row in obj_arr:
                self.all_obj_list.append((gen, row))

            # Capture objective history keyed by feature
            self.objectives_series_history[gen] = {}
            hist_dict = data.get("objectives_for_features_history", {})
            for key, item in hist_dict.items():
                self.objectives_series_history[gen][key] = item['best_objective']

            # Extract features
            feat_list = data.get("features", [])
            feat_arr = (
                np.array(feat_list, dtype=float) if feat_list else np.zeros((0,))
            )

            if feat_arr.ndim == 1 and feat_arr.size > 0:
                feat_arr = feat_arr.reshape(-1, 1)

            if feat_arr.size > 0 and feat_arr.ndim == 2:
                mean_feat = np.mean(feat_arr, axis=0)
                std_feat = np.std(feat_arr, axis=0)
            else:
                mean_feat = np.array([])
                std_feat = np.array([])

            self.mean_features_series.append(mean_feat)
            self.std_features_series.append(std_feat)
            self.gen_features[gen] = feat_arr

            # Append features to global list
            for row in feat_arr:
                self.all_feat_list.append((gen, row))

            model_info = data.get("model_evolution_info", {})
            self.model_evolution_info_history[gen] = model_info
        
        if self.generations:
            self.last_gen_key = max(self.gen_features.keys())

        # ---------------------------------------------------------------------
        # Establish a 1D PCA using the final generation’s features
        # ---------------------------------------------------------------------
        self.pca_global = PCA(n_components=1)
        if self.last_gen_key is not None:
            last_gen_feats = self.gen_features[self.last_gen_key]
            if last_gen_feats.shape[0] > 0:
                self.pca_global.fit(last_gen_feats)

    def _plot_objectives_vs_generation_history(self) -> None:
        """
        Plots the objectives vs generation for each distinct feature key
        found in the logs' 'objectives_for_features_history' field.
        """
        # Construct data structure:
        #   data_plot[feature_key] -> list of [generation, obj_dim0, obj_dim1, ...]
        data_plot = {}
        for gen, feature_dict in self.objectives_series_history.items():
            for feature_key, obj_values in feature_dict.items():
                if feature_key not in data_plot:
                    data_plot[feature_key] = []
                row = [gen] + obj_values
                data_plot[feature_key].append(row)

        if not data_plot:
            print("No feature-keyed objective history found. Skipping some objective vs generation plots.")
            return

        feature_keys = list(data_plot.keys())
        colors_plot = plt.cm.tab10(np.linspace(0, 1, len(feature_keys)))

        # Assume at least 2 objective dimensions for demonstration
        for i, (feature_key, rows) in enumerate(data_plot.items()):
            obj_N = np.array(rows).shape[1]
            break

        for obj_dim in range(1, obj_N):
            plt.figure()
            for i, (feature_key, rows) in enumerate(data_plot.items()):
                arr = np.array(rows)
                # Sort by generation (index = 0)
                arr_sorted = arr[np.argsort(arr[:, 0])]
                if arr_sorted.shape[1] > obj_dim:
                    plt.plot(
                        arr_sorted[:, 0],
                        arr_sorted[:, obj_dim],
                        color=colors_plot[i],
                        alpha=0.6
                    )
            plt.xlabel("Generation")
            plt.ylabel(f"Objective Dimension {obj_dim}")
            plt.title(f"Objectives vs. Generation (Dimension {obj_dim})")

            plot_filename = f"objectives_vs_generation_dim{obj_dim}.png"
            full_path = os.path.join(self.output_dir, plot_filename)
            plt.savefig(full_path, dpi=300)
            print(f"Saved plot '{plot_filename}' to: {full_path}")
            plt.close()

        # ---------------------------------------------------------------------
        # Additional filtered evolution view
        # ---------------------------------------------------------------------
        for obj_dim in range(1, 3):
            plt.figure()
            for i, (feature_key, rows) in enumerate(data_plot.items()):
                arr = np.array(rows)
                arr_sorted = arr[np.argsort(arr[:, 0])]
                if arr_sorted.shape[1] > obj_dim:
                    val_array = np.unique(arr_sorted[:, obj_dim])[::-1]
                    plt.plot(
                        val_array,
                        color=colors_plot[i],
                        alpha=0.6
                    )
            plt.xlabel("Generation")
            plt.ylabel(f"Objective Dimension {obj_dim}")
            plt.title(f"Filtered Evolution of Objective Value - Dimension {obj_dim}")

            plot_filename = f"objectives_vs_change_dim{obj_dim}.png"
            full_path = os.path.join(self.output_dir, plot_filename)
            plt.savefig(full_path, dpi=300)
            print(f"Saved plot '{plot_filename}' to: {full_path}")
            plt.close()

    def _plot_objectives_vs_1d_pca(self) -> None:
        """
        Plots "Objectives vs. 1D PCA(PC1) Feature" for each generation,
        using the PCA transformation fitted on the final generation.
        """
        # data_plot2[generation] -> list of [PC1_value, obj_dim0, obj_dim1, ...]
        data_plot2 = {}

        for gen, feature_dict in self.objectives_series_history.items():
            if gen not in data_plot2:
                data_plot2[gen] = []

            for feature_key, obj_values in feature_dict.items():
                tokens = [t.strip() for t in feature_key.strip("()").split(",") if t.strip()]
                numeric_feature = [float(t) for t in tokens]
                if self.pca_global is not None and self.gen_features[self.last_gen_key].shape[0] > 0:
                    pc1_value = self.pca_global.transform([numeric_feature])[0][0]
                else:
                    pc1_value = 0.0
                row = [pc1_value] + obj_values
                data_plot2[gen].append(row)

        if not data_plot2:
            print("No feature-keyed data for PC1 plots. Skipping PCA-based objective plots.")
            return

        gen_list = sorted(data_plot2.keys())
        colors_plot2 = plt.cm.viridis(np.linspace(0, 1, len(gen_list))) 

        for obj_dim in range(1, len(obj_values)):
            plt.figure()
            for i, gen in enumerate(gen_list):
                if len(data_plot2[gen]) > 0:
                    arr = np.array(data_plot2[gen])
                    # Sort by PC1 (column 0)
                    arr_sorted = arr[np.argsort(arr[:, 0])]
                    if arr_sorted.shape[1] > obj_dim:
                        plt.plot(
                            arr_sorted[:, 0],
                            arr_sorted[:, obj_dim],
                            'o--',
                            color=colors_plot2[i],
                            alpha=0.4
                        )
            plt.xlabel("Principal Component 1 (PC1)")
            plt.ylabel(f"Objective Dimension {obj_dim}")
            plt.title(f"Objectives vs. PC1 (Objective Dim {obj_dim})")

            plot_filename = f"objectives_vs_pca_dim{obj_dim}.png"
            full_path = os.path.join(self.output_dir, plot_filename)
            plt.savefig(full_path, dpi=300)
            print(f"Saved plot '{plot_filename}' to: {full_path}")
            plt.close()

    def _plot_stall_and_dataset_size(self) -> None:
        """
        Plots the stall count (cumulative and instantaneous) and
        the dataset size over generations.
        """
        if not self.generations:
            print("No generation data found. Skipping stall/dataset size plots.")
            return

        generations_arr = np.array(self.generations)
        stall_arr = np.array(self.stall_counts)
        data_size_arr = np.array(self.dataset_sizes)

        stall_count_objetive_arr = self.stall_count_objetive/np.max(self.stall_count_objetive) * np.max(stall_arr)
        stall_count_information_arr = self.stall_count_information/np.max(self.stall_count_information) * np.max(stall_arr)

        # Plot stall counts
        plt.figure()

        stall_count_objetive_cumsum = stall_count_objetive_arr
        plt.step(generations_arr, stall_count_objetive_cumsum/np.max(stall_count_objetive_cumsum) * np.max(stall_arr), where='post', label="(relative) Objetive Stall", alpha=0.2)
        stall_count_information_cumsum = stall_count_information_arr
        plt.step(generations_arr, stall_count_information_cumsum/np.max(stall_count_information_cumsum) * np.max(stall_arr), where='post', label="(relative) Information Stall", alpha=0.2)

        stall_cumsum = np.cumsum(stall_arr)
        plt.step(generations_arr, stall_cumsum/np.max(stall_cumsum) * np.max(stall_arr), where='post', label="(relative) Cumulative Stall")
        plt.step(generations_arr, stall_arr, where='post', label="Instant Stall")

        if np.max(stall_cumsum) > 1e-5:
            plt.plot(generations_arr, np.array(self.T)/np.max(self.T)* np.max(stall_arr), label="scaled T" )
        else:
            plt.plot(generations_arr, np.array(self.T), label="scaled T" )
    
        plt.title("Stall Count vs Generation")
        plt.xlabel("Generation")
        plt.ylabel("Stall Count")
        plt.legend()

        plot_filename = "stall_count_step_vs_generation.png"
        full_path = os.path.join(self.output_dir, plot_filename)
        plt.savefig(full_path, dpi=300)
        print(f"Saved plot '{plot_filename}' to: {full_path}")
        plt.close()

        # ======================= # # ======================= #
        # Plot stall counts
        plt.figure()

        novelty_history = self.novelty_history
        novelty_thresh_history = self.novelty_thresh_history
        plt.plot(generations_arr, np.array(novelty_history), label="novelty" )
        plt.plot(generations_arr, np.array(novelty_thresh_history), label="novelty_thresh" )

        if np.max(stall_cumsum) > 1e-5:
            plt.plot(generations_arr, np.array(self.T)/np.max(self.T)* np.max(self.novelty_history) , label="scaled T" )
        else:
            plt.plot(generations_arr, np.array(self.T), label="scaled T" )

        plt.title("novelty vs Generation")
        plt.xlabel("Generation")
        plt.ylabel("novelty")
        plt.legend()

        plot_filename = "novelty_vs_generation.png"
        full_path = os.path.join(self.output_dir, plot_filename)
        plt.savefig(full_path, dpi=300)
        print(f"Saved plot '{plot_filename}' to: {full_path}")
        plt.close()
        # ======================= # # ======================= #

        # Plot dataset size
        plt.figure()
        plt.plot(generations_arr, data_size_arr, marker='o')
        plt.title("Dataset Size vs Generation")
        plt.xlabel("Generation")
        plt.ylabel("Number of Structures")

        plot_filename = "dataset_size_vs_generation.png"
        full_path = os.path.join(self.output_dir, plot_filename)
        plt.savefig(full_path, dpi=300)
        print(f"Saved plot '{plot_filename}' to: {full_path}")
        plt.close()

    def _plot_mean_min_objectives_and_features(self) -> None:
        """
        Plots the mean and minimum objectives (all dimensions) vs generation,
        as well as mean and standard deviation of features vs generation.
        """
        if not self.generations:
            print("No generation data found. Skipping objective/feature line plots.")
            return

        def pad_list_of_arrays(list_of_arrays):
            """
            Pads a list of 1D arrays with NaNs to form a 2D array,
            based on the length of the largest array in the list.
            """
            if not list_of_arrays:
                return np.zeros((0, 0))
            max_dim = max(arr.shape[0] for arr in list_of_arrays)
            n_rows = len(list_of_arrays)
            out = np.full((n_rows, max_dim), np.nan)
            for i, arr in enumerate(list_of_arrays):
                out[i, :arr.shape[0]] = arr
            return out

        mean_obj_arr = pad_list_of_arrays(self.mean_objectives_series)  # shape (G, k)
        min_obj_arr = pad_list_of_arrays(self.min_objectives_series)    # shape (G, k)
        mean_feat_arr = pad_list_of_arrays(self.mean_features_series)   # shape (G, d)
        std_feat_arr = pad_list_of_arrays(self.std_features_series)     # shape (G, d)

        generations_arr = np.array(self.generations)

        # Plot mean/min objectives
        if mean_obj_arr.size > 0:
            _, k_obj = mean_obj_arr.shape
            for dim in range(k_obj):
                plt.figure()
                plt.plot(generations_arr, mean_obj_arr[:, dim], marker='o', label='Mean Obj')
                plt.plot(generations_arr, min_obj_arr[:, dim], marker='o', label='Min Obj')
                plt.title(f"Objective dim {dim} vs Generation")
                plt.xlabel("Generation")
                plt.ylabel("Objective Value")
                plt.legend()

                plot_filename = f"objective_dim{dim}.png"
                full_path = os.path.join(self.output_dir, plot_filename)
                plt.savefig(full_path, dpi=300)
                print(f"Saved plot '{plot_filename}' to: {full_path}")
                plt.close()

                # columns: generation, mean_obj, min_obj                
                if self.save_dat:
                    xy = np.column_stack([y_mean, y_min])  # shape (G, 2)
                    self._save_xy_data(x, xy, basename,
                                       header="generation mean_obj min_obj")

        # Plot mean/std features
        if mean_feat_arr.size > 0:
            _, d_feat = mean_feat_arr.shape
            for dim in range(d_feat):
                plt.figure()
                plt.plot(generations_arr, mean_feat_arr[:, dim], marker='o', label='Mean feat')
                plt.plot(generations_arr, std_feat_arr[:, dim], marker='o', label='Std feat')
                plt.title(f"Feature (dim {dim}) vs Generation")
                plt.xlabel("Generation")
                plt.ylabel("Feature Value")
                plt.legend()

                plot_filename = f"feature_dim{dim}.png"
                full_path = os.path.join(self.output_dir, plot_filename)
                plt.savefig(full_path, dpi=300)
                print(f"Saved plot '{plot_filename}' to: {full_path}")
                plt.close()

                # Dump data
                if self.save_dat:
                    xy = np.column_stack([y_mean, y_std])
                    self._save_xy_data(x, xy, basename,
                                       header="generation mean_feat std_feat")

    def _plot_2d_pca_heatmaps(self) -> None:
        """
        Generates a 2D PCA-based nearest-neighbor heatmap for each objective dimension,
        overlaying the original points in PCA space.
        """
        # Merge features and objectives
        if not self.all_feat_list or not self.all_obj_list:
            print("No global feature/obj data; skipping PCA heat-maps.")
            return

        all_feat_data = np.vstack([m[0] for m in self.all_feat_list])  # (N, d)
        all_obj_data  = np.vstack([m[1] for m in self.all_obj_list])   # (N, k)
        n_samples, n_features = all_feat_data.shape
        k_obj = all_obj_data.shape[1]

        # ----- CASE 1: Standard 2-D PCA possible --------------------------------
        if min(n_samples, n_features) >= 2:
            pca = PCA(n_components=2)
            feats_2d = pca.fit_transform(all_feat_data)

        # ----- CASE 2: Only one feature dimension ------------------------------
        elif n_features == 1 and n_samples > 1:
            pca = PCA(n_components=1)
            pc1 = pca.fit_transform(all_feat_data).ravel()          # (N,)
            # fabricate a quasi-2-D embedding by jittering a zero column
            jitter = (np.random.rand(n_samples) - 0.5) * 1e-3       # tiny ε
            feats_2d = np.column_stack([pc1, jitter])

            warnings.warn(
                "Only one feature-dimension detected → using a jittered "
                "second axis to render 2-D heat-maps.", RuntimeWarning
            )

        # ----- CASE 3: Only one sample -----------------------------------------
        else:  # n_samples == 1
            warnings.warn(
                "Only one sample available → cannot build a heat-map. "
                "Falling back to single-point scatter plots.",
                RuntimeWarning
            )
            feats_2d = np.zeros((1, 2))  # origin



        # -----------------------------------------------------------------------
        # Common plotting section
        Nx, Ny = 200, 200
        x_min, x_max = feats_2d[:, 0].min(), feats_2d[:, 0].max()
        y_min, y_max = feats_2d[:, 1].min(), feats_2d[:, 1].max()
        if x_min == x_max: x_min, x_max = x_min - 0.5, x_max + 0.5
        if y_min == y_max: y_min, y_max = y_min - 0.5, y_max + 0.5
        xs = np.linspace(x_min, x_max, Nx)
        ys = np.linspace(y_min, y_max, Ny)

        for dimO in range(k_obj):
            obj_dim_vec = all_obj_data[:, dimO]  # shape (N,)
            grid_points = np.array([(xx, yy) for yy in ys for xx in xs])
            # Build a cKDTree for nearest-neighbor lookups
            tree = cKDTree(feats_2d)

            # Nearest-neighbor query
            dist, idx = tree.query(grid_points, k=1)
            heat_values = obj_dim_vec[idx]
            heatZ = heat_values.reshape(Ny, Nx)

            plt.figure()
            plt.title(f"Feature Space (2D PCA) + Objective[{dimO}] Heatmap")
            plt.xlabel("PC1")
            plt.ylabel("PC2")

            plt.imshow(
                heatZ,
                origin='lower',
                extent=(x_min, x_max, y_min, y_max),
                aspect='auto',
                cmap='plasma'
            )
            plt.colorbar(label=f'Objective[{dimO}]')

            # Overlay original points
            plt.scatter(feats_2d[:, 0], feats_2d[:, 1], s=10, alpha=0.5)

            plot_filename = f"feature_space_heatmap_objective{dimO}.png"
            full_path = os.path.join(self.output_dir, plot_filename)
            plt.savefig(full_path, dpi=300)
            print(f"Saved plot '{plot_filename}' to: {full_path}")
            plt.close()

    def _plot_mutation_rate_series(self) -> None:
        """
        Plots multiple mutation rate series on the same figure, showing individual
        data points as well as a mean trend line with min/max deviation bands.
        Handles ragged lists by padding with np.nan.
        """
        # Pad the ragged list-of-lists into a 2D array
        mutation_array = pad_ragged_list_of_lists(self.mutation_rate_series)
        # Now 'mutation_array' has shape (num_generations, max_number_of_rates)

        # If, after padding, there's no data, skip
        if mutation_array.size == 0:
            print("No valid mutation rate data found after padding. Skipping mutation rate plot.")
            return

        # We expect 2D shape now
        num_generations, max_rates = mutation_array.shape

        # For safety, check if num_generations or max_rates is zero
        if num_generations == 0 or max_rates == 0:
            print("Empty mutation_rate_series array after padding. Skipping plot.")
            return

        # Build figure
        plt.figure(figsize=(8, 6))
        pastel_blue = "#AEC6CF"
        pastel_red = "#FF6961"

        # Generate statistics across each generation (ignore nan)
        mean_series = np.nanmean(mutation_array, axis=1)  # shape (num_generations,)
        min_series  = np.nanmin(mutation_array, axis=1)
        max_series  = np.nanmax(mutation_array, axis=1)
        x_values    = np.arange(num_generations)

        lower_errors = mean_series - min_series
        upper_errors = max_series - mean_series
        yerr = [lower_errors, upper_errors]

        # Deviation area
        plt.errorbar(
            x_values,
            mean_series,
            yerr=yerr,
            fmt='none',
            ecolor='gray',
            alpha=0.3,
            capsize=5,
            label='Deviation (Min/Max)'
        )

        # Plot all points. We iterate generation by generation
        for g in range(num_generations):
            # These are the rates at generation g for however many mutation types existed
            row_data = mutation_array[g, :]
            # Plot only the non-nan values
            valid_idx = ~np.isnan(row_data)
            plt.scatter(
                np.repeat(g, sum(valid_idx)),  # x-values all = generation index
                row_data[valid_idx],          # y-values
                color='black',
                alpha=0.2,
                marker='x',
                label='_nolegend_'
            )

            # Alternatively, if you want lines for each mutation index over generations,
            # you'd restructure logic to iterate columns instead of rows.

        # Mean trend line across generations
        plt.plot(
            x_values,
            mean_series,
            '-o',
            color=pastel_red,
            alpha=0.5,
            linewidth=2,
            markersize=6,
            label='Mean Mutation Rate'
        )

        plt.xlabel("Generation")
        plt.ylabel("Mutation Rate")
        plt.title("Mutation Rate Series with Mean Trend Line and Deviation")
        plt.legend(loc='best')

        plot_filename = "Crossover_rate_series.png"
        full_path = os.path.join(self.output_dir, plot_filename)
        plt.savefig(full_path, dpi=300)
        print(f"Saved plot '{plot_filename}' to: {full_path}")
        plt.close()

    def _plot_execution_times(self) -> None:
        """
        Plots the execution time for each workflow stage (stored in self.time_log)
        across generations on a log scale.
        """
        if not self.time_log:
            print("No time_log data found. Skipping execution time plot.")
            return

        plt.figure(figsize=(10, 6))

        # time_log is expected to be a dict of stage->list_of_times
        for stage, times in self.time_log.items():
            generations = range(1, len(times) + 1)
            plt.plot(
                generations,
                times,
                marker='o',
                linewidth=2,
                alpha=0.5,
                label=stage
            )

        plt.yscale('log')
        plt.title("Execution Time per Workflow Stage per Generation", fontsize=14)
        plt.xlabel("Generation", fontsize=12)
        plt.ylabel("Execution Time (s) [log]", fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.3)
        plt.legend(loc="best", fontsize=10)
        plt.tight_layout()

        plot_filename = "execution_time_plot.png"
        full_path = os.path.join(self.output_dir, plot_filename)
        plt.savefig(full_path, dpi=300)
        print(f"Saved plot '{plot_filename}' to: {full_path}")
        plt.close()

    def _plot_mutation_probabilities(self) -> None:
        """
        Plots the evolution of mutation probabilities for each mutation type
        across multiple generations.
        """
        mutation_array = np.array(self.mutation_probabilities)
        if mutation_array.ndim != 2 or mutation_array.shape[0] == 0 or mutation_array.shape[1] == 0:
            print("Invalid mutation_probabilities data. Skipping mutation probabilities plot.")
            return

        num_generations, num_mutations = mutation_array.shape
        generations = np.arange(1, num_generations + 1)

        plt.figure(figsize=(10, 6))
        for m in range(num_mutations):
            plt.plot(
                generations,
                mutation_array[:, m],
                marker='o',
                linestyle='-',
                linewidth=2,
                label=f'Mutation {m + 1}'
            )

        plt.title('Evolution of Mutation Probabilities Over Generations', fontsize=16)
        plt.xlabel('Generation', fontsize=14)
        plt.ylabel('Mutation Probability', fontsize=14)
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.legend(loc='best', fontsize=12)
        plt.tight_layout()

        plot_filename = "mutation_probabilities_evolution.png"
        full_path = os.path.join(self.output_dir, plot_filename)
        plt.savefig(full_path, dpi=300)
        print(f"Saved plot '{plot_filename}' to: {full_path}")
        plt.close()

    def _plot_mutation_counts_evolution(self) -> None:
        """
        Generates a 2×2 grid of subplots to illustrate the evolution of
        mutation attempt counts, failure counts, success counts, and
        unsuccessful counts over the generations.

        Each input is expected to be a 2D list or numpy array of shape (G, N),
        where G is the number of generations and N is the number of mutation types.
        """
        # Convert inputs to numpy arrays for consistent manipulation
        attempt_array = np.array(self.mutation_attempt_counts)
        fails_array = np.array(self.mutation_fails_counts)
        success_array = np.array(self.mutation_success_counts)
        unsuccess_array = np.array(self.mutation_unsuccess_counts)
        hashcolition_array = np.array(self.mutation_hashcolition_counts)
        outofdoe_array = np.array(self.mutation_outofdoe_counts)

        # Validate shapes
        if any(arr.ndim != 2 for arr in [attempt_array, fails_array, success_array, unsuccess_array]):
            print("One or more mutation count arrays have invalid dimensions. Skipping mutation counts plot.")
            return

        if not (
            attempt_array.shape == fails_array.shape ==
            success_array.shape == unsuccess_array.shape
        ):
            print("Mismatch in shape among mutation count arrays. Skipping mutation counts plot.")
            return

        num_generations, num_mutations = attempt_array.shape
        generations = np.arange(1, num_generations + 1)

        # Create a 2x2 grid figure
        fig, axs = plt.subplots(2, 3, figsize=(18, 10))
    
        plots_info = [
            (axs[0, 0], attempt_array,    "Mutation Attempts Over Generations", "Attempt Count"),
            (axs[0, 1], fails_array,      "Mutation Failures Over Generations", "Failure Count"),
            (axs[0, 2], success_array,    "Mutation Successes Over Generations", "Success Count"),
            (axs[1, 0], unsuccess_array,  "Mutation Unsuccesses Over Generations", "Unsuccess Count"),
            (axs[1, 1], hashcolition_array, "Mutation Hash Collisions Over Generations", "Hash Collision Count"),
            (axs[1, 2], outofdoe_array, "Mutation Out of DoE Generations", "Out of DoE Count"),
        ]

        for ax, data_array, title, ylabel in plots_info:
            for mutation_idx in range(num_mutations):
                ax.plot(
                    generations,
                    data_array[:, mutation_idx],
                    marker='o',
                    linestyle='-',
                    linewidth=2,
                    label=f"Mutation {mutation_idx + 1}"
                )
            ax.set_title(title, fontsize=14)
            ax.set_xlabel("Generation", fontsize=12)
            ax.set_ylabel(ylabel, fontsize=12)
            ax.grid(True, linestyle='--', alpha=0.6)
            ax.legend(loc="best", fontsize=10)

        plt.tight_layout()

        plot_filename = "mutation_counts_evolution.png"
        full_path = os.path.join(self.output_dir, plot_filename)
        plt.savefig(full_path, dpi=300)
        print(f"Saved plot '{plot_filename}' to: {full_path}")
        plt.close(fig)


    def _plot_crossover_probabilities(self) -> None:
        """
        Plots the evolution of crossover probabilities for each crossover type
        across multiple generations.
        """
        mutation_array = np.array(self.crossover_probabilities)
        if mutation_array.ndim != 2 or mutation_array.shape[0] == 0 or mutation_array.shape[1] == 0:
            print("Invalid crossover_probabilities data. Skipping crossover probabilities plot.")
            return

        num_generations, num_mutations = mutation_array.shape
        generations = np.arange(1, num_generations + 1)

        plt.figure(figsize=(10, 6))
        for m in range(num_mutations):
            plt.plot(
                generations,
                mutation_array[:, m],
                marker='o',
                linestyle='-',
                linewidth=2,
                label=f'Crossover {m + 1}'
            )

        plt.title('Evolution of Crossover Probabilities Over Generations', fontsize=16)
        plt.xlabel('Generation', fontsize=14)
        plt.ylabel('Crossover Probability', fontsize=14)
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.legend(loc='best', fontsize=12)
        plt.tight_layout()

        plot_filename = "mutation_probabilities_evolution.png"
        full_path = os.path.join(self.output_dir, plot_filename)
        plt.savefig(full_path, dpi=300)
        print(f"Saved plot '{plot_filename}' to: {full_path}")
        plt.close()

    def _plot_crossover_counts_evolution(self) -> None:
        """
        Generates a 2×2 grid of subplots to illustrate the evolution of
        crossover attempt counts, failure counts, success counts, and
        unsuccessful counts over the generations.

        Each input is expected to be a 2D list or numpy array of shape (G, N),
        where G is the number of generations and N is the number of crossover types.
        """
        # Convert inputs to numpy arrays for consistent manipulation
        attempt_array = np.array(self.crossover_attempt_counts)
        fails_array = np.array(self.crossover_fails_counts)
        success_array = np.array(self.crossover_success_counts)
        unsuccess_array = np.array(self.crossover_unsuccess_counts)
        hashcolition_array = np.array(self.crossover_hashcolition_counts)
        outofdoe_array = np.array(self.crossover_outofdoe_counts)

        # Validate shapes
        if any(arr.ndim != 2 for arr in [attempt_array, fails_array, success_array, unsuccess_array]):
            print("One or more crossover count arrays have invalid dimensions. Skipping crossover counts plot.")
            return

        if not (
            attempt_array.shape == fails_array.shape ==
            success_array.shape == unsuccess_array.shape
        ):
            print("Mismatch in shape among crossover count arrays. Skipping crossover counts plot.")
            return

        num_generations, num_mutations = attempt_array.shape
        generations = np.arange(1, num_generations + 1)

        # Create a 2x2 grid figure
        fig, axs = plt.subplots(2, 3, figsize=(18, 10))
    
        plots_info = [
            (axs[0, 0], attempt_array,    "Crossover Attempts Over Generations", "Attempt Count"),
            (axs[0, 1], fails_array,      "Crossover Failures Over Generations", "Failure Count"),
            (axs[0, 2], success_array,    "Crossover Successes Over Generations", "Success Count"),
            (axs[1, 0], unsuccess_array,  "Crossover Unsuccesses Over Generations", "Unsuccess Count"),
            (axs[1, 1], hashcolition_array, "Crossover Hash Collisions Over Generations", "Hash Collision Count"),
            (axs[1, 2], outofdoe_array, "Crossover Out of DoE Generations", "Out of DoE Count"),
        ]

        for ax, data_array, title, ylabel in plots_info:
            for mutation_idx in range(num_mutations):
                ax.plot(
                    generations,
                    data_array[:, mutation_idx],
                    marker='o',
                    linestyle='-',
                    linewidth=2,
                    label=f"Crossover {mutation_idx + 1}"
                )
            ax.set_title(title, fontsize=14)
            ax.set_xlabel("Generation", fontsize=12)
            ax.set_ylabel(ylabel, fontsize=12)
            ax.grid(True, linestyle='--', alpha=0.6)
            ax.legend(loc="best", fontsize=10)

        plt.tight_layout()

        plot_filename = "crossover_counts_evolution.png"
        full_path = os.path.join(self.output_dir, plot_filename)
        plt.savefig(full_path, dpi=300)
        print(f"Saved plot '{plot_filename}' to: {full_path}")
        plt.close(fig)

    def _plot_model_evolution_info(self) -> None:
        """
        Plots the evolution of surrogate model information over generations.
        This includes:
          - Predicted Feature Norm vs. Generation
          - Average Recommended Feature Norm vs. Generation
          - Average Acquisition Value vs. Generation
          - Active Model vs. Generation (categorical)
        """
        gens = []
        pred_norms = []
        rec_norms = []
        acq_means = []
        active_models = []
        for gen in sorted(self.model_evolution_info_history.keys()):
            info = self.model_evolution_info_history[gen]
            gens.append(gen)
            # Compute norm for predicted features
            pred_feat = info.get("predicted_features", None)
            if pred_feat is not None and isinstance(pred_feat, list) and len(pred_feat) > 0:
                norm_val = np.linalg.norm(np.array(pred_feat))
            else:
                norm_val = np.nan
            pred_norms.append(norm_val)
            # Compute average norm for recommended features
            rec_feats = info.get("recommended_features", [])
            if rec_feats and isinstance(rec_feats, list):
                norms = [np.linalg.norm(np.array(feat)) for feat in rec_feats if feat is not None]
                avg_norm = np.mean(norms) if norms else np.nan
            else:
                avg_norm = np.nan
            rec_norms.append(avg_norm)
            # Average acquisition value
            acq_vals = info.get("acquisition_values", [])
            if acq_vals and isinstance(acq_vals, list):
                acq_mean = np.mean(acq_vals)
            else:
                acq_mean = np.nan
            acq_means.append(acq_mean)
            # Active model (categorical)
            active_models.append(info.get("active_model", "unknown"))

        # Plot Predicted Feature Norm
        plt.figure()
        plt.plot(gens, pred_norms, '-o', color='blue', linewidth=2)
        plt.xlabel("Generation")
        plt.ylabel("Predicted Feature Norm")
        plt.title("Predicted Feature Norm vs. Generation")
        plot_filename = "predicted_feature_norm_vs_generation.png"
        full_path = os.path.join(self.output_dir, plot_filename)
        plt.savefig(full_path, dpi=300)
        print(f"Saved plot '{plot_filename}' to: {full_path}")
        plt.close()

        # Plot Average Recommended Feature Norm
        plt.figure()
        plt.plot(gens, rec_norms, '-o', color='green', linewidth=2)
        plt.xlabel("Generation")
        plt.ylabel("Avg Recommended Feature Norm")
        plt.title("Avg Recommended Feature Norm vs. Generation")
        plot_filename = "avg_recommended_feature_norm_vs_generation.png"
        full_path = os.path.join(self.output_dir, plot_filename)
        plt.savefig(full_path, dpi=300)
        print(f"Saved plot '{plot_filename}' to: {full_path}")
        plt.close()

        # Plot Average Acquisition Value
        plt.figure()
        plt.plot(gens, acq_means, '-o', color='red', linewidth=2)
        plt.xlabel("Generation")
        plt.ylabel("Avg Acquisition Value")
        plt.title("Avg Acquisition Value vs. Generation")
        plot_filename = "avg_acquisition_value_vs_generation.png"
        full_path = os.path.join(self.output_dir, plot_filename)
        plt.savefig(full_path, dpi=300)
        print(f"Saved plot '{plot_filename}' to: {full_path}")
        plt.close()

        # Plot Active Model vs Generation (categorical)
        unique_models = list(set(active_models))
        model_to_code = {model: idx for idx, model in enumerate(unique_models)}
        codes = [model_to_code[model] for model in active_models]
        plt.figure()
        plt.scatter(gens, codes, c=codes, cmap='Set1', s=100)
        plt.xlabel("Generation")
        plt.ylabel("Active Model")
        plt.title("Active Surrogate Model vs. Generation")
        plt.yticks(list(model_to_code.values()), list(model_to_code.keys()))
        plot_filename = "active_model_vs_generation.png"
        full_path = os.path.join(self.output_dir, plot_filename)
        plt.savefig(full_path, dpi=300)
        print(f"Saved plot '{plot_filename}' to: {full_path}")
        plt.close()

    def generate_all_plots(self, logger_dir:str='.', output_dir:str='.') -> None:
        """
        Main entry point to parse all JSON logs and generate the complete
        suite of evolutionary plots. All figures are saved as PNG files
        in self.output_dir.
        """
        self.output_dir = output_dir
        self.logger_dir = logger_dir
        os.makedirs(self.output_dir, exist_ok=True)

        # 1) Parse logs
        self._parse_json_logs()

        # If no logs were found, abort
        if not self.generations:
            print(f"No generation data loaded at {logger_dir}. Aborting all plots.")
            return

        # 2) Generate each plot in turn
        self._plot_objectives_vs_generation_history()
        #self._plot_objectives_vs_1d_pca()
        self._plot_stall_and_dataset_size()
        self._plot_mean_min_objectives_and_features()
        self._plot_2d_pca_heatmaps()
        self._plot_mutation_rate_series()

        self._plot_execution_times()
        self._plot_mutation_probabilities()
        self._plot_mutation_counts_evolution()
        self._plot_crossover_probabilities()
        self._plot_crossover_counts_evolution()
        self._plot_model_evolution_info()

        print(f"All evolution plots have been successfully saved to '{self.output_dir}'.")

# -----------------------------------------------------------------------------
# Example usage in your main function (pseudocode):
#
# def main():
#     partition_path = "some_partition"
#     output_path = "some_root_output"
#     
#     logger_dir = f"{output_path}/{partition_path}/logger"
#     plot_dir   = f"{output_path}/{partition_path}/plot"
#     
#     plotter = EvolutionPlotter(logger_dir, plot_dir)
#     plotter.generate_all_plots()
#
# if __name__ == "__main__":
#     main()
# -----------------------------------------------------------------------------

