from setuptools import setup

setup(
    name='ssmx',
    version='v1.0.0',
    py_modules=['ssmx'],
    download_url="https://github.com/JetJet13/ssmx/archive/v1.0.0.tar.gz",
    include_package_data=True,
    install_requires=[
        'click',
        'boto3',
        'tabulate',
        'subprocess32'
    ],
    entry_points='''
        [console_scripts]
        ssmx=ssmx:cli
    '''
)
