from pathlib import Path
import uproot
import numpy as np
import pandas as pd
import numexpr as ne
import re


def extract_variables_from_expression(expr):
    """
    Extract variable names from a mathematical expression string.
    Assumes variable names contain letters, numbers, or underscores.
    Ignores function names like 'log'.
    """
    # Remove function calls like log(...), sin(...), etc.
    expr_no_funcs = re.sub(r'\b[a-zA-Z_][a-zA-Z0-9_]*\s*\(', '', expr)
    # Extract variable-like tokens
    tokens = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', expr_no_funcs)
    # Filter out math functions
    known_funcs = {"log", "exp", "sqrt", "sin", "cos", "tan", "abs"}
    return {tok for tok in tokens if tok not in known_funcs}

def load_data(path, tree, columns, weights_col=None):
    """
    Load data from a ROOT file and return a DataFrame with computed expressions and optional weights.

    Args:
        path (str): Path to the ROOT file.
        tree (str): Name of the tree to read from.
        columns (list): List of column names or expressions (e.g. ["pt", "log(pt)", "pt/eta"]).
        weights_col (str, optional): Name of the column containing weights.

    Returns:
        df (pd.DataFrame): DataFrame with evaluated columns.
        weights (np.ndarray): Array of weights.
    """
    columns = list(columns)  # in case it's a tuple or other iterable
    expr_map = {}  # final_name -> expression
    needed_vars = set()

    for col in columns:
        if any(op in col for op in "+-*/()") or "log" in col or "exp" in col:
            expr_map[col] = col  # column is an expression
            needed_vars.update(extract_variables_from_expression(col))
        else:
            expr_map[col] = col
            needed_vars.add(col)

    if weights_col:
        needed_vars.add(weights_col)

    with uproot.open(path) as f:
        df = f[tree].arrays(list(needed_vars), library="pd")

    out_df = pd.DataFrame()
    for name, expr in expr_map.items():
        try:
            out_df[name] = ne.evaluate(expr, local_dict=df)
        except Exception as e:
            raise ValueError(f"Failed to evaluate expression '{expr}' for column '{name}': {e}")

    weights = df[weights_col].values if weights_col else np.ones(len(df))
    return out_df, weights

def save_data(input_path, tree, output_path, output_tree, branch, weights):
    """
    Save weights to a ROOT file.
    
    Args:
        input_path (str): Path to the input ROOT file.
        tree (str): Name of the tree to read from.
        output_path (str): Path to the output ROOT file.
        output_tree (str): Name of the tree to write to.
        branch (str): Name of the branch to save weights under.
        weights (np.ndarray): Weights to save.
    """
    with uproot.open(input_path) as f:
        data = f[tree].arrays(library="pd")
    data[branch] = weights
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    with uproot.recreate(output_path) as f:
        f[output_tree] = data

def def_aliases(df, aliases):
    """
    Apply aliases to the DataFrame.
    
    Args:
        df (pd.DataFrame): DataFrame to apply aliases to.
        aliases (dict): Dictionary of aliases where keys are new names and values are expressions.
    
    Returns:
        pd.DataFrame: DataFrame with applied aliases.
    """
    for new_name, expr in aliases.items():
        try:
            if expr in df.columns:
                df[new_name] = df[expr]
            else:
                df[new_name] = df.eval(expr)
        except Exception as e:
            print(f"Error applying alias '{new_name}': {e}")    
    return df

def flatten_vars(lst):
    """
    Flatten a names list 

    Args:
        lst (list): List of lists or a single list.
    """
    def transform(x):
        # Replace operators
        x = x.replace('/', 'over')
        x = x.replace('+', 'plus')
        x = x.replace('*', 'times')
        x = x.replace('-', 'minus')
        # Replace function calls like func(X) → funcX
        x = re.sub(r'(\w+)\((\w+)\)', r'\1\2', x)
        return x

    return [transform(x) for x in lst if isinstance(x, str) and x.strip() != ''] + \
           [x for x in lst if not isinstance(x, str) or x.strip() == '']