from setuptools import setup, find_packages

setup(
    name='parsing-module-library',
    version='0.1.0',
    author='Your Name',
    author_email='your.email@example.com',
    description='A library for parsing and processing data artifacts.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/parsing-module-library',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    include_package_data=True,
    install_requires=[
        'pandas',
        'numpy',
        'jsonschema',
        'boto3',
    ],
    extras_require={
        'dev': [
            'pytest',
            'black',  # Add other development dependencies here
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)