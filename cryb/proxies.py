import subprocess
import requests

import requests_cache
from stem.control import Controller


def random_proxy():
    with requests_cache.disabled():
        response = requests.get(
            'https://gimmeproxy.com/api/getProxy'
            '?supportsHttps=true&anonymous=1&protocol=http&ipPort=1',
            proxies={'https': 'socks5h://localhost:9050'}
        )

    if response.status_code == '200':
        return response.text
    else:
        print('resetting TOR')
        with Controller.from_port(port=9051) as controller:
            controller.authenticate()
            controller.signal('NEWNYM')
        return random_proxy()
