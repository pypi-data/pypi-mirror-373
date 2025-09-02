# Whitebox Plugin - Stratux

This is a plugin for [whitebox](https://gitlab.com/whitebox-aero) that adds stratux support to whitebox giving access to GPS, ADS-B, and Hardware Status data.

## Installation

1. Ensure you have [poetry](https://python-poetry.org/docs/) installed on your system.
2. Ensure whitebox is not running. Run `docker compose down` in the whitebox directory if running.
3. Change to the backend directory of whitebox.
4. Install the plugin: `poetry add whitebox-plugin-stratux`
5. Change back to the root directory of whitebox.
6. Start whitebox: `docker compose up -d`

## Environment Variables

`STRATUX_URL`: Defaults to `ws://stratux:80`. You can override this before starting whitebox to connect to a different stratux device.
`SKIP_HARDWARE_TESTS`: Defaults to `False`. Set to `True` to skip hardware tests.

## Additional Instructions

- [Development Environment Setup](https://docs.whitebox.aero/development_guide/#setting-up-development-environment)
- [Plugin Development Guide](https://docs.whitebox.aero/plugin_guide/#plugin-development-workflow)
- [Plugin Testing Guide](https://docs.whitebox.aero/plugin_guide/#testing-plugins)
- [Contributing Guidelines](https://docs.whitebox.aero/development_guide/#contributing)
