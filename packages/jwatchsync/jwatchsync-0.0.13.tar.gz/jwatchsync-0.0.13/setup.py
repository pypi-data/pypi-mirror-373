from setuptools import setup, find_packages

setup(
    name='jwatchsync',
    version='0.0.13',
    packages=find_packages(),
    install_requires=[
        'requests>=2.32.4'
    ],
    author='qquiroa',
    author_email='jmata@launion.com.gt',
    description='Libreria para escribir y consultar información en JWatch',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://bitbucket.org/desarrolloilu/rep-ti-jwatch/src/develop/JWatchSync-PY/',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.9',
)

# Para construir el paquete y subirlo a PyPi:
# python setup.py sdist bdist_wheel
# twine upload dist/*
# rm -rf build dist jwatchsync.egg-info