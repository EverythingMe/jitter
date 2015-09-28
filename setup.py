VERSION = "0.1.2"
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'JITT Command Line Tool',
    'author': 'Adam Kariv',
    'url': 'http://jitt.it',
    'download_url': 'https://github.com/EverythingMe/jitter/tarball/'+VERSION,
    'author_email': 'adam@everything.me',
    'version': VERSION,
    'install_requires': [
        'click',
        'nose',
        'lxml',
    ],
    'packages': ['jitter', 'jitter.android'],
    'scripts': [],
    'name': 'jitter',
    'entry_points':{
        'console_scripts': [
            'jitter = jitter.cli:entrypoint',
        ]
    },
}

setup(**config)
