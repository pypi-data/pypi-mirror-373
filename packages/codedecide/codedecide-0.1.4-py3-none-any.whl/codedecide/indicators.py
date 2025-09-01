import numpy as np
import pandas as pd
import talib

def ACCER(df: pd.DataFrame, timeperiod=10):
    # pre-allocate np-array
    accer = np.full(len(df), fill_value=np.nan)

    # calc slop
    for i in range(timeperiod - 1, len(df)):
        y = df.iloc[i - timeperiod + 1:i+1]
        x = np.array(range(timeperiod))
        coefficients = np.polyfit(x, y, 1)
        accer[i] = coefficients[0]

    return accer

def weighted_moving_average(data, period, times):
    """
    计算加权移动平均线
    """
    d = np.arange(period, 0, -1)
    w = times * (np.power(d,2))
    return np.sum(w * data[-period:] / np.sum(w))

def HULLMA(df: pd.DataFrame, period):
    """
    计算Hull Moving Average
    """
    sqrt_period = int(np.sqrt(period))
    wma_half_period = talib.WMA(df, timeperiod=int(period / 2))
    wma_full_period = talib.WMA(df, timeperiod=period)
    diff = 2 * wma_half_period - wma_full_period
    diff_wma = talib.WMA(diff, timeperiod=sqrt_period)
    return talib.WMA((2*wma_half_period)[-sqrt_period:] - wma_full_period[-sqrt_period:], timeperiod=sqrt_period)


# data = pd.Series(np.random.random(100))  # 生成一个包含100个随机数值的pandas Series

# hma = hull_moving_average(data, 10)
# print(hma)


def HEIKIN_ASHI(df: pd.DataFrame, inplace: bool =True):
    """Heikin ashi indicators, generate columns: ha_open, ha_close, ha_high, ha_low

    Args:
        df (pd.DataFrame): OHLCV data
        inplace (bool): add new columns in origin data frame, if false return a new data frame with 4 cols
    """
    if inplace:
        df['ha_close'] = (df['open'] + df['high'] + df['low'] + df['close']) / 4
        df['ha_open'] = 0
        for i in range(len(df)):
            if i == 0:
                df['ha_open'].iat[i] = df['open'].iat[i]
            else:
                df['ha_open'].iat[i] = (df['ha_open'].iat[i-1] + df['ha_close'].iat[i-1]) / 2
        df['ha_high'] = df[['ha_open', 'ha_close', 'high']].max(axis=1)
        df['ha_low'] = df[['ha_open', 'ha_close', 'low']].min(axis=1)
        return df
    else:
        heikin_ashi_df = pd.DataFrame(index=df.index.values)
        heikin_ashi_df['ha_close'] = (df['open'] + df['high'] + df['low'] + df['close']) / 4

        for i in range(len(df)):
            if i == 0:
                heikin_ashi_df.iat[0, heikin_ashi_df.columns.get_loc('ha_open')] = df['open'].iloc[i]
            else:
                heikin_ashi_df.iat[i, heikin_ashi_df.columns.get_loc('ha_open')] = (heikin_ashi_df.iat[i-1, heikin_ashi_df.columns.get_loc('ha_open')] + heikin_ashi_df.iat[i-1, heikin_ashi_df.columns.get_loc('ha_close')]) / 2
    
        heikin_ashi_df['ha_high'] = heikin_ashi_df.join(df['high']).max(axis=1)
        heikin_ashi_df['ha_low'] = heikin_ashi_df.join(df['low']).min(axis=1)
        return heikin_ashi_df
