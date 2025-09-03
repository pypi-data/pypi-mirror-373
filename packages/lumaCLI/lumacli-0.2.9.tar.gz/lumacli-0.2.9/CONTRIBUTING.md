# How to contribute to `luma`

## Setting up the development environment

### Prerequisites

#### uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Installing dependencies

```bash
uv sync
```

To execute PostgreSQL tests:

```bash
sudo apt install libpq-dev
```

### Running the docs locally

```bash
uv run mkdocs serve
```

## Generating API reference docs

```console
cd src/luma
typer luma.py utils docs --output ../../docs/api_reference.md
```
