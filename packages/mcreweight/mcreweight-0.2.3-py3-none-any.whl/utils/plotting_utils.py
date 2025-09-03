import numpy as np
import matplotlib.pyplot as plt
import math
from hep_ml.metrics_utils import ks_2samp_weighted
from utils.utils import evaluate_reweighting, weighted_corr_matrix
import seaborn as sns

hist_settings = {"bins": 50, "density": True, "alpha": 0.7}
plt.rcParams.update({
    'axes.titlesize': 20,
    'axes.labelsize': 18,
    'xtick.labelsize': 16,
    'ytick.labelsize': 16,
    'legend.fontsize': 16
})

def plot_correlation_matrix(df, columns, weights, title, output_file):
    """
    Plot a correlation matrix for the given DataFrame columns.

    Args:
        df (pd.DataFrame): DataFrame containing the data.
        columns (list): List of column names to include in the correlation matrix.
        weights (np.ndarray, optional): Weights for the correlation calculation. If None, unweighted correlation is used.
        title (str): Title of the plot.
        output_file (str): Path to save the output plot.
    """
    corr = weighted_corr_matrix(df, columns, weights) if weights is not None else df[columns].corr()
    plt.figure(figsize=(16, 12))
    sns.heatmap(
        corr,
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        square=True,
        cbar_kws={"shrink": .75},
        xticklabels=columns,
        yticklabels=columns,
        annot_kws={"size": 16}  # Increase annotation font size
    )
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)
    plt.title(title)
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()

def plot_distributions(mc, data, mc_weights, data_weights, columns, x_labels, output_file, x_edges=None):
    """
    Plot distributions with pulls of multiple columns from MC and Data samples.
    The main distribution plot is twice as large as the pull plot, and histograms are normalized as densities.

    Args:
        mc (pd.DataFrame): MC data.
        data (pd.DataFrame): Data to compare against.
        mc_weights (np.ndarray): Weights for the MC data.
        data_weights (np.ndarray): Weights for the Data.
        columns (list): List of column names to plot.
        x_labels (dict): Dictionary mapping column names to x-axis labels.
        output_file (str): Path to save the output plot.
        x_edges (dict, optional): Dictionary mapping column names to bin edges for histogramming.
    
    Raises:
        ValueError: If inputs are invalid or columns are not found in DataFrames.
    """
    hist_settings = dict(bins=50, histtype="step", linewidth=1.5)
    n_cols = 3 if len(columns) != 4 else 2
    if len(columns) >= 10:
        n_cols = 5
    n_rows = math.ceil(len(columns) / n_cols)

    # Create figure and axes with custom height ratios (2:1 for main:pull)
    fig, axes = plt.subplots(n_rows * 2, n_cols, figsize=(8 * n_cols, 5 * n_rows), 
                             gridspec_kw={'height_ratios': [2, 1] * n_rows}, 
                             constrained_layout=True)
    axes = np.array(axes).reshape(n_rows * 2, n_cols) if n_rows * n_cols > 1 else np.array([[axes[0]], [axes[1]]])

    for idx, column in enumerate(columns):
        row = (idx // n_cols) * 2
        col = idx % n_cols

        # Determine binning
        if x_edges and column in x_edges:
            bins = x_edges[column]
        else:
            # Use quantiles to avoid outliers, ensure valid range
            xlim = np.percentile(np.hstack([mc[column].dropna(), data[column].dropna()]), [0.01, 99.99])
            if xlim[0] == xlim[1]:  # Handle case where data is constant
                xlim[1] = xlim[0] + 1e-10
            bins = np.linspace(xlim[0], xlim[1], hist_settings['bins'] + 1)

        # Filter out NaN values and corresponding weights
        mc_valid = mc[column].notna()
        data_valid = data[column].notna()

        # Compute normalized histograms (density=True)
        bin_widths = np.diff(bins)
        mc_vals, _ = np.histogram(mc[column][mc_valid], bins=bins, weights=mc_weights[mc_valid], density=True)
        data_vals, _ = np.histogram(data[column][data_valid], bins=bins, weights=data_weights[data_valid], density=True)
        # Compute variances for error bars (not normalized for pulls)
        mc_var, _ = np.histogram(mc[column][mc_valid], bins=bins, weights=mc_weights[mc_valid]**2)
        data_var, _ = np.histogram(data[column][data_valid], bins=bins, weights=data_weights[data_valid]**2)

        # Calculate pulls using normalized histograms
        bin_centers = 0.5 * (bins[:-1] + bins[1:])
        total_unc = np.sqrt(mc_var + data_var) / (bin_widths * np.sum(mc_weights[mc_valid]))  # Scale variance appropriately
        pulls = np.divide(data_vals - mc_vals, total_unc, out=np.zeros_like(data_vals, dtype=float), where=total_unc > 0)

        # Main plot
        ax_main = axes[row, col]
        step_settings = {k: v for k, v in hist_settings.items() if k not in ['bins', 'histtype']}
        ax_main.step(bin_centers, mc_vals, label="MC", where='mid', **step_settings)
        ax_main.errorbar(bin_centers, data_vals, yerr=np.sqrt(data_var) / (bin_widths * np.sum(data_weights[data_valid])), 
                 fmt='o', label="Data", capsize=3)
        ax_main.set_ylabel("A.U.")
        ax_main.legend()
        ax_main.grid(True, alpha=0.3)
        ax_main.set_xticklabels([])  # Hide x-tick labels on main plot to bring pull plot visually closer

        # Pull plot
        ax_pull = axes[row + 1, col]
        ax_pull.axhline(0, color='gray', linestyle='--')
        ax_pull.bar(bin_centers, pulls, width=bin_widths, align='center', color='tab:red', alpha=0.6)
        ax_pull.set_ylabel("Pull")
        ax_pull.set_xlabel(x_labels.get(column, column))
        ax_pull.grid(True, alpha=0.3)

    # Hide unused subplots
    for i in range(len(columns) * 2, axes.size):
        axes.flat[i].axis('off')

    # Save and close
    plt.savefig(output_file, bbox_inches="tight", dpi=300)
    plt.close(fig)

def plot_mc_distributions(mc, original_mc_weights, new_mc_weights, columns, x_labels, output_file, x_edges=None):
    """
    Plot distributions of MC data with weights.

    Args:
        mc (pd.DataFrame): MC data.
        original_mc_weights (np.ndarray): Original weights for the MC data.
        new_mc_weights (np.ndarray): Weights for the MC data.
        columns (list): List of column names to plot.
        x_labels (dict): Dictionary mapping column names to x-axis labels.
        output_file (str): Path to save the output plot.
        x_edges (dict, optional): Dictionary mapping column names to bin edges for histogramming.
    """
    hist_settings = dict(bins=50, histtype="step", linewidth=1.5)
    n_cols = 3 if len(columns) != 4 else 2
    if len(columns) >= 10:
        n_cols = 5
    n_rows = math.ceil(len(columns) / n_cols)

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(8*n_cols, 5*n_rows), constrained_layout=True)
    if isinstance(axes, np.ndarray):
        axes = axes.reshape(n_rows, n_cols)

    for idx, column in enumerate(columns):
        row = idx // n_cols
        col = idx % n_cols

        # Determine binning
        if x_edges and column in x_edges:
            bins = x_edges[column]
        else:
            xlim = np.percentile(mc[column], [0.01, 99.99])
            bins = np.linspace(xlim[0], xlim[1], hist_settings['bins'] + 1)

        # Histogramming
        hist_orig, _ = np.histogram(mc[column], bins=bins, weights=original_mc_weights)
        hist_new, _ = np.histogram(mc[column], bins=bins, weights=new_mc_weights)

        bin_centers = 0.5 * (bins[:-1] + bins[1:])

        ax_main = axes[row, col]
        step_settings = {k: v for k, v in hist_settings.items() if k not in ['bins', 'histtype']}
        ax_main.step(bin_centers, hist_orig, where='mid', label='Original MC', **step_settings)
        ax_main.step(bin_centers, hist_new, where='mid', label='Reweighted MC', linestyle='--', **step_settings)
        ax_main.set_ylabel("A.U.")
        ax_main.set_xlabel(x_labels.get(column, column))
        ax_main.legend()

    # Hide unused subplots
    total_plots = len(columns)
    for i in range(total_plots, axes.shape[0] * axes.shape[1]):
        axes.flat[i].axis('off')

    plt.savefig(output_file, bbox_inches="tight")
    plt.close()

def plot_roc_curve(mc_test, mc, data_test, data, w_mc_test, w_data, w_data_test, gb_weights, gb_weights_kfolding, binning_weights, columns, output_file):
    """
    Plot ROC curve for the different reweighting methods.
    
    Args:
        mc_test (pd.DataFrame): MC testing sample.
        mc (pd.DataFrame): MC sample.
        data_test (pd.DataFrame): Data testing sample.
        data (pd.DataFrame): Data sample.
        w_mc_test (np.ndarray): Weights for the MC testing sample.
        w_data (np.ndarray): sWeights for the Data.
        w_data_test (np.ndarray): sWeights for the Data testing sample.
        gb_weights (np.ndarray): Weights predicted by the trained model.
        gb_weights_kfolding (np.ndarray): Weights from k-folding reweighting.
        binning_weights (np.ndarray): Weights from binning reweighting.
        columns (list): List of column names to use for plotting.
        output_file (str): Path to save the output plot.
    
    Returns:
        scores_gb, scores_kfolding, scores_binning (dict): Dictionaries containing classifier scores for each method.
    """
    fig, ax = plt.subplots(figsize=(16, 12))

    evaluate_reweighting(
        mc_test[columns].values, data_test[columns].values,
        w_mc_test, w_data_test, 
        "Unweighted", ax, {"MC": None, "Data": None}
    )

    scores_gb = {}
    evaluate_reweighting(
        mc_test[columns].values, data_test[columns].values,
        gb_weights, w_data_test,
        "GBReweighter", ax, scores_gb
    )

    scores_kfolding = {}
    evaluate_reweighting(
        mc[columns].values, data[columns].values,
        gb_weights_kfolding, w_data,
        "k-Folding GBReweighter", ax, scores_kfolding
    )

    scores_binning = {}
    evaluate_reweighting(
        mc_test[columns].values, data_test[columns].values,
        binning_weights, w_data_test,
        "BinsReweighter", ax, scores_binning
    )

    ax.plot([0, 1], [0, 1], linestyle='--', color='gray', label='Random')
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title("ROC Curve: Classifier distinguishing reweighted MC from Data")
    ax.legend(loc="lower right")
    plt.savefig(output_file)
    print(f"ROC curve saved to: {output_file}")
    plt.close()
    
    return scores_gb, scores_kfolding, scores_binning

def plot_classifier_output(score_dict, weights_dict, min_score, max_score, output_file):
    """
    Plot the classifier output distributions for different labels and add KS test values in legend.

    Args:
        score_dict (dict): Dictionary where keys are labels and values are lists of classifier scores.
        weights_dict (dict): Dictionary where keys are labels and values are weights for the scores.
        min_score (float): Minimum score to consider for the plot.
        max_score (float): Maximum score to consider for the plot.
        output_file (str): Path to save the output plot.
    """
    plt.figure(figsize=(16, 12))
    
    # Reference = Data
    score_data = score_dict.get("Data")
    weights_data = weights_dict.get("Data")

    for label, score in score_dict.items():
        w = weights_dict[label]
        if label == "Data":
            # Plot Data normally
            legend_label = "Data"
        else:
            # Compute KS vs. Data
            ks_val = ks_2samp_weighted(score, score_data, weights1=w, weights2=weights_data)
            legend_label = f"{label} (KS = {ks_val:.3f})"
        
        plt.hist(score, bins=50, density=True, weights=w, alpha=0.6, label=legend_label, range=(min_score, max_score))

    plt.xlabel("Classifier output")
    plt.ylabel("Density")
    plt.title("Classifier score distribution with KS values")
    plt.legend()
    plt.savefig(output_file, bbox_inches="tight")
    print(f"Classifier output plot saved to: {output_file}")
    plt.close()

def plot_weight_distributions(weights_dict, output_file, bins=50, xlim=None):
    """
    Plot histograms of weight distributions.

    Args:
        weights_dict (dict): Dictionary where keys are labels and values are arrays of weights.
        output_file (str): Output file path for the plot.
        bins (int): Number of histogram bins.
        xlim (tuple or None): Limit for the x-axis, e.g., (0, 5). Default: auto.
    """
    plt.figure(figsize=(10, 7))
    for label, weights in weights_dict.items():
        plt.hist(weights, bins=bins, density=True, alpha=0.6, label=label, range=xlim, histtype="stepfilled")
    
    plt.xlabel("weights")
    plt.ylabel("Density")
    plt.legend()
    if xlim:
        plt.xlim(xlim)
    plt.yscale("log")  # Helps visualize long tails
    plt.grid(True, which="both", linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(output_file)
    print(f"Weight distributions plot saved to: {output_file}")
    plt.close()