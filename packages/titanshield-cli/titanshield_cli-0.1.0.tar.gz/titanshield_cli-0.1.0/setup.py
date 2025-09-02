from setuptools import setup, find_packages

setup(
    name='titanshield-cli',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'pyaxmlparser',
        'pyyaml',
        'rich', 
    ],
    entry_points={
        'console_scripts': [
            'titanshield=titanshield_cli.main:cli',
        ],
    },
)