import pandas as pd

def macd(df: pd.DataFrame, parameters: dict = None, columns: dict = None) -> tuple:
    """
    Calculates the Moving Average Convergence Divergence (MACD), Signal Line, and Histogram.

    The MACD is a popular momentum indicator used in technical analysis that shows the relationship between two exponential moving averages (EMAs) of a security's price.

    Args:
        df (pd.DataFrame): The input DataFrame.
        parameters (dict, optional): Dictionary containing calculation parameters:
            - window_slow (int): The window size for the slower EMA. Default is 26.
            - window_fast (int): The window size for the faster EMA. Default is 12.
            - window_signal (int): The window size for the signal line EMA. Default is 9.
        columns (dict, optional): Dictionary containing column name mappings:
            - close_col (str): The column name for closing prices. Default is 'Close'.

    Returns:
        tuple: A tuple containing the MACD DataFrame and a list of column names.

    The MACD is calculated as follows:

    1. Calculate the fast EMA (typically 12 periods).
    2. Calculate the slow EMA (typically 26 periods).
    3. Calculate the MACD line by subtracting the slow EMA from the fast EMA.
    4. Calculate the signal line by taking an EMA of the MACD line (typically 9 periods).
    5. Calculate the MACD histogram by subtracting the signal line from the MACD line.

    Use Cases:

    - Identifying trend direction: The MACD can be used to identify the direction of a price trend.
    - Identifying potential buy and sell signals: Crossovers of the MACD line and signal line can be used to generate buy and sell signals.
    - Identifying overbought and oversold conditions: The MACD histogram can be used to identify overbought and oversold conditions.
    """
    # Set default values
    if parameters is None:
        parameters = {}
    if columns is None:
        columns = {}
        
    # Extract parameters with defaults
    window_slow = int(parameters.get('window_slow', 26))
    window_fast = int(parameters.get('window_fast', 12))
    window_signal = int(parameters.get('window_signal', 9))
    close_col = columns.get('close_col', 'Close')
    
    series = df[close_col]
    ema_fast = series.ewm(span=window_fast, adjust=False).mean()
    ema_slow = series.ewm(span=window_slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=window_signal, adjust=False).mean()
    histogram = macd_line - signal_line
    # Return DataFrame for multi-output indicators
    df_macd = pd.DataFrame({
        f'MACD_{window_fast}_{window_slow}': macd_line,
        f'Signal_{window_signal}': signal_line,
        f'Hist_{window_fast}_{window_slow}_{window_signal}': histogram
    })
    # Ensure index is passed explicitly, just in case
    df_macd.index = series.index
    columns_list = list(df_macd.columns)
    return df_macd, columns_list