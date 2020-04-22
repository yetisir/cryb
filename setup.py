from setuptools import setup

name = 'cryb'
version = '0.0.1'

setup(
    name=name,
    version=version,
    description='Cryb',
    url='https://github.com/yetisir/cryb',
    author='M. Yetisir',
    author_email='yetisir@gmail.com',
    license='GNU GPL v3.0',
    install_requires=[
        'scrapy',
    ],
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'cryb = cryb.__main__:main',
            ],
        },
    )
