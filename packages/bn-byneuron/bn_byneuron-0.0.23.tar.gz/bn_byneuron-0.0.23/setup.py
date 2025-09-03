# setup.py
from setuptools import setup, find_packages

setup(
    name='bn_byneuron',  # only lowercase and dashes
    version='0.0.23',
    author='jovi',
    author_email='jo.vinckier@bynubian.com',
    description='API for byneuron backend',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://gitlab.com/bynubian/bynode/python_packages/byneuron',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
    install_requires=[
        'requests>=2.32.4',
        # 'python-decouple>=3.8'
        # dependencies: other packages required
        # eg 'numpy>=1.11.1'
    ]
)
