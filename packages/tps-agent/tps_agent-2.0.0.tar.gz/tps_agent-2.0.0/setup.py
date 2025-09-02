"""Setup script for TPS Agent library."""

from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="tps-agent",
    version="2.0.0",
    author="Earlypay",
    author_email="dev@earlypay.co.kr",
    description="Lightweight TPS monitoring agent for distributed systems",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Earlypay/tps-manager",
    packages=find_packages(include=['tps_agent', 'tps_agent.*']),
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
        "Topic :: System :: Monitoring",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0,<3.0.0",
        "prometheus_client>=0.16.0,<1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "isort>=5.0",
            "flake8>=3.8",
        ],
    },
    entry_points={
        "console_scripts": [
            "tps-agent-test=tps_agent.cli:main",
        ],
    },
)
