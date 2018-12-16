from setuptools import setup

setup(
    name='ssmx',
    version='1.0',
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
