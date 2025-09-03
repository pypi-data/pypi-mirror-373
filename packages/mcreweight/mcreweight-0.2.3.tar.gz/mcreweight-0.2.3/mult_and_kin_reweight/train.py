from hep_ml import reweight
from sklearn.model_selection import train_test_split
import joblib
from utils.utils import run_optuna
import numpy as np
from .io import flatten_vars

def train_and_test(mc, data, mcweights, sweights, columns, test_size):
    """
    Split the data into training and testing sets.

    Args:
        mc (pd.DataFrame): MC data.
        data (pd.DataFrame): Data to reweight to.
        mcweights (np.ndarray): Weights for the MC data.
        sweights (np.ndarray): Sweights for the data.
        columns (list): List of column names to use for training.
        test_size (float): Proportion of the dataset to include in the test split.
    
    Returns:
        mc_train, mc_test, w_mc_train, w_mc_test, data_train, data_test, w_data_train, w_data_test: Split datasets and weights.
    """
    mc_train, mc_test, w_mc_train, w_mc_test = train_test_split(mc[columns], mcweights, test_size=test_size, random_state=42)
    data_train, data_test, w_data_train, w_data_test = train_test_split(data[columns], sweights, test_size=test_size, random_state=42)
    return mc_train, mc_test, w_mc_train, w_mc_test, data_train, data_test, w_data_train, w_data_test

def optuna_tuning(mc, data, mcweights, sweights, columns, n_trials, n_folds, weightsdir):
    """
    Run Optuna to optimize hyperparameters for the Gradient Boosting Reweighter.

    Args:
        mc (pd.DataFrame): MC data.
        data (pd.DataFrame): Data to reweight to.
        mcweights (np.ndarray): Weights for the MC data.
        sweights (np.ndarray): Sweights for the data.
        columns (list): List of column names to use for training.
        n_trials (int): Number of trials for hyperparameter optimization.
        n_folds (int): Number of folds for k-folding.
        weightsdir (str): Directory to save the weights and model.
    
    Returns:
        study: Optuna study object containing the results of the optimization.
    """
    saving_vars = flatten_vars(columns)
    study_path = f"{weightsdir}/mult_and_kin_optuna_study_" + "_".join(saving_vars) + ".pkl"
    if joblib.os.path.exists(study_path):
        # Load existing study if it exists
        print(f"Loading existing study from {study_path}")
        study = joblib.load(study_path)
    else:
        # Run Optuna to create a new study
        print(f"Creating new Optuna study and saving to {study_path}")
        if np.all(mcweights == 1):
            mcweights = None
        if np.all(sweights == 1):
            sweights = None
        study = run_optuna(mc=mc, data=data, mcweights=mcweights, sweights=sweights, columns=columns, n_trials=n_trials, n_folds=n_folds)
        joblib.dump(study, study_path)
    return study

def gbreweight(mc_train, data_train, mc_test, data_test, w_mc_train, w_mc_test, w_data_train, w_data_test, columns, study, weightsdir):
    """
    Optimize hyperparameters using Optuna and train the Gradient Boosting Reweighter.

    Args:
        mc_train (pd.DataFrame): MC data for training.
        data_train (pd.DataFrame): Data to reweight to.
        mc_test (pd.DataFrame): MC data for testing.
        data_test (pd.DataFrame): Data to test against.
        w_mc_train (np.ndarray): weights for the training MC.
        w_mc_test (np.ndarray): weights for the test MC.
        w_data_train (np.ndarray): Sweights for the training data.
        w_data_test (np.ndarray): Sweights for the test data.
        columns (list): List of column names to use for training.
        study (optuna.Study): Optuna study object containing the results of the optimization.
        weightsdir (str): Directory to save the weights and model.
        test_size (float): Proportion of the dataset to include in the test split.
    Returns:
        gb (reweight.GBReweighter): Trained Gradient Boosting Reweighter.
        gb_weights (np.ndarray): Weights predicted by the trained model.
    """
    # NOTE: Treating weights as None if they are all 1
    # This is to avoid issues with the reweighter when all weights are uniform
    if np.all(w_mc_test == 1) and np.all(w_mc_train == 1):
        w_mc_test = None
        w_mc_train = None
    if np.all(w_data_test == 1) and np.all(w_data_train == 1):
        w_data_test = None
        w_data_train = None

    best = study.best_params
    gb = reweight.GBReweighter(
        n_estimators=best["n_estimators"],
        learning_rate=best["learning_rate"],
        max_depth=best["max_depth"],
        min_samples_leaf=best["min_samples_leaf"],
        gb_args={"subsample": best["subsample"]}
    )
    print(f"Training GBReweighter with parameters: {best}")
    gb.fit(mc_train[columns], data_train[columns], original_weight=w_mc_train, target_weight=w_data_train)
    new_mc_weights = gb.predict_weights(mc_test[columns])
    saving_vars = flatten_vars(columns)
    joblib.dump(gb, f"{weightsdir}/gb_model_" + "_".join(saving_vars) + ".pkl")
    joblib.dump(new_mc_weights, f"{weightsdir}/gb_weights_" + "_".join(saving_vars) + ".pkl")
    return gb, new_mc_weights

def kfolding(gb, mc, data, w_mc, w_data, columns, n_folds, weightsdir):
    """
    Perform k-folding reweighting using the trained Gradient Boosting model.

    Args:
        gb (reweight.GBReweighter): Trained Gradient Boosting Reweighter.
        mc (pd.DataFrame): MC data.
        data (pd.DataFrame): Data to reweight to.
        w_mc (np.ndarray): Weights for the MC data.
        w_data (np.ndarray): Sweights for the data.
        columns (list): List of column names to use for reweighting.
        n_folds (int): Number of folds for k-folding.
        weightsdir (str): Directory to save the weights and model.
    
    Returns:
        gb_weights_kfolding (np.ndarray): Weights for the MC data after k-folding reweighting.
    """
    # NOTE: Treating weights as None if they are all 1
    # This is to avoid issues with the reweighter when all weights are uniform
    if np.all(w_mc == 1):
        w_mc = None
    if np.all(w_data == 1):
        w_data = None
    gb_kfolding = reweight.FoldingReweighter(gb, n_folds=n_folds)
    gb_kfolding.fit(mc[columns], data[columns], original_weight=w_mc, target_weight=w_data)
    gb_weights_kfolding = gb_kfolding.predict_weights(mc[columns])
    saving_vars = flatten_vars(columns)
    joblib.dump(gb_kfolding, f"{weightsdir}/gb_kfolding_model_" + "_".join(saving_vars) + ".pkl")
    joblib.dump(gb_weights_kfolding, f"{weightsdir}/gb_weights_kfolding_" + "_".join(saving_vars) + ".pkl")
    return gb_weights_kfolding

def binning_reweight(mc_train, data_train, mc_test, w_mc_train, w_mc_test, w_data_train, w_data_test, columns, n_bins, n_neighs, weightsdir):
    """
    Perform binning reweighting on the provided MC and Data samples.

    Args:
        mc_train (pd.DataFrame): MC data for training.
        data_train (pd.DataFrame): Data used for training.
        mc_test (pd.DataFrame): MC data for testing.
        w_mc_train (np.ndarray): Weights for the training MC data.
        w_mc_test (np.ndarray): Weights for the test MC data.
        w_data_train (np.ndarray): Sweights for the training data.
        w_data_test (np.ndarray): Sweights for the test data.
        columns (list): List of column names to use for reweighting.
        n_bins (int): Number of bins to use for reweighting.
        n_neighs (int): Number of nearest neighbors to consider for reweighting.
        weightsdir (str): Directory to save the weights and model.
    Returns:
        new_mc_weights (np.ndarray): Weights for the MC data after reweighting.
    """
    # NOTE: Treating weights as None if they are all 1
    # This is to avoid issues with the reweighter when all weights are uniform
    if np.all(w_mc_test == 1) and np.all(w_mc_train == 1):
        w_mc_test = None
        w_mc_train = None
    if np.all(w_data_test == 1) and np.all(w_data_train == 1):
        w_data_test = None
        w_data_train = None
    bins = reweight.BinsReweighter(n_bins=n_bins, n_neighs=n_neighs)
    bins.fit(mc_train[columns], data_train[columns], original_weight=w_mc_train, target_weight=w_data_train)
    new_mc_weights = bins.predict_weights(mc_test[columns])
    saving_vars = flatten_vars(columns)
    joblib.dump(bins, f"{weightsdir}/binning_model_" + "_".join(saving_vars) + ".pkl")
    joblib.dump(new_mc_weights, f"{weightsdir}/binning_weights_" + "_".join(saving_vars) + ".pkl")
    return new_mc_weights