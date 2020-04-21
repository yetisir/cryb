#from setuptools import setup, find_namespace_packages
#from sphinx.setup_command import BuildDoc

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
#    packages=find_namespace_packages(
#        include=['data.*', 'geometry.*', 'modelling.*', 'plot.*']),
    install_requires=[
        'scrapy',
 #         'sphinx',
 #         'sphinx_rtd_theme',
#          'pytest',
 #         'pytest-flakes',
  #        'pyyaml',
  #        'configurator',
  #        'tqdm',
  #        'pandas',
  #        'sqlalchemy',
  #        'psutil',
          ],
    zip_safe=False,
 #   cmdclass={'build_sphinx': BuildDoc},
    entry_points={
        'console_scripts': [
            'cryb = cryb.__main__:main',
            ],
        },
  #  command_options={
   #     'build_sphinx': {
    #        'project': ('setup.py', name),
     #       'version': ('setup.py', version),
      #      'source_dir': ('setup.py', 'docs'),
       #     },
        #}
    )

