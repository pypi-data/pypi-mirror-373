from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="yugenkairo-sentinel-sdk",
    version="1.0.0",
    author="Sentinel Team",
    author_email="sentinel-team@yugenkairo.com",
    description="Python SDK for Sentinel - Enterprise LLM Security Gateway with AI-powered threat detection and cryptographic data protection",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/swayam8624/Sentinel",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Security",
        "Topic :: Security :: Cryptography",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.31.0",
        "pydantic>=2.0.0",
        "cryptography>=41.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
        ],
        "enterprise": [
            "redis>=4.6.0",
            "prometheus-client>=0.17.0",
        ],
    },
    keywords=["sentinel", "llm", "security", "firewall", "cryptography", "pii", "data-protection", "ai-security", "prompt-injection", "rate-limiting", "enterprise", "compliance"],
    project_urls={
        "Documentation": "https://swayam8624.github.io/Sentinel/",
        "Source": "https://github.com/swayam8624/Sentinel",
        "Tracker": "https://github.com/swayam8624/Sentinel/issues",
    },
)