import pandas as pd
import numpy as np


def obv(df: pd.DataFrame, parameters: dict = None, columns: dict = None) -> tuple:
    """
    Calculates the On-Balance Volume (OBV), a volume-based momentum indicator that 
    relates volume flow to price changes.
    
    Args:
        df (pd.DataFrame): The DataFrame containing the data.
        parameters (dict, optional): Dictionary containing calculation parameters. This indicator does not use any calculation parameters.
        columns (dict, optional): Dictionary containing column name mappings:
            - close_col (str): The column name for closing prices. Default is 'Close'.
            - volume_col (str): The column name for volume. Default is 'Volume'.
    
    Returns:
        tuple: A tuple containing the OBV series and a list of column names.
    
    On-Balance Volume is calculated by adding volume on up days and subtracting 
    volume on down days:
    
    1. If today's close is higher than yesterday's close:
       OBV = Previous OBV + Today's Volume
    
    2. If today's close is lower than yesterday's close:
       OBV = Previous OBV - Today's Volume
    
    3. If today's close is equal to yesterday's close:
       OBV = Previous OBV
    
    The absolute OBV value is not important; rather, the trend and slope of the 
    OBV line should be considered.
    
    Use Cases:
    
    - Trend confirmation: Rising OBV confirms an uptrend; falling OBV confirms a downtrend.
    - Divergence detection: If price makes a new high but OBV doesn't, it may indicate weakness.
    - Potential breakouts: A sharp rise in OBV might precede a price breakout.
    - Support/resistance validation: Volume should increase when price breaks through 
      significant levels.
    - Accumulation/distribution identification: Increasing OBV during sideways price 
      movement may indicate accumulation.
    """
    # Set default values
    if parameters is None:
        parameters = {}
    if columns is None:
        columns = {}
        
    # Extract parameters with defaults
    close_col = columns.get('close_col', 'Close')
    volume_col = columns.get('volume_col', 'Volume')
    
    close = df[close_col]
    volume = df[volume_col]

    # Calculate the daily price change direction
    # 1 for price up, -1 for price down, 0 for unchanged
    price_direction = close.diff().apply(lambda x: 1 if x > 0 else (-1 if x < 0 else 0))
    
    # First OBV value is equal to the first period's volume
    obv_values = pd.Series(index=close.index, dtype=float)
    obv_values.iloc[0] = volume.iloc[0]
    
    # Cumulative sum of volume multiplied by price direction
    for i in range(1, len(close)):
        obv_values.iloc[i] = obv_values.iloc[i-1] + (volume.iloc[i] * price_direction.iloc[i])
    
    obv_values.name = 'OBV'
    columns_list = [obv_values.name]
    return obv_values, columns_list
