from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="weavium",
    version="0.1.5",
    author="Weavium Team",
    author_email="support@weavium.com",
    description="Python client library for the Weavium prompt compression API with boto3 instrumentation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    # url="https://github.com/weavium/weavium-ai",
    project_urls={
        # "Homepage": "https://weavium.com",
        # "Documentation": "https://docs.weavium.com",
        # "Repository": "https://github.com/weavium/weavium-ai",
        # "Issues": "https://github.com/weavium/weavium-ai/issues",
        # "API Documentation": "https://api.weavium.com/docs",
    },
    packages=find_packages(exclude='tests'),
    classifiers=[
        "Development Status :: 3 - Alpha",
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
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    keywords="weavium api client compression llm prompt ai machine-learning",
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
    ],
    extras_require={
        "boto3": ["boto3>=1.26.0"],
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.9",
            "mypy>=0.900",
            "boto3>=1.26.0",
        ],
    },
    include_package_data=True,
    zip_safe=False,
) 