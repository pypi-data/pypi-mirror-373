from setuptools import setup
from ollama_rich import __version__

setup(
    name="ollama-rich",
    version=__version__,
    description="A feature-rich Ollama client with enhanced terminal UI using the Rich library.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Jak BIn",
    packages=["ollama_rich"],
    install_requires=[
        "rich",
        "ollama",
        "pyyaml",
    ],
    python_requires=">=3.7",
    entry_points={
        'console_scripts': [
            'ollama-rich=ollama_rich.cli:main',
            'or=ollama_rich.cli:main',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    license="MIT",
    url="https://github.com/jakbin/ollama-rich",
    project_urls={
        "Source": "https://github.com/jakbin/ollama-rich",
        "Tracker": "https://github.com/jakbin/ollama-rich/issues",
    },
)
