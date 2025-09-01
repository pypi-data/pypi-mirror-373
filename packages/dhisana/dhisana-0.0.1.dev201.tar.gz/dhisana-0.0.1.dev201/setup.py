from setuptools import setup, find_packages

setup(
    name='dhisana',  
    version='0.0.1-dev201',
    description='A Python SDK for Dhisana AI Platform',
    author='Admin',
    author_email='contact@dhisana.ai',
    url='https://github.com/dhisana-ai/dhisana-python-sdk',
    license='MIT',
    packages=find_packages(where='src'), 
    package_dir={'': 'src'},
    install_requires=[
        'bs4',
        'click>=7.0',
        'fastapi',
        'google-api-python-client',
        'google-auth',
        'openai',
        'playwright',
        'requests',
        'uvicorn[standard]',
        'aiohttp',
        'openapi_pydantic',
        'pandas',
        'simple_salesforce',
        'backoff',
        'html2text',
        'hubspot-api-client',
        'tldextract',
        'pyperclip',
        'azure-storage-blob',
        'email_validator',
        'fqdn',
        'json_repair'
    ],
    entry_points={
        'console_scripts': [
            'dhisana=dhisana.cli.cli:main',
        ],
    },    
    classifiers=[
        'Development Status :: 3 - Alpha', 
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License', 
        'Programming Language :: Python :: 3.8'
    ],
    python_requires='>=3.8',
)
