import os
from setuptools import setup, find_packages


f = open(os.path.join(os.path.dirname(__file__), 'README.rst'))
readme = f.read()
f.close()


setup(
    name='PyAxe',
    version=__import__('PyAxe').__version__,
    description='An utility library for building command-line tool easily',
    long_description=readme,
    author='Sun Jin',
    author_email='412640665@qq.com',
    url='https://github.com/sunjinopensource/PyAxe/',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
    ],
)
