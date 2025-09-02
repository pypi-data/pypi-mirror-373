from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="clutch-scraper",
    version="1.2.3",
    author="Dhawal Bisht",
    author_email="dhawalbisht4543@gmail.com",
    description="A CLI tool to scrape company reviews from Clutch.co",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dhawalbisht/clutch-scraper",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "clutch-scraper=clutch_scraper.main:main",
        ],
    },
    scripts=["scripts/clutch-scraper"],
    include_package_data=True,
)