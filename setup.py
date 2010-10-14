from distutils.core import setup
import datetime

setup(
    name = 'django-voting',
    version = "0.2",
    description = 'Generic voting application for Django',
    author = 'Jonathan Buchanan, stephan preeker',
    author_email = 'jonathan.buchanan@gmail.com',
    url = 'http://github.com/spreeker/django-voting2',
    packages = ['voting', 'voting.templatetags', 'voting.tests'],
    classifiers = ['Development Status :: 4 - Beta',
                   'Environment :: Web Environment',
                   'Framework :: Django',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: BSD License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Utilities'],
)
