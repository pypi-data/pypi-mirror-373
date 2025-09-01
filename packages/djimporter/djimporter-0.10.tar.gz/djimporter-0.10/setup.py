import os
from distutils.util import convert_path

from setuptools import find_packages, setup

main_ns = {}
ver_path = convert_path('djimporter/__init__.py')
with open(ver_path) as ver_file:
    exec(ver_file.read(), main_ns)

version = main_ns['get_version']()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))


setup(
    name="djimporter",
    version=version,
    url='https://github.com/ico-apps/django-importer',
    author='ICO - Institut Catala Ornitologia',
    author_email='ico@ornitologia.org',
    description='Django importer, another CSV import library.',
    long_description=('Django importer, another CSV import library.'),
    license='BSD-3-Clause',
    packages=find_packages(),
    include_package_data=True,
    install_requires=["django>=2.2,<4.1", "django4-background-tasks>=1.2.9", "python-magic>=0.4.27"],
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 2.2',
        'Framework :: Django :: 3.2',
        'Framework :: Django :: 4',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
    ],
)
