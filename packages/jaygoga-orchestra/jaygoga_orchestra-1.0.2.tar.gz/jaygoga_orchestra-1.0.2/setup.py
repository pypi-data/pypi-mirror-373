from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="jaygoga-orchestra",
    version="1.0.2",
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
        # Core Dependencies
        "pydantic>=2.4.2",
        "openai>=1.13.3",
        "litellm>=1.74.9",
        "instructor>=1.3.3",

        # Text Processing
        "pdfplumber>=0.11.4",
        "regex>=2024.9.11",

        # Telemetry and Monitoring
        "opentelemetry-api>=1.30.0",
        "opentelemetry-sdk>=1.30.0",
        "opentelemetry-exporter-otlp-proto-http>=1.30.0",

        # Data Handling
        "chromadb>=0.5.23",
        "tokenizers>=0.20.3",
        "onnxruntime>=1.22.0",
        "openpyxl>=3.1.5",
        "pyvis>=0.3.2",

        # Authentication and Security
        "python-dotenv>=1.0.0",
        "pyjwt>=2.9.0",

        # Configuration and Utils
        "click>=8.1.7",
        "appdirs>=1.4.4",
        "jsonref>=1.1.0",
        "json-repair>=0.25.2",
        "tomli-w>=1.1.0",
        "tomli>=2.0.2",
        "blinker>=1.9.0",
        "json5>=0.10.0",
        "portalocker>=2.7.0",

        # Rich Console Output
        "rich>=13.0.0",

        # Additional Core Dependencies
        "typing-extensions>=4.0.0",
        "requests>=2.25.0",
        "anthropic>=0.3.0",
        "langchain>=0.1.0",
        "langchain-community>=0.0.1",
        "langchain-openai>=0.0.1",
        "tiktoken>=0.5.0",
        "tenacity>=8.0.0",
        "PyYAML>=6.0.0",
        "jsonschema>=4.0.0",

        # Memory and Storage
        "sqlalchemy>=2.0.0",
        "aiofiles>=23.0.0",

        # Web and HTTP
        "httpx>=0.24.0",
        "aiohttp>=3.8.0",

        # Data Processing
        "pandas>=2.2.3",
        "numpy>=1.24.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "build>=0.10.0",
            "twine>=4.0.0",
        ],
        "vectordbs": [
            "faiss-cpu>=1.7.0",
            "pinecone-client>=2.2.0",
            "weaviate-client>=3.15.0",
            "qdrant-client>=1.6.0",
            "pgvector>=0.2.0",
            "lancedb>=0.20.0",
        ],
        "tools": [
            "arxiv>=1.4.0",
            "newspaper4k>=0.9.0",
            "youtube-transcript-api>=0.6.0",
            "googlemaps>=4.10.0",
            "matplotlib>=3.7.0",
            "opencv-python>=4.8.0",
            "selenium>=4.15.0",
            "beautifulsoup4>=4.12.0",
        ],
        "files": [
            "pypdf>=3.0.0",
            "python-docx>=0.8.11",
            "markdown>=3.4.0",
            "unstructured>=0.10.0",
        ],
        "memory": [
            "mem0ai>=0.1.94",
            "redis>=4.5.0",
        ],
        "all": [
            "faiss-cpu>=1.7.0",
            "pinecone-client>=2.2.0",
            "weaviate-client>=3.15.0",
            "qdrant-client>=1.6.0",
            "pgvector>=0.2.0",
            "arxiv>=1.4.0",
            "newspaper4k>=0.9.0",
            "matplotlib>=3.7.0",
            "pypdf>=3.0.0",
            "python-docx>=0.8.11",
            "mem0ai>=0.1.94",
            "redis>=4.5.0",
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
