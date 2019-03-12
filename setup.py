from setuptools import setup

with open("README.md", "r") as fh:
    long_description = '\n' + fh.read()

setup(
    name='ssmx',
    author="Johny Georges",
    author_email="jgeorges371@gmail.com",
    url="https://github.com/JetJet13/ssmx",
    python_requires=">=2.7",
    description="CLI tool for injecting parameters stored in AWS SSM into executables.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    version='v1.0.3',
    py_modules=['ssmx'],
    download_url="https://github.com/JetJet13/ssmx/archive/v1.0.2.tar.gz",
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
