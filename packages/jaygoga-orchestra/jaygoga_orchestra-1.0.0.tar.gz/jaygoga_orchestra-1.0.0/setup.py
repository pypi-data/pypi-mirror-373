from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="jaygoga-orchestra",
    version="1.0.0",
    author="AIMLDev726",
    author_email="aistudentlearn4@gmail.com",
    description="JayGoga-Orchestra - Advanced AI Agent Orchestration Framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AIMLDev726/jaygoga_orchestra",
    packages=find_packages(),
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
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pydantic>=2.0.0",
        "typing-extensions>=4.0.0",
        "requests>=2.25.0",
        "python-dotenv>=0.19.0",
        "openai>=1.0.0",
        "anthropic>=0.3.0",
        "langchain>=0.1.0",
        "langchain-community>=0.0.1",
        "langchain-openai>=0.0.1",
        "chromadb>=0.4.0",
        "tiktoken>=0.5.0",
        "tenacity>=8.0.0",
        "click>=8.0.0",
        "rich>=13.0.0",
        "PyYAML>=6.0.0",
        "jsonschema>=4.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "all": [
            "faiss-cpu>=1.7.0",
            "pinecone-client>=2.2.0",
            "weaviate-client>=3.15.0",
            "qdrant-client>=1.6.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "jaygoga-orchestra=jaygoga_orchestra.v1.cli.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "jaygoga_orchestra": ["**/*.yaml", "**/*.yml", "**/*.json", "**/*.txt"],
    },
)
