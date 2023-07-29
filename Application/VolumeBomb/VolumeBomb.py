import ccxt.async_support as ccxt
import asyncio
import nest_asyncio
import pandas as pd
from Base.Connector import DiscordConnector
from Base.ConfigReader import Config
nest_asyncio.apply()


class Connector(object):
    def __init__(self):
        self.config = Config()


class VolumeBomb(Connector):

    VALID_SYMBOL = ['BTCUSDT', 'ETHUSDT']

    def __init__(self):
        super().__init__()
        self.EXCHANGE = 'Binance'
        self.discord = DiscordConnector()
        self.exchange = ccxt.binanceusdm({
            'apiKey': self.config['Binance']['apiKey'],
            'secret': self.config['Binance']['secret'],
            'enableRateLimit': True,
            'options': {
                'defaultMarket': 'future',
            }
        })

    async def run(self):
        ohlcv_dict = await self.getKline()
        for symbol, ohlcv_df in ohlcv_dict.items():
            mean_volume = self.cleanData2GenerateMeanVolume(ohlcv_df)
            self.checkSignal(symbol, mean_volume, ohlcv_df)

    async def get_ohlcv(self, symbol, timeframe):
        return await self.exchange.fetch_ohlcv(symbol, timeframe, limit=100)

    async def getKline(self) -> dict:
        ohlcv_dict = {}
        tasks = []
        for symbol in self.VALID_SYMBOL:
            task = asyncio.create_task(self.get_ohlcv(symbol, '3m'))
            tasks.append(task)

        responses = await asyncio.gather(*tasks)
        for i, response in enumerate(responses):
            symbol = self.VALID_SYMBOL[i]

            df = pd.DataFrame(response, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
            df['time'] = df['time'].astype(int)
            df['open'] = df['open'].astype(float)
            df['high'] = df['high'].astype(float)
            df['low'] = df['low'].astype(float)
            df['close'] = df['close'].astype(float)
            df['volume'] = df['volume'].astype(float)

            if symbol not in ohlcv_dict:
                ohlcv_dict[symbol] = {}
            ohlcv_dict[symbol]= df
        return ohlcv_dict

    def cleanData2GenerateMeanVolume(self, ohlcv_df):
        volume = ohlcv_df['volume']
        Q1 = volume.quantile(0.25)
        Q3 = volume.quantile(0.75)
        IQR = Q3 - Q1
        mean_volume = volume[(volume >= Q1 - 1.5 * IQR) & (volume <= Q3 + 1.5 * IQR)].mean()
        return mean_volume

    def checkSignal(self, symbol, mean_volume, ohlcv_df):
        slope = ohlcv_df['CLOSE'].iloc[-1] - ohlcv_df['CLOSE'].iloc[-10]

        if slope <= 0:
            trend = '下跌'
        else:
            trend = '上漲'

        if ohlcv_df['volume'].iloc[-1] >= mean_volume * 9:
            message = f"**[🔥｜Volume Bomb]**\n**{symbol}爆量{trend}**\n```現價：{ohlcv_df['close'].iloc[-1]}\n成交量：{ohlcv_df['volume'].iloc[-1]}```"
            self.discord.sendMessage(self.config['Discord']['VolumeBomb'], message)

