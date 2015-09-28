
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'JITT Command Line Tool',
    'author': 'Adam Kariv',
    'url': 'http://jitt.it',
    'download_url': 'http://jitt.it',
    'author_email': 'adam@everything.me',
    'version': '0.1',
    'install_requires': [
        'click',
        'nose',
        'lxml',
    ],
    'packages': ['jitter'],
    'scripts': [],
    'name': 'jitter',
    'entry_points':{
        'console_scripts': [
            'jitter = jitter.cli:entrypoint',
        ]
    },
}

setup(**config)
