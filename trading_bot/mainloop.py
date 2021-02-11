import time
from datetime import datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from signals import Signals
import logging
scheduler = BackgroundScheduler()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, filename='log.log')

from tg_bot import BaseBot


class MainLoop:

    bot = BaseBot('1698743512:AAFnBVoOOx0DmWF6isruGxMviceRaCHBsmc', channel='-1001390028426')

    def __init__(self, coins):
        check_dict = {}
        self.coins = coins
        self.check_dict = {}

    def set_up(self):
        for coin in self.coins:
            self.check_dict[coin] = []

    def mainloop(self):
        for coin in self.coins:
            check_time = datetime.now()
            signals = Signals(coin)
            for k, v in signals.ema_signals_dict.items():
                if v is True:
                    alert = (check_time.strftime("%H:%M:%S"), k, 'bullish')
                    if k not in [t[1] for t in self.check_dict[coin]]:
                        self.bot.broadcast(f'[{alert[0]}] {coin}: {alert[1]} ({alert[2]})')
                        self.check_dict[coin].append(alert)
                elif v is False:
                    alert = (check_time.strftime("%H:%M:%S"), k, 'bearish')
                    if k not in [t[1] for t in self.check_dict[coin]]:
                        self.bot.broadcast(f'[{alert[0]}] {coin}: {alert[1]} ({alert[2]})')
                        self.check_dict[coin].append(alert)
            for k, v in signals.rsi_div_dict.items():
                if v is True:
                    alert = (check_time.strftime("%H:%M:%S"), k)
                    if k not in [t[1] for t in self.check_dict[coin]]:
                        self.bot.broadcast(f'[{alert[0]}] {coin}: {alert[1]}')
                        self.check_dict[coin].append(alert)
            for k, v in signals.rsi_ob_os_dict.items():
                if v is True:
                    alert = (check_time.strftime("%H:%M:%S"), k)
                    if k not in [t[1] for t in self.check_dict[coin]]:
                        self.bot.broadcast(f'[{alert[0]}] {coin}: {alert[1]}')
                        self.check_dict[coin].append(alert)
            for k, v in signals.macd_dict.items():
                if v is not None:
                    if v is True:
                        v = 'up'
                    else:
                        v = 'down'
                    alert = (check_time.strftime("%H:%M:%S"),' '.join((k,v)))
                    if alert[1] not in [t[1] for t in self.check_dict[coin]]:
                        self.bot.broadcast(f'[{alert[0]}] {coin}: {alert[1]}')
                        self.check_dict[coin].append(alert)
            if signals.vol_signal:
                alert = (check_time.strftime("%H:%M:%S"), 'Volume rising')
                if alert[1] not in [t[1] for t in self.check_dict[coin]]:
                    self.bot.broadcast(f'[{alert[0]}] {coin}: {alert[1]}')
                    self.check_dict[coin].append(alert)
            if signals.vol_candle:
                alert = (check_time.strftime("%H:%M:%S"), 'Current candle large volume')
                if alert[1] not in [t[1] for t in self.check_dict[coin]]:
                    self.bot.broadcast(f'[{alert[0]}] {coin}: {alert[1]}')
                    self.check_dict[coin].append(alert)
            for alert in self.check_dict[coin]:
                full_time = datetime.strptime(datetime.now().strftime('%Y-%m-%d ') + alert[0],
                                              '%Y-%m-%d %H:%M:%S')
                if full_time < datetime.now() - timedelta(minutes=15):
                    self.check_dict[coin].remove(alert)

    def print_checklist(self):
        print(self.check_dict)


if __name__ == '__main__':

    coins = ["DOGEUSDT","XRPUSDT","XLMUSDT","BNBUSDT",
             "BCHUSDT","AAVEUSDT","UNIUSDT","EGLDUSDT",
             "SXPUSDT","MKRUSDT","SUSHIUSDT","EOSUSDT",
             "DOTUSDT","ADAUSDT","BTCUSDT","ETHUSDT",
             "LTCUSDT","LINKUSDT","XTZUSDT","MATICUSDT"]
    loop = MainLoop(coins)
    loop.set_up()
    loop.mainloop()
    scheduler.start()
    scheduler.add_job(loop.mainloop, trigger="interval", minutes=5)
    while True:
        time.sleep(300)