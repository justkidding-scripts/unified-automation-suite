#!/usr/bin/env python3
"""
Setup script for Advanced API Rate Optimization Suite
Professional Edition
"""

from setuptools import setup, find_packages
import os

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="api-optimization-suite",
    version="1.0.0",
    author="Professional Software Solutions",
    author_email="enterprise@apisuite.com",
    description="Enterprise-Grade API Traffic Management and Load Testing Platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://www.api-optimization-suite.com",
    packages=find_packages(),
    py_modules=["api_optimization_suite"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Information Technology",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Testing :: Traffic Generation",
        "Topic :: System :: Networking",
        "Topic :: System :: Systems Administration",
        "Topic :: Internet :: WWW/HTTP",
        "License :: Other/Proprietary License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: X11 Applications :: Qt",
        "Environment :: Win32 (MS Windows)",
        "Environment :: MacOS X"
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-asyncio>=0.21.0",
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.991"
        ],
        "enterprise": [
            "cryptography>=3.4.8",
            "pycryptodome>=3.15.0",
            "psutil>=5.8.0",
            "prometheus-client>=0.14.0"
        ]
    },
    entry_points={
        "console_scripts": [
            "api-optimizer=api_optimization_suite:main",
            "api-suite=api_optimization_suite:main",
        ],
        "gui_scripts": [
            "api-optimizer-gui=api_optimization_suite:main",
        ]
    },
    include_package_data=True,
    zip_safe=False,
    keywords=[
        "api", "optimization", "load-testing", "performance", "rate-limiting",
        "traffic-management", "enterprise", "professional", "testing", "automation"
    ],
    project_urls={
        "Bug Reports": "https://github.com/professional-software/api-suite/issues",
        "Source": "https://github.com/professional-software/api-suite",
        "Documentation": "https://docs.api-optimization-suite.com",
        "Commercial License": "https://www.api-optimization-suite.com/license",
        "Enterprise Support": "https://www.api-optimization-suite.com/support"
    }
)