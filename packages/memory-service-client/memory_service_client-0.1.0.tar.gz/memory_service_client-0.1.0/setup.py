"""
Setup configuration for memory-service-client package.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="memory-service-client",
    version="0.1.0",
    author="Memory Service Team",
    author_email="team@example.com",
    description="Python client library for Memory Service gRPC API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/example/memory-service",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
    ],
    python_requires=">=3.9",
    install_requires=[
        "grpcio>=1.59.0",
        "protobuf>=4.24.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-grpc>=0.8.0",
            "black>=23.9.0",
            "ruff>=0.1.0",
            "mypy>=1.6.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "memory-client=memory_service_client.cli:main",
        ],
    },
)
