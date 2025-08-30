# Trainerbase Injector (forked Pyinjector)

Forked from [kmaork's Pyinjector](https://github.com/kmaork/pyinjector) in order to support Python 3.13.

[![PyPI Supported Python Versions](https://img.shields.io/pypi/pyversions/trainerbase-injector.svg)](https://pypi.python.org/pypi/trainerbase-injector/)
[![PyPI version](https://badge.fury.io/py/trainerbase-injector.svg)](https://badge.fury.io/py/trainerbase-injector)
[![Downloads](https://pepy.tech/badge/trainerbase-injector)](https://pepy.tech/project/trainerbase-injector)

A cross-platform tool/library allowing dynamic library injection into running processes.
If you are looking for a way to inject *python* code into a running process, try the [hypno](https://github.com/kmaork/hypno) library.

Trainerbase Injector has no external python dependencies.
It is implemented as a python wrapper for [kubo/injector](https://github.com/kubo/injector).

## Installation

```shell script
uv add trainerbase-injector
```

## Usage

### CLI

```shell script
uv run inject <pid> <path/to/shared/library>
```

### API

```python
from trainerbase_injector import inject

inject(pid, path_to_so_file)
```

## How it works

We build [kubo/injector](https://github.com/kubo/injector) as a C-extension and use its interface using `ctypes`.
[kubo/injector](https://github.com/kubo/injector) is an awesome repo allowing to inject shared libraries into running
processes both on Windows (`CreateRemoteThread`), Linux (`ptrace`), and Mac (`task_for_pid`).
