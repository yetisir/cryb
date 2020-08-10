from setuptools import setup

name = 'cryb-coingecko'
version = '0.0.1'

setup(
    name=name,
    version=version,
    description='CoinGecko downloader for Cryb',
    url='https://github.com/yetisir/cryb',
    author='M. Yetisir',
    author_email='yetisir@gmail.com',
    license='GNU GPL v3.0',
    install_requires=[
        'psycopg2-binary',
        'pycoingecko',
        'sqlalchemy',
        'marshmallow',
        'marshmallow_sqlalchemy',
        'pyyaml',
    ],
    zip_safe=False,
)
