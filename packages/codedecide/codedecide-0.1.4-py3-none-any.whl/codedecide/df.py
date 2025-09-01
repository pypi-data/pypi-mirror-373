import pandas as pd
import os

def read_feather_file(file_path, top_n: int = -1, date_col: str = 'date'):
    """
    read ohlcv feather file
    """
    df = pd.read_feather(file_path)
    df[date_col] = pd.to_datetime(df[date_col])
    if top_n > 0:
        df = df.head(top_n)
    return df


def convert_symbol(symbol: str = ''):
    return symbol.replace('/', '_').replace(':', '_')


def read_data(exchange: str = 'binance', trading_mode: str = 'futures', symbol: str = 'BTC/USDT:USDT', timeframe: str = '1d', format: str = 'feather'):
    home_path = os.environ['CRYPTO_DATA_HOME']
    assert home_path is not None
    data_dir = os.path.join(home_path, exchange, trading_mode)
    file_name = convert_symbol(symbol) + '-' + \
        timeframe + '-' + trading_mode + '.' + format
    file_path = os.path.join(data_dir, file_name)
    if format == 'feather':
        return read_feather_file(file_path)
    else:
        return None


def merge_bars(df: pd.DataFrame, timeframe: str):
    """
    example: merge_bars(df, '5min')
    :param df: origin data frame, DateTimeIndex and open,high,low,close,volume columns are requires
    :param timeframe: time frame，such as 5T,3D,10H,5min,30s, etc.，refer to pandas.date_range
    :return:
    """
    ohlc_dict = {
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum'
    }
    return df.resample(timeframe).agg(ohlc_dict)
