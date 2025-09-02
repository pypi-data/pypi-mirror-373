from pathlib import Path

from setuptools import setup, find_packages

setup(
    name='agentic-kit-common',
    version="0.0.3",
    author="manson",
    author_email="manson.li3307@gmail.com",
    description='Common utilities and tools for agentic kit ecosystem, including MinIO manager and other shared components',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Distributed Computing',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent'
    ],
    python_requires='>=3.12',
    install_requires=[
        # MinIO dependencies
        "minio",
        "urllib3",
        
        # Core dependencies
        "pydantic",
        "requests",
        
        # Agent framework dependencies
        "langchain_core",
        "langgraph",
        "langchain_community",
        "langchain_experimental",

        # sqlalchemy
        "mysql-connector-python",
        "sqlalchemy",
    ],
    keywords=['AI', 'LLM', 'Agent', 'MinIO', 'Storage', 'Common', 'Utilities'],
    include_package_data=True,
    package_data={
        # If any package contains *.txt or *.rst files, include them:
        '': ['*.txt', '*.rst', '.csv', '*.json', '*.yaml', '*.yml']
    },
)