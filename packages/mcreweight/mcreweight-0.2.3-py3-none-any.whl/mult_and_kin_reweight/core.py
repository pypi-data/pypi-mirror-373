from .io import load_data, def_aliases, save_data, flatten_vars
from .train import train_and_test, gbreweight, kfolding, binning_reweight, optuna_tuning
from .config import X_LABELS
from utils.plotting_utils import plot_distributions, plot_mc_distributions, plot_correlation_matrix, plot_roc_curve, plot_classifier_output, plot_weight_distributions
import joblib
import numpy as np

def run_reweighting_pipeline(args, plotdir, weightsdir):
    """
    Main function to run the reweighting pipeline.

    Args:
        args (argparse.Namespace): Command line arguments containing paths, variables, and other parameters.
        plotdir (str): Directory to save plots.
        weightsdir (str): Directory to save weights.
    """
    # Load data
    vars_list = args.vars
    if args.monitoring_vars is not None:
        vars_list.extend(v for v in args.monitoring_vars if v not in vars_list)
    data, sweights = load_data(path=args.path_data, tree=args.tree_data, columns=vars_list, weights_col=args.sweights_name)
    mc, mc_weights = load_data(path=args.path_mc, tree=args.tree_mc, columns=vars_list, weights_col=args.mcweights_name)

    # Plot correlations
    print("Plotting correlation matrices...")
    plot_correlation_matrix(df=data, columns=args.vars, weights=sweights, output_file=f"{plotdir}/corr_data.png", title=args.data_label)
    plot_correlation_matrix(df=mc, columns=args.vars, weights=mc_weights, output_file=f"{plotdir}/corr_mc.png", title=args.mc_label)

    # Train and test split and plot distributions
    mc_train, mc_test, w_mc_train, w_mc_test, data_train, data_test, w_data_train, w_data_test = train_and_test(mc=mc, data=data, mcweights=mc_weights, sweights=sweights, columns=vars_list, test_size=args.test_size)

    print("Plotting original distributions...")
    plot_distributions(mc=mc_train, data=data_train, mc_weights=w_mc_train, data_weights=w_data_train, columns=args.vars, x_labels=X_LABELS, output_file=f"{plotdir}/input_features_training.png")
    plot_distributions(mc=mc_test, data=data_test, mc_weights=w_mc_test, data_weights=w_data_test, columns=args.vars, x_labels=X_LABELS, output_file=f"{plotdir}/input_features_testing.png")
    if args.monitoring_vars is not None:
        plot_distributions(mc=mc_train, data=data_train, mc_weights=w_mc_train, data_weights=w_data_train, columns=args.monitoring_vars, x_labels=X_LABELS, output_file=f"{plotdir}/other_vars_training.png")
        plot_distributions(mc=mc_test, data=data_test, mc_weights=w_mc_test, data_weights=w_data_test, columns=args.monitoring_vars, x_labels=X_LABELS, output_file=f"{plotdir}/other_vars_testing.png")


    print("Weights for MC and Data samples:")
    print(f"MC weights training: {w_mc_train} and testing: {w_mc_test}")
    print(f"Data weights training: {w_data_train} and testing: {w_data_test}")
   
    # Train the model
    print("Training the classifier...")
    optuna_study = optuna_tuning(mc=mc, data=data, mcweights=mc_weights, sweights=sweights, columns=args.vars, n_trials=args.n_trials, n_folds=args.n_folds, weightsdir=weightsdir)
    gb, gb_weights = gbreweight(mc_train=mc_train, data_train=data_train, mc_test=mc_test, data_test=data_test, w_mc_train=w_mc_train, w_mc_test=w_mc_test, w_data_train=w_data_train, w_data_test=w_data_test, columns=args.vars, study=optuna_study, weightsdir=weightsdir)
    gb_weights_kfolding = kfolding(gb=gb, mc=mc, data=data, w_mc=mc_weights, w_data=sweights, columns=args.vars, n_folds=args.n_folds, weightsdir=weightsdir)
    binning_weights = binning_reweight(mc_train=mc_train, data_train=data_train, mc_test=mc_test, w_mc_train=w_mc_train, w_mc_test=w_mc_test, w_data_train=w_data_train, w_data_test=w_data_test, columns=args.vars, n_bins=args.n_bins, n_neighs=args.n_neighs, weightsdir=weightsdir)
    print("Classifier training complete.")

    # Plot distributions after reweighting
    print("Plotting distributions after reweighting...")
    plot_distributions(mc=mc_test, data=data_test, mc_weights=gb_weights, data_weights=w_data_test, columns=args.vars, x_labels=X_LABELS, output_file=f"{plotdir}/input_features_gb_weighted.png")
    plot_distributions(mc=mc, data=data, mc_weights=gb_weights_kfolding, data_weights=sweights, columns=args.vars, x_labels=X_LABELS, output_file=f"{plotdir}/input_features_kfolding_weighted.png")
    plot_distributions(mc=mc_test, data=data_test, mc_weights=binning_weights, data_weights=w_data_test, columns=args.vars, x_labels=X_LABELS, output_file=f"{plotdir}/input_features_binning_weighted.png")
    if args.monitoring_vars is not None:
        plot_distributions(mc=mc_test, data=data_test, mc_weights=gb_weights, data_weights=w_data_test, columns=args.monitoring_vars, x_labels=X_LABELS, output_file=f"{plotdir}/other_vars_gb_weighted.png")
        plot_distributions(mc=mc, data=data, mc_weights=gb_weights_kfolding, data_weights=sweights, columns=args.monitoring_vars, x_labels=X_LABELS, output_file=f"{plotdir}/other_vars_kfolding_weighted.png")
        plot_distributions(mc=mc_test, data=data_test, mc_weights=binning_weights, data_weights=w_data_test, columns=args.monitoring_vars, x_labels=X_LABELS, output_file=f"{plotdir}/other_vars_binning_weighted.png")

    # ROC curve
    scores_gb, scores_kfolding, scores_binning = plot_roc_curve(mc_test=mc_test, data_test=data_test, 
                                                                w_mc_test=w_mc_test, w_data_test=w_data_test, 
                                                                mc=mc, data=data, w_data=sweights,
                                                                gb_weights=gb_weights, gb_weights_kfolding=gb_weights_kfolding, binning_weights=binning_weights, 
                                                                columns=args.vars, output_file=f"{plotdir}/roc_curve.png")

    # Draw classifier output
    plot_classifier_output(
        score_dict={args.data_label: scores_gb["Data"], f"{args.mc_label} GBReweighted": scores_gb["MC"], f"{args.mc_label} k-folding GBReweighted": scores_kfolding["MC"], f"{args.mc_label} bins-reweighted": scores_binning["MC"]},
        weights_dict={args.data_label: w_data_test, f"{args.mc_label} GBReweighted": gb_weights, f"{args.mc_label} k-folding GBReweighted": gb_weights_kfolding, f"{args.mc_label} bins-reweighted": binning_weights},
        min_score=0., max_score=1., output_file=f"{plotdir}/classifier_output.png"
    )
    
    # Plot weight distributions
    plot_weight_distributions(
        weights_dict={
            "GB": gb_weights,
            "KFold": gb_weights_kfolding,
            "Bins": binning_weights,
        },
        output_file=f"{plotdir}/weight_distributions.png",
        xlim=(0, 10)
    )

def apply_weights_pipeline(args, plotdir, weightsdir):
    """
    Main function to apply weights to the data using the trained model.

    Args:
        args (argparse.Namespace): Command line arguments containing paths, variables, and other parameters.
        plotdir (str): Directory to save plots.
        weightsdir (str): Directory containing weights.
    """
    # Load data
    vars_list = args.vars
    if args.monitoring_vars is not None:
        vars_list.extend(v for v in args.monitoring_vars if v not in vars_list)
    mc, mc_weights = load_data(path=args.path_mc, tree=args.tree_mc, columns=vars_list, weights_col=args.mcweights_name)
    if args.path_data:
        data, sweights = load_data(path=args.path_data, tree=args.tree_data, columns=vars_list, weights_col=args.sweights_name)

    # Define aliases for training variables
    # Each alias should match the training variables used in the classifier with the name of the branch in the mc
    if(len(args.vars) != len(args.training_vars)):
        raise ValueError("The number of variables for reweighting must match the number of training variables."
                        " Please check the --vars and --training_vars arguments.")

    aliases = dict(zip(args.training_vars, args.vars))

    mc = def_aliases(mc, aliases)

    saving_vars = flatten_vars(args.training_vars)

    # Load method and weights
    print("Loading model and weights...")
    if args.method == "gbreweighter":
     classifier = joblib.load(f"{weightsdir}/gb_model_" + "_".join(saving_vars) + ".pkl")
    elif args.method == "kfolding":
        classifier = joblib.load(f"{weightsdir}/gb_kfolding_model_" + "_".join(saving_vars) + ".pkl") 
    elif args.method == "binning":
        classifier = joblib.load(f"{weightsdir}/binning_model_" + "_".join(saving_vars) + ".pkl")
    else:
        raise ValueError(f"Unknown model type: {args.method}. Currently supported methods are 'gbreweighter', 'kfolding', and 'binning'.")

    # Apply weights
    print("Applying weights to MC data...")
    #progress_thread.start()
    new_mc_weights = classifier.predict_weights(mc[args.vars])
    w_normalized = new_mc_weights * (len(new_mc_weights) / np.sum(new_mc_weights))
    #stop_event.set()
    #progress_thread.join()
    print("Weights predicted successfully.")
    joblib.dump(w_normalized, f"{weightsdir}/mcweights_" + "_".join(args.vars) + ".pkl")

    # Plot distributions after applying weights
    print("Plotting distributions after applying weights...")
    plot_mc_distributions(mc=mc, original_mc_weights=mc_weights, new_mc_weights=w_normalized, columns=args.vars, x_labels=X_LABELS, output_file=f"{plotdir}/mc_vars_reweighting.png")
    if args.monitoring_vars is not None: 
        plot_mc_distributions(mc=mc, original_mc_weights=mc_weights, new_mc_weights=w_normalized, columns=args.monitoring_vars, x_labels=X_LABELS, output_file=f"{plotdir}/mc_other_vars_reweighting.png")
    if args.path_data:
        plot_distributions(mc=mc, data=data, mc_weights=w_normalized, data_weights=sweights, columns=args.vars, x_labels=X_LABELS, output_file=f"{plotdir}/input_features_reweighted.png")
        if args.monitoring_vars is not None:
            plot_distributions(mc=mc, data=data, mc_weights=w_normalized, data_weights=sweights, columns=args.monitoring_vars, x_labels=X_LABELS, output_file=f"{plotdir}/other_vars_reweighted.png")


    # Write to output ROOT file
    print("Saving weights to output ROOT file...")
    weights_array = np.array(w_normalized, dtype=np.float32)
    save_data(input_path=args.path_mc, tree=args.tree_mc, output_path=args.output_path, output_tree=args.output_tree, branch=args.weights_name, weights=weights_array)
    