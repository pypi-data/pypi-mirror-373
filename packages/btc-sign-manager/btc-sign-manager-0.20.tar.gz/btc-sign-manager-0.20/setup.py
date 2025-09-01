import os

from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='btc-sign-manager',
    version='0.20',
    packages=['sign_manager'],
    include_package_data=True,
    license='BSD License',
    description='An application for cryptographic signing of models, files and etc.',
    long_description=README,
    url='https://github.com/MEADez/btc-sign-manager',
    author='MEADez',
    author_email='m3adez@gmail.com',
    install_requires=['Django>=2.1.4', 'django_redis>=4.10.0', 'PyMuPDF>=1.16.2'],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
