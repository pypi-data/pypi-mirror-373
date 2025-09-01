# LangChain CLI

A command-line interface for developing and deploying LangChain tool servers.

## Installation

```bash
pip install -e .
```

## Quick Start

```bash
# Create a new toolkit
langchain tools new my-toolkit
cd my-toolkit

# Start local development server
langchain tools serve --reload

# Deploy to production
langchain tools deploy --server https://tools.company.com
```

## Commands

### `langchain tools new <name>`
Create a new toolkit project with standard structure.

### `langchain tools serve`
Start a local development server with auto-reload. No database persistence.

### `langchain tools deploy`
Deploy current toolkit to a remote tool server with version management.

## Development

Install in development mode:
```bash
pip install -e .
```