import requests
import proxyscrape

print('getting proxy ....')
collector = proxyscrape.create_collector('collector', ['https'])
https_proxy = collector.get_proxy({'anonymous': True, 'type': 'https'})
http_proxy = collector.get_proxy({'anonymous': True, 'type': 'http'})
proxies = {
    'https': f'{https_proxy.host}:{https_proxy.port}',
    'http': f'{http_proxy.host}:{http_proxy.port}',
}

print('getting request ...')
url = 'https://api.coingecko.com/api/v3/ping'
requests.get(url, proxies=proxies)
