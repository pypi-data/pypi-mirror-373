# ollama-rich

A feature-rich Ollama client with enhanced terminal UI using the Rich library.

[![PyPI version](https://badge.fury.io/py/ollama-rich.svg)](https://pypi.org/project/ollama-rich)
[![Downloads](https://pepy.tech/badge/ollama-rich/month)](https://pepy.tech/project/ollama-rich)
[![Downloads](https://static.pepy.tech/personalized-badge/ollama-rich?period=total&units=international_system&left_color=green&right_color=blue&left_text=Total%20Downloads)](https://pepy.tech/project/ollama-rich)
![GitHub commit activity](https://img.shields.io/github/commit-activity/m/jakbin/ollama-rich)
![GitHub last commit](https://img.shields.io/github/last-commit/jakbin/ollama-rich)

## Features
- List available Ollama models in a beautiful table
- Chat with models directly from the terminal
- Stream responses live with markdown rendering
- Easy-to-use CLI interface
- More comming soon

## Requirements
- Python 3.7+
- [Ollama](https://github.com/jmorganca/ollama) server running
- [rich](https://github.com/Textualize/rich) Python library

## Installation
```sh
pip install ollama-rich
```
Or

```bash
pip install .
```

## Usage
### List Models
```bash
ollama-rich models
```

### Chat with a Model
```bash
ollama-rich chat <model> "Your message here"
```

### Stream Chat Response
```bash
ollama-rich chat <model> "Your message here" --stream
```


