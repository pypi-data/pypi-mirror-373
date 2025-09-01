#!/usr/bin/env python3
"""
Emergence Agent SDK Setup
Official Python SDK for building and deploying agents on the Emergence Platform
"""

from setuptools import setup, find_packages
import os

# Read version from version file
def get_version():
    version_file = os.path.join(os.path.dirname(__file__), 'emergence_agent', 'version.py')
    try:
        with open(version_file, 'r') as f:
            exec(f.read())
            return locals()['__version__']
    except FileNotFoundError:
        return '0.1.0'

# Read long description from README
def get_long_description():
    readme_file = os.path.join(os.path.dirname(__file__), 'README.md')
    try:
        with open(readme_file, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "Emergence Agent SDK - Official Python SDK for the Emergence Platform"

# Read requirements
def get_requirements():
    req_file = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    try:
        with open(req_file, 'r') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    except FileNotFoundError:
        return [
            'requests>=2.31.0',
            'typing-extensions>=4.0.0;python_version<"3.9"',
            'aiohttp>=3.8.0',
        ]

setup(
    name='emergence-agent',
    version=get_version(),
    author='Emergence Platform Team',
    author_email='developers@emergence-platform.com',
    description='Official Python SDK for building and deploying intelligent agents on the Emergence Platform',
    long_description=get_long_description(),
    long_description_content_type='text/markdown',
    url='https://github.com/emergence-platform/emergence-agent-sdk',
    project_urls={
        'Homepage': 'https://emergence-platform.com',
        'Documentation': 'https://docs.emergence-platform.com/agent-sdk',
        'Repository': 'https://github.com/emergence-platform/emergence-agent-sdk',
        'Bug Reports': 'https://github.com/emergence-platform/emergence-agent-sdk/issues',
        'Platform': 'https://app.emergence-platform.com',
    },
    packages=find_packages(exclude=['tests*', 'examples*']),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Internet :: WWW/HTTP :: HTTP Servers',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Operating System :: OS Independent',
        'Environment :: Web Environment',
        'Framework :: AsyncIO',
    ],
    keywords=[
        'emergence', 'agent', 'ai', 'platform', 'sdk', 'webhook', 
        'automation', 'integration', 'api', 'client'
    ],
    python_requires='>=3.8',
    install_requires=get_requirements(),
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-asyncio>=0.21.0',
            'pytest-cov>=4.0.0',
            'black>=23.0.0',
            'flake8>=6.0.0',
            'mypy>=1.0.0',
            'isort>=5.12.0',
            'pre-commit>=3.0.0',
        ],
        'examples': [
            'flask>=2.3.0',
            'fastapi>=0.100.0',
            'uvicorn>=0.23.0',
            'celery>=5.3.0',
            'redis>=4.6.0',
        ],
        'all': [
            'pytest>=7.0.0',
            'pytest-asyncio>=0.21.0',
            'pytest-cov>=4.0.0',
            'black>=23.0.0',
            'flake8>=6.0.0',
            'mypy>=1.0.0',
            'isort>=5.12.0',
            'pre-commit>=3.0.0',
            'flask>=2.3.0',
            'fastapi>=0.100.0',
            'uvicorn>=0.23.0',
            'celery>=5.3.0',
            'redis>=4.6.0',
        ]
    },
    entry_points={
        'console_scripts': [
            'emergence-agent=emergence_agent.cli:main',
            'emergence-validate=emergence_agent.cli:validate_agent',
            'emergence-deploy=emergence_agent.cli:deploy_agent',
        ],
    },
    include_package_data=True,
    package_data={
        'emergence_agent': [
            'templates/*.py',
            'templates/*.json',
            'schemas/*.json',
        ],
    },
    zip_safe=False,
    license='MIT',
    platforms=['any'],
)