# Zapper

A string manipulation tool for crazed maniacs including built in typed tuple returns.

## Installation

```bash
pip install zapper
```

## Quick Start

After installation, you can use the CLI:

```bash
zapper --help
```

### Available Commands

```bash
# Get version information
zapper version

# Show debug information
zapper debug_info

# Version management
zapper bump patch|minor|major

# Interactive mode
zapper interactive

```


## Development

Clone the repository and install dependencies:

```bash
git clone <your-repo-url>
cd zapper
uv sync
```

Run tests:

```bash
nox -s tests
```

## License

This project is licensed under the  License.