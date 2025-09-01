from setuptools import setup, find_packages

setup(
    name='scholr',
    version='0.2.3',
    author='Anas AlMutary',
    author_email='me@ianas.me',
    description='A lightweight scraper for Google Scholar',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/An4s0/Scholr',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires='>=3.7',
    install_requires=[
        'beautifulsoup4',
        'requests',
    ],
)