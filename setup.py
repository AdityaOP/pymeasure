from distutils.core import setup

setup(
    name='Automate',
    version='0.1.0',
    author='Colin Jermain',
    author_email='clj72@cornell.edu',
    packages=['automate'],
    scripts=[],
    url='',
    license='LICENSE.txt',
    description='Automation objects for instrument control',
    long_description=open('README').read(),
    install_requires=[
        "Numpy >= 1.6.1",
    ],
)
