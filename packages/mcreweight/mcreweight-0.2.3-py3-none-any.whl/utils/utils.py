import numpy as np
import pandas as pd
import optuna
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import roc_curve, auc, roc_auc_score
from hep_ml import reweight

def evaluate_reweighting(mc, data, weights_mc, weights_data, label, ax, score_dict=None):
    """
    Evaluate the reweighting performance using ROC curve and AUC.

    Args:
        mc (np.ndarray): MC data features.
        data (np.ndarray): Data features.
        weights_mc (np.ndarray): Weights for MC data.
        weights_data (np.ndarray): Weights for Data.
        label (str): Label for the plot.
        ax (matplotlib.axes.Axes): Axes to plot the ROC curve on.
        score_dict (dict, optional): Dictionary to store scores for MC and Data.
    """
    X = np.vstack([mc, data])
    y = np.hstack([np.zeros(len(mc)), np.ones(len(data))])
    sample_weight = np.hstack([weights_mc, weights_data])

    clf = GradientBoostingClassifier(n_estimators=50, max_depth=3)
    clf.fit(X, y, sample_weight=sample_weight)
    y_scores = clf.predict_proba(X)[:, 1]

    if score_dict is not None:
        score_dict["MC"] = y_scores[:len(mc)]
        score_dict["Data"] = y_scores[len(mc):]

    fpr, tpr, _ = roc_curve(y, y_scores, sample_weight=sample_weight)
    auc_val = auc(fpr, tpr)
    if ax is not None:
        ax.plot(fpr, tpr, label=f"{label} (AUC = {auc_val:.3f})")
    return auc_val

def weighted_corr_matrix(df, columns, weights):
    """Compute (weighted) correlation matrix for a DataFrame.
    
    Args:
        df (pd.DataFrame): DataFrame containing the data.
        columns (list): List of column names to include in the correlation matrix.
        weights (np.ndarray, optional): Weights for the correlation calculation. 
    """
    data = df[columns].values
    weights = np.asarray(weights)

    # Weighted mean
    mean = np.average(data, axis=0, weights=weights)

    # Weighted covariance matrix (signed weights)
    xm = data - mean
    cov = np.dot(weights * xm.T, xm) / np.sum(weights)

    # Standard deviations
    stddev = np.sqrt(np.diag(cov))

    # Correlation matrix
    corr = cov / np.outer(stddev, stddev)
    corr = np.clip(corr, -1, 1)  # ensure numerical stability

    return pd.DataFrame(corr, index=columns, columns=columns)

def run_optuna(mc, data, mcweights, sweights,  columns, n_folds, n_trials):
    """    
    Run Optuna hyperparameter optimization for Gradient Boosting Reweighter.

    Args:
        mc (pd.DataFrame): MC data for training.
        data (pd.DataFrame): Data to reweight to.
        mcweights (np.ndarray): Weights for the training MC.
        sweights (np.ndarray): Sweights for the training data.
        columns (list): List of column names to use for training.
        n_folds (int): Number of folds for k-folding.
        n_trials (int): Number of trials for hyperparameter optimization.
    """
    def objective(trial):
        params = {
            "n_estimators": trial.suggest_int("n_estimators", 50, 100, step=10),
            "learning_rate": trial.suggest_float("learning_rate", 0.05, 0.2, step=0.05),
            "max_depth": trial.suggest_int("max_depth", 2, 4, step=1),
            "min_samples_leaf": trial.suggest_int("min_samples_leaf", 200, 1200, step=200),
            "subsample": trial.suggest_float("subsample", 0.3, 0.6, step=0.1),
        }

        try:
            gb = reweight.GBReweighter(
                n_estimators=params["n_estimators"],
                learning_rate=params["learning_rate"],
                max_depth=params["max_depth"],
                min_samples_leaf=params["min_samples_leaf"],
                gb_args={"subsample": params["subsample"], "random_state": 42},
            )

            folding = reweight.FoldingReweighter(
                gb,
                n_folds=n_folds,
                random_state=42,
            )

            folding.fit(mc[columns], data[columns],
                   original_weight=mcweights,
                   target_weight=sweights)

            weights_pred = folding.predict_weights(mc[columns])
            
            ax = None

            score = evaluate_reweighting(
                mc=mc[columns].values,
                data=data[columns].values,
                weights_mc=weights_pred,
                weights_data=sweights,
                label="Trial",
                ax=ax,
                score_dict=None  # or a dict if you want scores
            )

            # skip the trial if the score is not valid
            if score < 0.5 or np.isnan(score) or np.isinf(score):
                raise ValueError("Invalid score: {}".format(score))
            return score
        
        except Exception as e:
            print(f"Trial failed with error: {e}")
            return float('inf')

    initial_params = {
        "n_estimators": 50,
        "learning_rate": 0.1,
        "max_depth": 3,
        "min_samples_leaf": 1000,
        "subsample": 0.4
    }

    sampler = optuna.samplers.TPESampler(seed=42)
    study = optuna.create_study(direction="minimize", sampler=sampler)
    study.enqueue_trial(initial_params)
    study.optimize(objective, n_trials=n_trials, n_jobs=-1)

    return study 