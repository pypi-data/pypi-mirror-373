import pandas as pd

def sma(df: pd.DataFrame, parameters: dict = None, columns: dict = None) -> tuple:
    """
    Calculates the Simple Moving Average (SMA) of a series.

    The SMA is a moving average that is calculated by taking the arithmetic
    mean of a given set of values over a specified period.

    Args:
        df (pd.DataFrame): The dataframe containing price data. Must have close column.
        parameters (dict): The parameter dictionary that includes window size for the SMA calculation.
        columns (dict): The column dictionary that includes close column name.

    Returns:
        tuple: A tuple containing the SMA series and its column names list.

    The Simple Moving Average (SMA) is a type of moving average that is calculated
    by taking the arithmetic mean of a given set of values over a specified
    period. It is the simplest form of moving average and is often used to
    smooth out price data or other time series data.

    The formula for calculating the SMA is as follows:

    SMA = (Sum of values in the period) / (Number of values in the period)

    Use Cases:

    - Identifying trends: The SMA can be used to identify the direction of a
      price trend.
    - Smoothing price data: The SMA can smooth out short-term price fluctuations
      to provide a clearer view of the underlying trend.
    - Generating buy and sell signals: The SMA can be used in crossover systems
      to generate buy and sell signals.
    """
    # Set default values
    if parameters is None:
        parameters = {}
    if columns is None:
        columns = {}
        
    # Extract parameters with defaults
    close_col = columns.get('close_col', 'Close')
    window = int(parameters.get('window', 20))

    series = df[close_col]
    series =series.rolling(window=window).mean()
    series.name = f'SMA_{window}'

    columns_list = [series.name]

    return series, columns_list