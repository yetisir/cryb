from setuptools import setup


setup(
    name='Cryb',
    version='0.1.0',
    description='Cryptocurrency data scraper',
    url='https://github.com/yetisir/cryb',
    author='M. Yetisir',
    author_email='yetisir@gmail.com',
    install_requires=[
        # 'arctic>=1.79',
        'celery>=4.4',
        'configurator[yaml]>=2.0',
        'redis>=3.5'
    ],
    # extras_require={
    #     'dev': [
    #         'coveralls>=2.0',
    #         'mkdocs>=1.1',
    #         'pip-tools>=5.1',
    #         'pytest>=5.4',
    #         'pytest-cov>=2.8',
    #         'pytest-flake8>=1.0',
    #     ],
    # },
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'cryb = cryb.__main__:main',
        ],
    },
)
