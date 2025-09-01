from setuptools import setup, find_packages
import os

def get_version():
    init_file = os.path.join(os.path.dirname(__file__), 'foreva_ai', '__init__.py')
    with open(init_file, 'r') as f:
        for line in f:
            if line.startswith('__version__'):
                return line.split('=')[1].strip().strip('"\'')
    return '0.1.0'

def get_long_description():
    readme_file = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_file):
        with open(readme_file, 'r', encoding='utf-8') as f:
            return f.read()
    return "Foreva AI SDK for restaurant voice AI integration"

setup(
    name='foreva-ai',
    version=get_version(),
    author="Foreva AI",
    author_email="support@foreva.ai",
    description="Voice AI for restaurants - Python SDK for Partners",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url="https://foreva.ai/partners",
    project_urls={
        "Documentation": "https://foreva.ai/partners/docs",
        "Support": "https://foreva.ai/partners/support",
        "Dashboard": "https://foreva.ai/partners/dashboard",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Communications :: Telephony",
        "Topic :: Office/Business :: Financial :: Point-Of-Sale",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
        "typing-extensions>=4.0.0; python_version<'3.10'",
    ],
    entry_points={
        "console_scripts": [
            "foreva=foreva_ai.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "foreva_ai": [
            "examples/*.py",
        ],
    },
    zip_safe=False,
)
