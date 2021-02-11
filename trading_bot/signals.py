import os
from datetime import datetime
# import matplotlib
# matplotlib.use('Agg')
from matplotlib import pyplot as plt

import mplfinance as mpf
import pandas as pd
import pandas_ta as ta
import numpy as np
import scipy.signal
from binance.client import Client

plt.style.use('dark_background')

client = Client(os.getenv('bbot_pub'), os.getenv('bbot_sec'))


class Signals:

    def __init__(self, symbol='BTCUSDT', tf='1h'):
        self.df = self.get_df(symbol, tf)
        self.symbol = symbol.upper()
        self.tf = tf
        self.rsi_div_chart = None
        self.vol_signal = self.vol_rise_fall()
        self.vol_candle = self.large_vol_candle()
        self.rsi_ob_os_dict = {
            'overbought': False,
            'oversold': False,
        }
        self.rsi_overbought_oversold()
        self.rsi_div_dict = {
            'possible bearish divergence': False,
            'possible bullish divergence': False,
            'confirmed bearish divergence': False,
            'confirmed bullish divergence': False,
        }
        self.rsi_divergence()
        self.macd_dict = {
            'MACD cross': None,
            'MACD 0 cross': None,
        }
        self.macd_signals()
        self.ema_signals_dict = {
            'Price crossing EMA200': None,
            'EMA20 crossing EMA50': None,
            'EMA50 crossing EMA200': None,
        }
        self.ema_signals()

    def full_check(self):
        self.rsi_divergence()
        self.ema_signals()
        self.macd_signals()
        self.rsi_overbought_oversold()
        self.vol_rise_fall()
        self.large_vol_candle()

    @staticmethod
    def get_df(symbol='BTCUSDT', tf='1h') -> pd.DataFrame:
        interval_dict = {
            '1m': Client.KLINE_INTERVAL_1MINUTE,
            '5m': Client.KLINE_INTERVAL_5MINUTE,
            '15m': Client.KLINE_INTERVAL_15MINUTE,
            '1h': Client.KLINE_INTERVAL_1HOUR,
            '4h': Client.KLINE_INTERVAL_4HOUR,
            '1d': Client.KLINE_INTERVAL_1DAY,
            '1w': Client.KLINE_INTERVAL_1WEEK,
            '1M': Client.KLINE_INTERVAL_1MONTH,
        }
        klines = client.futures_klines(symbol=symbol, interval=interval_dict[tf])
        rows_list = []
        for kline in klines:
            row_dict = {
                'date': datetime.fromtimestamp(int(str(kline[0])[0:10])),
                'open': float(kline[1]),
                'high': float(kline[2]),
                'low': float(kline[3]),
                'close': float(kline[4]),
                'volume': float(kline[5]),
            }
            rows_list.append(row_dict)
        df = pd.DataFrame(rows_list)
        df['rsi'] = ta.rsi(df.close, 14)
        df = pd.concat((df, ta.macd(df.close, 12, 26, 9)), axis=1)
        df['ema_20'], df['ema_50'] = ta.ema(df.close, 20), ta.ema(df.close, 50)
        if len(df) >= 288:
            df['ema_200'] = ta.ema(df.close, 200)
        else:
            df['ema_200'] = ta.ema(df.close, len(df.close)-3)
        df.set_index('date', inplace=True)
        df.rename_axis('date', inplace=True)
        df = df.tail(88)
        return df

    def main_chart(self):
        plt.style.use('dark_background')
        fig, axes = plt.subplots(nrows=3, ncols=1, gridspec_kw={'height_ratios': [3, 1, 1]})
        fig.suptitle(f"{self.symbol} {self.tf}", fontsize=16)
        ax_r = axes[0].twinx()
        mc = mpf.make_marketcolors(up='#00e600', down='#ff0066',
                                   edge={'up': '#00e600', 'down': '#ff0066'},
                                   wick={'up': '#00e600', 'down': '#ff0066'},
                                   volume={'up': '#808080', 'down': '#4d4d4d'},
                                   ohlc='black')
        s = mpf.make_mpf_style(marketcolors=mc)
        ax_r.set_alpha(0.01)
        axes[0].set_zorder(2)
        for ax in axes:
            ax.set_facecolor((0, 0, 0, 0))
        ax_r.set_zorder(1)

        axes[1].set_ylabel('RSI')
        axes[1].margins(x=0, y=0.1)
        axes[0].margins(x=0, y=0.05)
        axes[2].set_ylabel('MACD')
        ax_r.set_ylabel('')
        ax_r.yaxis.set_visible(False)
        axes[2].margins(0, 0.05)
        axes[0].xaxis.set_visible(False)
        axes[1].xaxis.set_visible(False)

        axes[0].yaxis.tick_left()
        axes[0].yaxis.set_label_position('left')
        fig.autofmt_xdate()
        plt.tight_layout()
        self.df.volume = self.df.volume.div(2)
        mpf.plot(self.df, ax=axes[0], type="candle", style=s, volume=ax_r)
        max_vol = max({y for index, y in self.df.volume.items()})
        ax_r.axis(ymin=0, ymax=max_vol * 3)
        self.df['rsi'].plot(ax=axes[1], legend=False, sharex=axes[0], color='#00e600')
        self.df['MACD_12_26_9'].plot(ax=axes[2], legend=False, sharex=axes[0], color='#00e600')
        self.df['MACDs_12_26_9'].plot(ax=axes[2], legend=False, sharex=axes[0], color='#ff0066')
        axes[2].axhline(0, color='gray', ls='--')
        axes[1].axhline(70, color='gray', ls='--')
        axes[1].axhline(30, color='gray', ls='--')
        axes[2].set_xlabel('')
        plt.savefig('main.png')
        plt.close()

    def plot_emas(self):
        plt.style.use('dark_background')
        fig = plt.figure()
        fig.suptitle(f"{self.symbol.upper()} 25EMA/99EMA ({self.tf})", fontsize=16)
        self.df.close.plot(color='gray')
        self.df.ema_20.plot(color='#00e600')
        self.df.ema_50.plot(color='#ff0066')
        self.df.ema_200.plot(color=(0,0,1,1))
        fig.autofmt_xdate()
        plt.legend()
        plt.xlabel('')
        plt.ylabel('')
        plt.tight_layout()
        plt.savefig('emas.png')
        plt.close()

    def plot_rsi_div(self):
        rsi_array = np.array(self.df['rsi'].tail(20).array)
        close_array = np.array(self.df['close'].tail(20).array)
        rsi_peaks, _ = scipy.signal.find_peaks(rsi_array)
        rsi_troughs, _ = scipy.signal.find_peaks(-rsi_array)
        fig, (ax1, ax2) = plt.subplots(2, sharex=True)
        fig.suptitle(f'{self.symbol} RSI Divergence {self.tf}')
        ax1.set_ylabel('Close')
        ax2.set_ylabel('RSI')
        ax2.axhline(70, color='gray', ls='--')
        ax2.axhline(30, color='gray', ls='--')
        ax1.xaxis.set_visible(False)
        ax2.xaxis.set_visible(False)
        ax1.plot(close_array)
        ax2.plot(rsi_array, color='green')
        ax1.plot(rsi_peaks, close_array[rsi_peaks], '.', color="#ff0066")
        ax2.plot(rsi_peaks, rsi_array[rsi_peaks], '.', color="#ff0066")
        ax1.plot(rsi_troughs, close_array[rsi_troughs], '.', color="#00e600")
        ax2.plot(rsi_troughs, rsi_array[rsi_troughs], '.', color="#00e600")
        _, new_close_array, new_rsi_array, indices = self.rsi_divergence()
        if len(close_array) != len(new_close_array):
            ax1.plot(indices, new_close_array, color="#ff0066")
            ax2.plot(indices, new_rsi_array, color="#ff0066")
        fig.savefig('rsi_div.png')
        plt.close()
        # plt.show()

    def rsi_divergence(self):
        rsi_array = np.array(self.df['rsi'].tail(20).array)
        close_array = np.array(self.df['close'].tail(20).array)
        rsi_peaks, _ = scipy.signal.find_peaks(rsi_array)
        rsi_troughs, _ = scipy.signal.find_peaks(-rsi_array)
        original_index = len(close_array)
        indices = np.array([])

        # bearish divergence confirmed: rsi formed lower peak while price formed higher peak
        if rsi_array[rsi_peaks[-2]] >= rsi_array[rsi_peaks[-1]] >= rsi_array[-1]:
            if close_array[rsi_peaks[-2]] <= close_array[rsi_peaks[-1]]:
                close_array = np.array([close_array[rsi_peaks[-2]], close_array[rsi_peaks[-1]]])
                rsi_array = np.array([rsi_array[rsi_peaks[-2]], rsi_array[rsi_peaks[-1]]])
                indices = np.array([rsi_peaks[-2], rsi_peaks[-1]])
                self.rsi_div_dict['confirmed bearish divergence'] = True

        # possible bearish divergence: rsi forming lower peak while price forming higher peak
        elif rsi_array[rsi_peaks[-1]] >= rsi_array[-1]:
            if close_array[rsi_peaks[-1]] <= close_array[-1]:
                close_array = np.array([close_array[rsi_peaks[-1]], close_array[-1]])
                rsi_array = np.array([rsi_array[rsi_peaks[-1]], rsi_array[-1]])
                indices = np.array([rsi_peaks[-1], original_index])
                self.rsi_div_dict['possible bearish divergence'] = True

        # bullish divergence confirmed: rsi formed higher trough while price formed lower trough
        elif rsi_array[rsi_troughs[-2]] <= rsi_array[rsi_troughs[-1]] <= rsi_array[-1]:
            if close_array[rsi_troughs[-2]] >= close_array[rsi_troughs[-1]]:
                close_array = np.array([close_array[rsi_troughs[-2]], close_array[rsi_troughs[-1]]])
                rsi_array = np.array([rsi_array[rsi_troughs[-2]], rsi_array[rsi_troughs[-1]]])
                indices = np.array([rsi_troughs[-2], rsi_troughs[-1]])
                self.rsi_div_dict['confirmed bullish divergence'] = True

        # possible bullish divergence: rsi forming higher trough while price forming lower trough
        elif rsi_array[rsi_troughs[-1]] <= rsi_array[-1]:
            if close_array[rsi_troughs[-1]] >= close_array[-1]:
                close_array = np.array([close_array[rsi_troughs[-1]], close_array[-1]])
                rsi_array = np.array([rsi_array[rsi_troughs[-1]], rsi_array[-1]])
                indices = np.array([rsi_troughs[-1], original_index])
                self.rsi_div_dict['possible bullish divergence'] = True

        return self.rsi_div_dict, close_array, rsi_array, indices

    def rsi_overbought_oversold(self, os=30, ob=70):
        rsi_array = self.df['rsi'].array
        if rsi_array[-1] > os > rsi_array[-2]:
            self.rsi_ob_os_dict['oversold'] = True
        elif rsi_array[-1] < ob < rsi_array[-2]:
            self.rsi_ob_os_dict['overbought'] = True
        return self.rsi_ob_os_dict

    def macd_signals(self, long=26, short=12, smoothing=9):
        if self.df['MACD_12_26_9'].array[-1] > self.df['MACDs_12_26_9'].array[-1]:
            if self.df['MACD_12_26_9'].array[-2] < self.df['MACDs_12_26_9'].array[-2]:
                self.macd_dict['MACD cross'] = True
        elif self.df['MACD_12_26_9'].array[-1] < self.df['MACDs_12_26_9'].array[-1]:
            if self.df['MACD_12_26_9'].array[-2] > self.df['MACDs_12_26_9'].array[-2]:
                self.macd_dict['MACD cross'] = False
        if (self.df['MACD_12_26_9'].array[-1], self.df['MACDs_12_26_9'].array[-1]) > (0, 0):
            if (self.df['MACD_12_26_9'].array[-2], self.df['MACDs_12_26_9'].array[-2]) <= (0, 0):
                self.macd_dict['MACD 0 cross'] = True
        elif (self.df['MACD_12_26_9'].array[-1], self.df['MACDs_12_26_9'].array[-1]) < (0, 0):
            if (self.df['MACD_12_26_9'].array[-2], self.df['MACDs_12_26_9'].array[-2]) >= (0, 0):
                self.macd_dict['MACD 0 cross'] = False


    def ema_signals(self):
        ema_200 = self.df['ema_200'].array[-3:]
        ema_50 = self.df['ema_50'].array[-3:]
        ema_20 = self.df['ema_20'].array[-3:]
        price = self.df['close'].array[-3:]
        if ema_200[0] > price[0] and ema_200[1] >= price[1] and ema_200[2] < price[2]:
            self.ema_signals_dict['Price crossing EMA200'] = True
        elif ema_200[0] < price[0] and ema_200[1] <= price[1] and ema_200[2] > price[2]:
            self.ema_signals_dict['Price crossing EMA200'] = False
        if ema_20[0] > ema_50[0] and ema_20[1] >= ema_50[1] and ema_20[2] < ema_50[2]:
            self.ema_signals_dict['EMA20 crossing EMA50'] = False
        elif ema_20[0] < ema_50[0] and ema_20[1] <= ema_50[1] and ema_20[2] > ema_50[2]:
            self.ema_signals_dict['EMA20 crossing EMA50'] = True
        if ema_50[0] > ema_200[0] and ema_50[1] >= ema_200[1] and ema_50[2] < ema_200[2]:
            self.ema_signals_dict['EMA50 crossing EMA200'] = False
        elif ema_50[0] < ema_200[0] and ema_50[1] <= ema_200[1] and ema_50[2] > ema_200[2]:
            self.ema_signals_dict['EMA50 crossing EMA200'] = True
        return self.ema_signals_dict

    def vol_rise_fall(self):
        recent_vol = self.df.volume.tail(3).array
        self.vol_signal = True if recent_vol[0] < recent_vol[1] < recent_vol[2] else False
        return self.vol_signal

    def large_vol_candle(self):
        self.vol_candle = True if self.df.volume.array[-1] >= self.df.volume.tail(14).values.mean()*2 else False
        return self.vol_candle

    def plot_charts(self):
        self.main_chart()
        self.plot_rsi_div()
        self.plot_emas()

if __name__ == '__main__':
    sig = Signals('ADAUSDT')
    print(len(sig.df))
    sig.plot_charts()