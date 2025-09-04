from setuptools import setup

setup(
    name='gima',
    version='1.0.7',
    author='Arkadiusz Hypki',
    description='Software which simplifies managing many git repositories through a console',
    packages=['gima', 'gima/db', 'gima/git', 'gima/utils'],
    include_package_data=True,
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    install_requires=[
        'pygit2'
    ],
    entry_points = {
        'console_scripts': [
            'gima = gima.gima:main'
        ]
    },
)
