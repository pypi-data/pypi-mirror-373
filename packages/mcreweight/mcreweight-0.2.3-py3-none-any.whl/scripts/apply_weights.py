import argparse
from os import makedirs
from mult_and_kin_reweight.core import apply_weights_pipeline

def main():
    parser = argparse.ArgumentParser()

    # Input MC
    parser.add_argument("--path_mc", required=True, help="Path to the MC signal sample")
    parser.add_argument("--tree_mc", default="DecayTree", help="Name of the tree in the MC signal sample")
    parser.add_argument("--mcweights_name", default=None, help="Name of the branch for weights in the output ROOT file")
    parser.add_argument("--path_data", default=None, help="Path to the data sample for comparison")
    parser.add_argument("--tree_data", default="DecayTree", help="Name of the tree in the data sample")
    parser.add_argument("--sweights_name", default="sweight_sig", help="Name of the sweights column in the data sample")

    # List of variables
    parser.add_argument("--vars", nargs='+', default=["B_DTF_Jpsi_P", "B_DTF_Jpsi_PT", "nLongTracks", "nPVs"], 
                        help="List of variables to use for reweighting")
    parser.add_argument("--training_vars", nargs='+', default=["B_DTF_Jpsi_P", "B_DTF_Jpsi_PT", "nLongTracks", "nPVs"], 
                        help="List of variables used for training")
    parser.add_argument("--monitoring_vars", nargs='+', default=None,
                        help="List of variables to plot")

    # Configuration of reweighter to apply
    parser.add_argument("--training_sample", default="bd_jpsikst_ee", help="Sample name for the dataset")
    parser.add_argument("--application_sample", default="bd_jpsikst_ee", help="Sample name for the application of weights")
    parser.add_argument("--method", choices=["gbreweighter", "kfolding", "binning"], default="gbreweighter", help="Method to apply weights")
    parser.add_argument("--weightsdir", default="weights", help="Directory to save weights")
    parser.add_argument("--plotdir", default="plots", help="Directory to save plots")

    # Output
    parser.add_argument("--output_path", required=True, help="Path to save the output ROOT file")
    parser.add_argument("--output_tree", default="DecayTree", help="Name of the tree in the output ROOT file")
    parser.add_argument("--weights_name", default="weights", help="Name of the weights branch in the output ROOT file")

    args = parser.parse_args()
    plotdir = f"{args.plotdir}/{args.application_sample}"
    weightsdir = f"{args.weightsdir}/{args.training_sample}"

    if not weightsdir:
        raise ValueError("Weights directory must exist.")
    makedirs(plotdir, exist_ok=True)
    # Run the apply weights pipeline
    apply_weights_pipeline(args, plotdir=plotdir, weightsdir=weightsdir)
    
if __name__ == "__main__":
    main()
