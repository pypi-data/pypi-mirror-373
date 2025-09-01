from setuptools import setup, find_packages
from pathlib import Path
from kin_tokenizer.version import VERSION

# Read long description
long_description = (Path(__file__).parent / "README.md").read_text()

setup(
    name='alta_tokenizer',
    version=VERSION, 
    author='Schadrack Niyibizi',
    author_email='niyibizischadrack@gmail.com',
    description='ALTA tokenizer for encoding and decoding Kinyarwanda language text',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/Nschadrack/Kin-Tokenizer',
    packages=find_packages(),
    keywords="Tokenizer, Kinyarwanda, ALTA Model",
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',  # Add your license
        'Intended Audience :: Developers',
        'Topic :: Text Processing :: Linguistic',
    ],
    python_requires='>=3.12',
    install_requires=[
        "regex>=2024.7.24",
        "requests>=2.32.3"  # Fixed package name and version
    ],
    package_data={
        'kin_tokenizer': ['data/*'],
    },
    include_package_data=True,
)