"""Setup configuration for bedrock-region-balancer package."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="bedrock-region-balancer",
    version="0.4.0",
    author="SungHyon Kim",
    author_email="spero84@gmail.com",
    description="AWS Bedrock region load balancer with round-robin distribution and batch processing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    # url="https://github.com/spero84/bedrock-region-balancer",  # PyPI에서는 선택사항
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "boto3>=1.33.0",
        "botocore>=1.33.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "boto3-stubs[bedrock,bedrock-runtime,secretsmanager]>=1.28.0",
        ]
    },
    project_urls={
        "Bug Reports": "https://github.com/spero84/bedrock-region-balancer/issues",
        "Source": "https://github.com/spero84/bedrock-region-balancer",
    },
)
