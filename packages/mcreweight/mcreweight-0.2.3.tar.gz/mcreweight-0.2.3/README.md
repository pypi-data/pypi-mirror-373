# mcreweight

`mcreweight` is a python library to perform Monte Carlo event reweighting based on multiplicity and kinematic variables. The tool is using GBReweighter, a classifier-based method implemented in `hep_ml` package, and it supports automated hyperparameter tuning with Optuna. A folding approach over the reweighter is also applied, and performances are compared with the ones from the bins reweighting. 

> [!WARNING]
Bins reweighting works fine for one or two dimensional histograms, but it is unstable and inaccurate for higher dimenstions 

## Requirements

- Python 3.8+
- Required packages listed in `requirements.txt`

## Setup

If you run in a lb-conda environment, as
```bash
lb-conda default
```
consider exporting the PATH to run `scripts/run_reweighting.py` and `scripts/apply_weights.py` with commands `run-reweight` and `apply-weights`. In this case, use
```bash
export PATH=$PATH:/path/to/.local/bin
```	

## Installation

### From PyPl

```bash
pip install mcreweight
```

### From Gitlab

```bash
git clone https://github.com/tfulghes/mcreweight.git
cd mcreweight
pip install -e .
```

## Usage

To run the reweighting:

```bash
run-reweight --path_data <path_to_data.root> \
    	     --path_mc <path_to_mc.root> \
    	     --vars <variable_list> \
    	     --monitoring_vars <monitoring_variable_list> \
    	     --sample <sample> \
    	     --trials <optuna_tests> \
    	     --test_size <test_sample_size>
```

To apply the weights to the signal MC:

```bash
apply-weights --path_mc <path_to_mc.root> \
    	      --vars <variable_list> \
    	      --training_sample <training_sample> \
    	      --application_sample <application_sample> \
    	      --method <method_for_reweighter> \
    	      --monitoring_vars <monitoring_variable_list> \
    	      --output_path <output_file.root>
```

### Options

#### For the reweighting (`run-reweight`):

**Input files:**
- `--path_data`: Path to the data control sample (required)
- `--tree_data`: Name of the tree in the data control sample (default: "DecayTree")
- `--path_mc`: Path to the MC control sample (required)
- `--tree_mc`: Name of the tree in the MC control sample (default: "DecayTree")
- `--mcweights_name`: Name of the branch for weights in the MC sample (default: None)
- `--sweights_name`: Name of the sweights column in the data (default: "sweight_sig")
- `--mc_label`: Label for the MC sample (default: "MC")
- `--data_label`: Label for the data sample (default: "Data")

**Variables:**
- `--vars`: List of variables to use for reweighting (default: ["B_DTF_Jpsi_P", "B_DTF_Jpsi_PT", "nLongTracks", "nPVs"])
- `--monitoring_vars`: List of variables to plot (default: None)

**Reweighter configuration:**
- `--sample`: Sample name for the dataset (default: "bd_jpsikst_ee")
- `--trials`: Number of trials for the gradient boosting reweighting (default: 10)
- `--test_size`: Proportion of the dataset to include in the test split (default: 0.3)
- `--n_folds`: Number of folds for k-folding reweighting (default: 4)
- `--n_bins`: Number of bins for binning reweighting (default: 20)
- `--n_neighs`: Number of nearest neighbors for binning reweighting (default: 3)

**Output:**
- `--weightsdir`: Directory to save weights (default: "weights")
- `--plotdir`: Directory to save plots (default: "plots")

Additional options can be found by running:
```bash
run-reweight --help
```

#### For the application of the weights (`apply-weights`):

**Input files:**
- `--path_mc`: Path to the MC signal sample (required)
- `--tree_mc`: Name of the tree in the MC signal sample (default: "DecayTree")
- `--mcweights_name`: Name of the branch for weights in the output ROOT file (default: None)
- `--path_data`: Path to the data sample for comparison (default: None)
- `--tree_data`: Name of the tree in the data sample (default: "DecayTree")
- `--sweights_name`: Name of the sweights column in the data (default: "sweight_sig")

**Variables:**
- `--vars`: List of variables to use for reweighting (default: ["B_DTF_Jpsi_P", "B_DTF_Jpsi_PT", "nLongTracks", "nPVs"])
- `--training_vars`: List of variables used for training (default: ["B_DTF_Jpsi_P", "B_DTF_Jpsi_PT", "nLongTracks", "nPVs"])
- `--monitoring_vars`: List of variables to plot (default: None)

**Configuration:**
- `--training_sample`: Sample name for the dataset (default: "bd_jpsikst_ee")
- `--application_sample`: Sample name for the application of weights (default: "bd_jpsikst_ee")
- `--method`: Method to apply weights (choices: "gbreweighter", "kfolding", "binning", default: "gbreweighter")
- `--weightsdir`: Directory to save weights (default: "weights")
- `--plotdir`: Directory to save plots (default: "plots")

**Output:**
- `--output_path`: Path to save the output ROOT file (required)
- `--output_tree`: Name of the tree in the output ROOT file (default: "DecayTree")

Additional options can be found by running:
```bash
apply-weights --help
```

## Example

Reweighting:
```bash
run-reweight --path_data data/control_sample_tuple.root \
    	     --path_mc mc/control_sample_tuple.root \
    	     --vars B_DTF_Jpsi_P B_DTF_Jpsi_PT nLongTracks nPVs \
    	     --monitoring_vars B_ETA nFTClusters nVPClusters nEcalClusters \
    	     --sample bd_jpsikst_ee \
    	     --n_trials 5 \
    	     --test_size 0.3 
```

Application of the weights:
```bash
apply-weights --path_mc mc/signal_tuple.root \
    	      --vars B_P B_PT nLongTracks nPVs  \
    	      --training_vars B_DTF_Jpsi_P B_DTF_Jpsi_PT nLongTracks nPVs  \
    	      --training_sample bd_jpsikst_ee \
    	      --application_sample bd_jpsikst_ee \
    	      --method gbreweighter \
    	      --monitoring_vars B_ETA nFTClusters nVPClusters nEcalClusters \
    	      --output_path mc/signal_tuple_reweighted.root
```

## Contact

For questions, please contact the repository maintainer.