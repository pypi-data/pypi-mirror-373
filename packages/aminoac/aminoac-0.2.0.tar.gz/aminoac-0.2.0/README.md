# aminoac

A Python package that modifies CTRL-C behavior to play audio before exiting.

## Installation

```bash
pip install aminoac
```

## Usage

Simply import the package and the CTRL-C behavior is automatically modified:

```python
import aminoac

# Now when you press CTRL-C, it will play amns.mp3 before exiting
```

## What it does

- Automatically sets up a signal handler for SIGINT (CTRL-C)
- When CTRL-C is pressed, plays the `amns.mp3` audio file
- Then exits normally with the default signal handler
