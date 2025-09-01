from setuptools import setup, find_packages

setup(
    name='rcquant_sdk',
    version='0.0.250901.09',
    description='rcquant_sdk',
    author='rcquant_sdk',
    author_email='rcquant_sdk@example.com',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    install_requires=[
        'msgpack',
        'numpy',
        'pandas',
    ],
    python_requires='>=3.6',
)
