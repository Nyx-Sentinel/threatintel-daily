from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="threatintel-daily",
    version="0.1.0",
    author="Alphonse",
    author_email="nyxsentinel.se@gmail.com",
    description="Personal threat intelligence aggregator for security-conscious individuals",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Nyx-Sentinel/threatintel-daily",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Topic :: Security",
        "Topic :: System :: Monitoring",
    ],
    python_requires=">=3.9",
    install_requires=[
        "requests>=2.31.0",
        "pyyaml>=6.0",
        "apscheduler>=3.10.4",
        "click>=8.1.7",
        "fastapi>=0.104.1",
        "uvicorn>=0.24.0",
        "sqlalchemy>=2.0.23",
        "pydantic>=2.5.0",
        "python-dotenv>=1.0.0",
        "aiohttp>=3.9.1",
        "validators>=0.22.0",
    ],
    entry_points={
        "console_scripts": [
            "threatintel-daily=threatintel_daily.cli:cli",
        ],
    },
)
