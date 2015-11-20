"""

This file is part of the PyMeasure package.

Copyright (c) 2013-2015 Colin Jermain, Graham Rowlands

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

"""

from distutils.core import setup

setup(
    name='PyMeasure',
    version='0.2',
    author='Colin Jermain',
    author_email='clj72@cornell.edu',
    packages=[
        'pymeasure', 'pymeasure.instruments',
        'pymeasure.adapters', 'pymeasure.display',
        'pymeasure.experiment'
    ],
    scripts=[],
    url='',
    license='LICENSE.txt',
    description='Measurement automation library for Python instrument control',
    long_description=open('README.md').read(),
    install_requires=[
        "Numpy >= 1.6.1",
        "pandas >= 0.14",
        "pyzmq >= 14.7.0",
        "msgpack-python >= 0.4.6"
    ],
)
