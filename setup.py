from setuptools import setup, find_packages

setup(
    name='alteryx-pyx',
    version='0.2.0',
    description='Python library for reading, writing, and analyzing Alteryx Designer workflow files (.yxmd)',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    license='GPL-3.0-only',
    packages=find_packages(),
    python_requires='>=3.10',
    install_requires=[
        'xmltodict',
    ],
    url='https://github.com/Ozzeron/alteryx-pyx',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    ],
)
