import aiohttp
import asyncio
import nest_asyncio
import yfinance as yf
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from Base.Connector import MongoDBConnector, DiscordConnector
from Base.ConfigReader import Config
nest_asyncio.apply()


class Connector(object):
    def __init__(self):
        self.config = Config()


class MagicFormula(Connector):
    def __init__(self):
        super().__init__()
        self.mongo = MongoDBConnector().getConn()
        self.discord = DiscordConnector()
        self.webhook = self.config['Discord']['MagicFormula']

    async def run(self):
        stocks = list(self.mongo['stock_list']['taiwan_50'].find({}))

        tasks = []
        for stock in stocks:
            tasks.append(self.get_stock_info(stock['stock_num'], stock['stock_name']))

        data = await asyncio.gather(*tasks)
        df = pd.DataFrame(data, columns=['stock_name', 'financial_data'])
        df = pd.concat([df.drop(['financial_data'], axis=1), df['financial_data'].apply(pd.Series)], axis=1)

        df = self.calculate_earnings_yield(df)
        df = self.calculate_roic(df)
        df = self.rank_companies(df)

        df = df['stock_name']
        df = df.reset_index(drop=True)

        top_10 = df.head(10).tolist()
        top_10_set = set(top_10)
        old_top_10_set = set(self.mongo['indicators']['magic_formula'].find_one({'name': 'magic_formula'})['stocks'])

        out_of_top_10 = list(old_top_10_set - top_10_set)
        into_top_10 = list(top_10_set - old_top_10_set)

        message = "**[🧙‍♀️｜Magic Formula]**\n**今日的前十名股票:**\n```" + "\n".join(top_10) + "```"
        if out_of_top_10:
            message += "\n**股票踢出前十名:**\n```" + "\n".join(out_of_top_10) + "```"
        if into_top_10:
            message += "\n**股票進入前十名:**\n```" + "\n".join(into_top_10) + "```"

        self.discord.sendMessage(self.webhook, message)

    async def get_ebit(self, session, stock):
        url = f'https://histock.tw/stock/{str(stock)}/%E6%90%8D%E7%9B%8A%E8%A1%A8'
        async with session.get(url) as res:
            soup = BeautifulSoup(await res.text(), 'html.parser')
            total_asset_row = soup.find('tr', class_='alt-row')
            total_asset = total_asset_row.find_all('td')
            result = int(total_asset[4].text.replace(',', ''))
            return result

    async def get_bv(self, session, stock): # 每股淨值
        url = f'https://histock.tw/stock/{str(stock)}/%E6%AF%8F%E8%82%A1%E6%B7%A8%E5%80%BC'
        bv = np.nan
        async with session.get(url) as res:
            soup = BeautifulSoup(await res.text(), 'html.parser')
            row = soup.find('tr', class_='alt-row')
            row = row.find_all('td')
            for i in range(len(row)):
                if row[i].text == '-':
                    break
                else:
                    bv = float(row[i].text.replace(',', ''))
            return bv

    async def get_total_asset_total_debt_and_current_liabiliby(self, session, stock):
        url = f'https://histock.tw/stock/{str(stock)}/%E8%82%A1%E6%9D%B1%E6%AC%8A%E7%9B%8A'
        async with session.get(url) as res:
            soup = BeautifulSoup(await res.text(), 'html.parser')
            row = soup.find('tr', class_='alt-row')
            row = row.find_all('td')
            total_asset = int(row[6].text.replace(',', ''))
            total_debt = int(row[4].text.replace(',', ''))
            current_liability = int(row[1].text.replace(',', ''))
            return total_asset, total_debt, current_liability

    async def get_outstanding_share(self, session, stock):
        url = f'https://histock.tw/stock/{str(stock)}/%E5%85%AC%E5%8F%B8%E8%B3%87%E6%96%99'
        async with session.get(url) as res:
            soup = BeautifulSoup(await res.text(), 'html.parser')
            share_row = soup.find('tr')
            share_row = share_row.find_all('tr')[1].text
            share_row = share_row.strip().replace('\n', '|').split('|')
            share = int(share_row[-1].replace(',', ''))
            return share

    async def get_latest_price(self, stock):
        start  = datetime.now() - timedelta(days=5)
        df = yf.download(f'{str(stock)}.TW', start=start, progress=False)
        return df['Adj Close'].iloc[-1]

    async def get_stock_info(self, stock, stock_name):
        tasks = []

        async with aiohttp.ClientSession() as session:
            tasks.append(self.get_outstanding_share(session, stock))
            tasks.append(self.get_ebit(session, stock))
            tasks.append(self.get_total_asset_total_debt_and_current_liabiliby(session, stock))
            tasks.append(self.get_latest_price(stock))
            tasks.append(self.get_bv(session, stock))
            response = await asyncio.gather(*tasks)

        result = {}
        result['outstanding_share'] = response[0]
        result['EBIT'] = response[1]
        result['total_asset'] = response[2][0]
        result['total_debt'] = response[2][1]
        result['current_liability'] = response[2][2]
        result['price'] = response[3]
        result['book_value'] = response[4]
        return [stock_name, result]

    def calculate_earnings_yield(self, df):
        df['Enterprise Value'] = df['outstanding_share'] * df['price'] + df['total_debt']
        df['Earnings Yield'] = df['EBIT'] / df['Enterprise Value']
        return df

    def calculate_roic(self, df):
        df['ROIC'] = df['EBIT'] / (df['total_asset'] - df['current_liability'])
        return df

    def rank_companies(self, df):
        df['Earnings Yield Rank'] = df['Earnings Yield'].rank(ascending=False)
        df['ROIC Rank'] = df['ROIC'].rank(ascending=False)
        df['Magic Formula Rank'] = df['Earnings Yield Rank'] + df['ROIC Rank']
        df = df.sort_values(by='Magic Formula Rank', ascending=True)
        return df

if __name__ == '__main__':
    magic_formula = MagicFormula()
    asyncio.run(magic_formula.analyze())