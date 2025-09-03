from os import makedirs
import argparse
from mult_and_kin_reweight.core import run_reweighting_pipeline

def main():
    parser = argparse.ArgumentParser()

    # Inputs
    parser.add_argument("--path_data", required=True, help="Path to the data control sample")
    parser.add_argument("--tree_data", default="DecayTree", help="Name of the tree in the data control sample")
    parser.add_argument("--path_mc", required=True, help="Path to the MC control sample")
    parser.add_argument("--tree_mc", default="DecayTree", help="Name of the tree in the MC control sample")
    parser.add_argument("--mcweights_name", default=None, help="Name of the branch for weights in the MC sample")
    parser.add_argument("--sweights_name", default="sweight_sig", help="Name of the sweights column in the data")
    parser.add_argument("--mc_label", default="MC", help="Label for the MC sample")
    parser.add_argument("--data_label", default="Data", help="Label for the data sample") 

    # List of variables
    parser.add_argument("--vars", nargs='+', default=["B_DTF_Jpsi_P", "B_DTF_Jpsi_PT", "nLongTracks", "nPVs"], 
                        help="List of variables to use for reweighting")
    parser.add_argument("--monitoring_vars", nargs='+', default=None,
                        help="List of variables to plot")

    # Reweighter configuration
    parser.add_argument("--sample", default="bd_jpsikst_ee", help="Sample name for the dataset")
    parser.add_argument("--n_trials", type=int, default=10, help="Number of trials for the gradient boosting reweighting")
    parser.add_argument("--test_size", type=float, default=0.3, help="Proportion of the dataset to include in the test split")
    parser.add_argument("--n_folds", type=int, default=10, help="Number of folds for k-folding reweighting")
    parser.add_argument("--n_bins", type=int, default=10, help="Number of bins for binning reweighting")
    parser.add_argument("--n_neighs", type=int, default=3, help="Number of nearest neighbors for binning reweighting")

    # Output
    parser.add_argument("--weightsdir", default="weights", help="Directory to save weights")
    parser.add_argument("--plotdir", default="plots", help="Directory to save plots")

    args = parser.parse_args()
    plotdir = f"{args.plotdir}/{args.sample}"
    weightsdir = f"{args.weightsdir}/{args.sample}"

    # Create directories if they do not exist
    makedirs(weightsdir, exist_ok=True)
    makedirs(plotdir, exist_ok=True)

    # Run the reweighting pipeline
    run_reweighting_pipeline(args, plotdir=plotdir, weightsdir=weightsdir)

if __name__ == "__main__":
    main()
