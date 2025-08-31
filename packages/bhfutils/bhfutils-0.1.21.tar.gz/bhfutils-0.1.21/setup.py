import sys
from setuptools import setup, find_packages


def readme():
    ''' Returns README.rst contents as str '''
    with open('README.rst') as f:
        return f.read()


install_requires = [
    'python-json-logger==0.1.8',
    'redis>=4.0.2',
    'kazoo>=2.8.0',
    'mock>=4.0.3',
    'playwright>=1.17.2',
    'testfixtures>=6.18.3',
    'ujson>=4.3.0',
    'future>=0.18.2'
]

lint_requires = [
    'pep8',
    'pyflakes'
]

tests_require = [
    'mock>=2.0.0',
    'testfixtures>=4.13.5'
]

dependency_links = []
setup_requires = []
extras_require = {
    'test': tests_require,
    'all': install_requires + tests_require,
    'docs': ['sphinx'] + tests_require,
    'lint': lint_requires
}

if 'nosetests' in sys.argv[1:]:
    setup_requires.append('nose')

setup(
    name='bhfutils',
    version='0.1.21',
    description='Utilities that are used by any spider of Behoof project',
    long_description=readme(),
    long_description_content_type='text/x-rst',
    author='Teplygin Vladimir',
    author_email='vvteplygin@gmail.com',
    license='MIT',
    url='https://behoof.app/',
    keywords=['behoof', 'scrapy-cluster', 'utilities'],
    packages=find_packages(),
    package_data={},
    install_requires=install_requires,
    tests_require=tests_require,
    setup_requires=setup_requires,
    extras_require=extras_require,
    dependency_links=dependency_links,
    zip_safe=True,
    include_package_data=True,
)
