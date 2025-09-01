import pandas as pd

charles_theme = {
    'candlestick': {
        'increasing': 'rgb(107,174,214)',
        'decreasing': 'rgb(198,113,113)'
    },
    'grid': 'rgb(255,255,255)',
    'background': 'rgb(207,216,209)',
    'text': 'rgb(68,68,68)'
}

theme_map = {
    'charles': charles_theme
}


def plot_simple_ohlcv(df: pd.DataFrame, with_rangeslider: bool = True,
                      title: str = None, theme: str = 'charles', show_legend: bool = False):
    pass


def plot_ohlcv(df: pd.DataFrame, with_volume: bool = True, with_rangeslider: bool = True,
               title: str = None, theme: str = 'charles', show_legend: bool = False):
    pass
