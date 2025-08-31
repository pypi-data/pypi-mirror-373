from setuptools import setup, find_packages
from pathlib import Path


# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

def read_version():
    version_path = Path(__file__).parent / "scribe_python_client" / "version.py"
    with open(version_path) as f:
        for line in f:
            if line.startswith("__version__"):
                delim = '"' if '"' in line else "'"
                return line.split(delim)[1]
    raise RuntimeError("Unable to find version string.")

__version__ = read_version()

setup(
    name='scribe-python-client',
    version=__version__,
    packages=find_packages(include=['scribe_python_client', 'scribe_python_client.*']),
    include_package_data=True,
    install_requires=[
        'requests',
        'PyJWT',
        'python-dotenv',
        # ONLY base/core dependencies here
    ],
    extras_require={
    'mcp': [
        'fastapi',
        'uvicorn',
        'fastapi_mcp',
        'python-dotenv',
    ],
    'graph': [
        'plotly',
        'numpy',
        'networkx',
        'pyvis',
    ],
    'all': [
        'fastapi',
        'uvicorn',
        'fastapi_mcp',
        'plotly',
        'numpy',
        'networkx',
        'pyvis',
        'python-dotenv',
    ],
},
    entry_points={
    "console_scripts": [
        "scribe-client = scribe_python_client.cli:main"
        ]
    },
    description='A Python client for interacting with ScribeHub.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Daniel Nebenzahl',
    author_email='dn@scribesecurity.com',
    url='https://github.com/scribe-security/scribe-python-client',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    package_data={
        'scribe_python_client.mcp_app.toolsDescriptions': [
            '*.json', '*.py',
            'fullToolDocs/*.json'
        ]
    },
)