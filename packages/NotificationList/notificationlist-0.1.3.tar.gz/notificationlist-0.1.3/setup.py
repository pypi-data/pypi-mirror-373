from setuptools import setup, find_packages

setup(
    name='NotificationList',
    version='0.1.3',
    author='Ranjeet Aloriya',
    author_email='ranjeet.aloriya@gmail.com',
    description='A Python package for consolidating breach response notification lists efficiently.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    install_requires=[
        'pandas',
        'polars'
    ],
    license='MIT',
    include_package_data=False,  # Disable this to avoid license-file problem
)