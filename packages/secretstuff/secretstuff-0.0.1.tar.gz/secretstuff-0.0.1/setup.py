"""Setup configuration for SecretStuff package."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="secretstuff",
    version="0.0.1",
    author="axondendrite",
    author_email="amandogra2016@gmail.com",
    description="A comprehensive PII redaction and reverse mapping library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/adw777/secretStuff",
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
        "Topic :: Security",
        "Topic :: Text Processing",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
        ],
    },
    include_package_data=True,
    keywords="pii, redaction, privacy, nlp, gliner, data-protection, anonymization, secretstuff",
    project_urls={
        "Bug Reports": "https://github.com/adw777/secretStuff/issues",
        "Source": "https://github.com/adw777/secretStuff",
        "Documentation": "https://github.com/adw777/secretStuff/blob/main/README.md"
    },
)
