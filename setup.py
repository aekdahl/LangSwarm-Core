from setuptools import setup, find_packages

setup(
    name="langswarm-core",
    version="0.0.2",
    description="A core framework for multi-agent LLM ecosystems",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/aekdahl/langswarm-core",
    author="Alexander Ekdahl",
    author_email="alexander.ekdahl@gmail.com",
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "langchain",
        "tiktoken",
        "llama-index",
        "pyyaml",
        # Add other dependencies here
    ],
    extras_require={
        "dev": ["pytest", "black", "flake8"],
    },
    include_package_data=True,
    entry_points={
        "console_scripts": [
            # If your package includes CLI tools, specify them here.
            # e.g., "langswarm=core.cli:main",
        ],
    },
)
