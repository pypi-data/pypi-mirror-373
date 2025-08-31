from setuptools import setup

setup(
    name='lockserver-client',
    version='0.1.0',
    description='Python client SDK for lockserver (distributed lock server)',
    author='Ben Liao',
    author_email='abenliao@gmail.com',
    py_modules=['lockserver_client'],
    install_requires=['requests'],
    url='https://github.com/benliao/lockserver',
    keywords='distributed lock server client sdk python',
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
