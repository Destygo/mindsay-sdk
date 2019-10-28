# pylint: skip-file
import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='mindsay-sdk',
    version='1.0.0',
    author='Mindsay tech team',
    author_email='tech@mindsay.com',
    description='Mindsay python client',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/Destygo/mindsay-sdk',
    packages=setuptools.find_packages(),
    install_requires=[
        'requests'
    ],
    classifiers=[
        'Programming Language :: Python :: 3.7',
        'Operating System :: OS Independent',
    ],
)
