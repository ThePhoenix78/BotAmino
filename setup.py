from setuptools import setup, find_packages
from BotAmino.__init__ import __version__

with open("README.md", "r") as stream:
    long_description = stream.read()

setup(
    name='BotAmino',
    version=__version__,
    url='https://github.com/ThePhoenix78/AminoBot',
    download_url='https://github.com/ThePhoenix78/AminoBot/tarball/master',
    license='MIT',
    author='ThePhoenix78, Vedansh',
    author_email='thephoenix788@gmail.com',
    description='A library to create Amino bots.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords=[
        'aminoapps',
        'amino-py',
        'amino',
        'amino-bot',
        'narvii',
        'api',
        'python',
        'python3',
        'python3.x',
        'ThePhoenix78',
        'AminoBot',
        'BotAmino',
        'botamino',
        'aminobot'
    ],
    install_requires=[
        'setuptools',
        'requests',
        'six',
        'websocket-client',
        'pathlib'
    ],
    setup_requires=[
        'wheel'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=find_packages()
    # packages=["sdist", "bdist_wheel"]
    # python_requires='>=3.6',
)
