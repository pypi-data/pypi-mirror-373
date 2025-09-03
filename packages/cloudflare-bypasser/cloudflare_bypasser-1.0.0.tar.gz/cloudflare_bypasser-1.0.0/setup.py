"""
Setup configuration for cloudflare-bypass package
"""
import os
from setuptools import setup, find_packages

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Read requirements
with open(os.path.join(this_directory, 'requirements.txt'), encoding='utf-8') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="cloudflare-bypasser",
    version="1.0.0",
    author="CloudflareBypass Team",
    author_email="dev@cloudflarebypass.com",
    description="Professional Python library for bypassing Cloudflare protection without external services",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cloudflarebypass/cloudflare-bypass",
    project_urls={
        "Bug Reports": "https://github.com/cloudflarebypass/cloudflare-bypass/issues",
        "Source": "https://github.com/cloudflarebypass/cloudflare-bypass",
        "Documentation": "https://cloudflarebypass.readthedocs.io/",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP :: Browsers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Networking",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "advanced": [
            "numpy>=1.21.0",
            "pillow>=8.0.0",
        ],
        "ml": [
            "tensorflow>=2.8.0",
            "torch>=1.10.0",
        ],
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.900",
            "pre-commit>=2.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "cloudflare-bypasser=cloudflare_bypass.cli:main",
        ],
    },
    keywords=[
        "cloudflare", "bypass", "captcha", "selenium", "automation", 
        "web-scraping", "bot-detection", "turnstile", "challenge"
    ],
    include_package_data=True,
    zip_safe=False,
)
