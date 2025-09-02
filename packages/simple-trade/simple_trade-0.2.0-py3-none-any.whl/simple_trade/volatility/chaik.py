import pandas as pd
import numpy as np
from ..trend.ema import ema


def chaikin_volatility(df: pd.DataFrame, parameters: dict = None, columns: dict = None) -> tuple:
    """
    Calculates the Chaikin Volatility (CV) indicator, which measures volatility by 
    calculating the rate of change of the high-low price range.
    
    Args:
        df (pd.DataFrame): The input DataFrame.
        parameters (dict, optional): Dictionary containing calculation parameters:
            - ema_window (int): The window for calculating the EMA of the high-low range. Default is 10.
            - roc_window (int): The window for calculating the rate of change. Default is 10.
        columns (dict, optional): Dictionary containing column name mappings:
            - high_col (str): The column name for high prices. Default is 'High'.
            - low_col (str): The column name for low prices. Default is 'Low'.
    
    Returns:
        tuple: A tuple containing the Chaikin Volatility series and a list of column names.
    
    The Chaikin Volatility is calculated in three steps:
    
    1. Calculate the daily high-low range: high - low
    2. Calculate an exponential moving average (EMA) of the high-low range
    3. Calculate the rate of change of this EMA over the specified period
    
    A higher CV value indicates higher volatility, while a lower value indicates lower volatility.
    
    Use Cases:
    
    - Volatility measurement: Identifies periods of increasing or decreasing volatility.
    - Market turning points: Rising volatility may precede market tops, while falling volatility
      may precede market bottoms.
    - Range expansion/contraction: Helps identify when markets are transitioning from quiet to 
      active periods.
    - Breakout confirmation: Sharp increases in volatility can confirm breakout movements.
    - Risk management: Adjust position sizing based on current volatility conditions.
    """
    # Set default values
    if parameters is None:
        parameters = {}
    if columns is None:
        columns = {}
        
    # Extract parameters with defaults
    ema_window = int(parameters.get('ema_window', 10))
    roc_window = int(parameters.get('roc_window', 10))
    high_col = columns.get('high_col', 'High')
    low_col = columns.get('low_col', 'Low')
    
    high = df[high_col]
    low = df[low_col]
    
    # Calculate the daily high-low range
    hl_range = high - low
    df = pd.DataFrame(hl_range, columns=['Close'])

    # Calculate the EMA of the high-low range
    # Create parameters for ema function
    ema_parameters = {'window': ema_window}
    ema_columns = {'close_col': 'Close'}
    range_ema_series, _ = ema(df, parameters=ema_parameters, columns=ema_columns)
    
    # Calculate the percentage rate of change over roc_window days
    # (Current EMA - EMA roc_window days ago) / (EMA roc_window days ago) * 100
    roc = ((range_ema_series - range_ema_series.shift(roc_window)) / range_ema_series.shift(roc_window)) * 100
    roc.name = f'CHAIK_{ema_window}_{roc_window}'
    columns_list = [roc.name]
    return roc, columns_list
