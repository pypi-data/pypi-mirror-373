import pandas as pd
from scipy import stats

def impute_missing(series: pd.Series, strategy: str = 'median') -> pd.Series:
    """
    Impute missing values in a pandas Series using specified strategy.
    
    Parameters:
        series (pd.Series): The data column with missing values.
        strategy (str): One of 'median', 'mean', or 'mode' (default 'median').
        
    Returns:
        pd.Series: Series with missing values imputed.
    """
    if strategy == 'median':
        value = series.median()
    elif strategy == 'mean':
        value = series.mean()
    elif strategy == 'mode':
        # mode() returns a Series, take the first mode if multiple
        mode_vals = series.mode()
        if not mode_vals.empty:
            value = mode_vals.iloc[0]
        else:
            value = None
    else:
        raise ValueError("strategy must be one of 'median', 'mean', or 'mode'")
    
    return series.fillna(value)
