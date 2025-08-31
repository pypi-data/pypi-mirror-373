from setuptools import setup, find_packages
import os

with open(os.path.join(os.path.dirname(__file__), 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='newrcc',
    version='0.3.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires= [],
    author='RestRegular',
    author_email='3228097751@qq.com',
    description='A tool that can make your console output beautiful.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ]
)