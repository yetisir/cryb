import downloader

def main():
    coin_gecko = downloader.CoinGecko()
    coin_gecko.get_coin_info()
