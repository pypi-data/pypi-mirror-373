from setuptools import setup, find_packages
from pathlib import Path

# Read the README for long description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="aider-jac-osp",
    version="2.0.0",
    description="Aider: AI-powered coding assistant rebuilt with Jac Object-Spatial Programming and Genius Mode",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Thiruvarankan M",
    author_email="thiru07official@gmail.com",
    url="https://github.com/ThiruvarankanM/Rebuilding-Aider-with-Jac-OSP",
    packages=find_packages(exclude=["tests*", "examples*", "docs*", "scripts*"]),
    python_requires=">=3.8",
    install_requires=[
        # Core dependencies
        "rich>=13.5.0",
        "prompt-toolkit>=3.0.0",
        "configargparse>=1.7.0",
        "pyperclip>=1.8.0",
        "pillow>=9.0.0",
        
        # AI/LLM dependencies
        "litellm>=1.0.0",
        "openai>=1.0.0",
        "anthropic>=0.7.0",
        "tiktoken>=0.7.0",
        
        # Code analysis
        "tree-sitter>=0.20.0",
        "gitpython>=3.1.0",
        
        # Async operations
        "aiofiles>=23.0.0",
        
        # Data handling
        "pydantic>=2.0.0",
        "json5>=0.9.0",
        "pyyaml>=6.0.0",
        
        # CLI tools
        "shtab>=1.6.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "jac": [
            "jaclang>=0.7.0",  # Jac language support
        ],
        "dev": [
            "black>=24.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "pytest>=7.0.0",
            "pytest-mock>=3.10.0",
        ],
        "demo": [
            "rich>=13.5.0",  # For competition demo visuals
        ],
    },
    entry_points={
        "console_scripts": [
            "aider=aider.__main__:main",
            "aider-genius=aider.cli:main",  # Complete CLI interface
        ],
    },
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9", 
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Text Processing :: Linguistic",
    ],
    keywords="AI assistant LLM code OSP MTP Jac automation spatial-programming genius-mode",
)
