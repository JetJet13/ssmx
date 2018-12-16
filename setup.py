from setuptools import setup

setup(
    name='ssmx',
    version='0.1',
    py_modules=['ssmx'],
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