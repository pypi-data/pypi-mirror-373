# mnimi

> Keeps every byte in sight — uncovers the memory of your MCU.

**mnimi** is a Python tool that parses ELF files and connects to your
embedded target (e.g. via J-Link). It lets you spy on functions,
global variables, and memory — directly from the command line.

## Features

Currently under development

- [ ] Parse ELF symbols (functions, global variables, addresses, sizes).
- [ ] Connect to STM32/embedded targets using J-Link.
- [ ] Read variables directly from the running device.
- [ ] TUI/CLI interface for inspecting memory maps.
- [ ] Export symbol/function metadata.
- [ ] Fuzzy search
- [ ] Support multiple providers (OpenOCD, gdb/ptrace, jlink, stlink, etc)

## Getting Started

To get a local copy up and running follow these simple steps.

### Installation

Run the following command:

```sh
pip install mnimi
```

## Contact

Kanelis Elias - [@email](mailto:e.kanelis@voidbuffer.com)
