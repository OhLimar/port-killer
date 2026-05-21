# port-killer

Kill the process listening on a given port.

## Installation

```
pip install pkiller
```

Or run directly:

```
python port_killer.py <port>
```

## Usage

```
port-killer <port> [options]
```

| Option | Short | Description |
|--------|-------|-------------|
| `--force` | `-f` | Skip confirmation, use SIGKILL directly |
| `--info` | `-i` | Show process info without killing |

## Examples

```
port-killer 3000
port-killer 8080 --force
port-killer 5432 --info
```

## Requirements

- Python 3.8+
- psutil

## License

MIT
