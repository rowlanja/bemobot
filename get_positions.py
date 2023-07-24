from binance.client import Client
import os

def get_positions():
    client = Client(os.environ.get('API_KEY'), os.environ.get('API_SECRET'), {"verify": False, "timeout": 20})
    positions = client.futures_account()['positions']
    positions = pd.DataFrame.from_dict(positions)
    positions = positions.loc[positions['symbol'] == f'{SYMBOL_INPUT}']
    print(positions)