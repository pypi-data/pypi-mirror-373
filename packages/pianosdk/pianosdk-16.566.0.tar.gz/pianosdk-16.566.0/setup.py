from setuptools import setup, find_packages

with open('README.md', encoding='utf-8') as f:
    readme = f.read()

setup(
    name='pianosdk',
    version='16.566.0',
    packages=find_packages(),
    # url='url will be here',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Software Development :: Libraries',
        
    ],
    license='Apache License, Version 2.0',
    description='Piano API SDK',
    long_description=readme,
    long_description_content_type='text/markdown',
    python_requires='>=3.7',
    install_requires=[
        'requests>=2.28.1',
        'pydantic==2.5.3',
        'pycryptodome>=3.15.0'
    ]
)
