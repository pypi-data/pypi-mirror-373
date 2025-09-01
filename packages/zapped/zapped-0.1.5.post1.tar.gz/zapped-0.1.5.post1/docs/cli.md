# CLI Reference

The `zapper` command provides several utilities for working with your project.

## Available Commands

### `version`
Display the current version of Zapper.

```bash
zapper version
```

### `debug_info`
Show detailed environment and system information.

```bash
zapper debug_info
```

Options:
- `--no-color, -n`: Disable colored output

### `bump`
Bump the project version and create a git tag.

```bash
zapper bump <version_type>
```

Arguments:
- `version_type`: One of `patch`, `minor`, or `major`

Examples:
```bash
# Bump patch version (1.0.0 -> 1.0.1)
zapper bump patch

# Bump minor version (1.0.1 -> 1.1.0)  
zapper bump minor

# Bump major version (1.1.0 -> 2.0.0)
zapper bump major
```

### `interactive`
Start interactive mode for enhanced CLI experience.

```bash
zapper interactive
```


## Global Options

- `--version, -V`: Show version information and exit
- `--help`: Show help message and exit

