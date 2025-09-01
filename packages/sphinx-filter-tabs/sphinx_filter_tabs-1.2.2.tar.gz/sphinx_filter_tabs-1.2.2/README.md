# Sphinx Filter Tabs Extension

[![Tests and Docs Deployment](https://github.com/aputtu/sphinx-filter-tabs/actions/workflows/test.yml/badge.svg)](https://github.com/aputtu/sphinx-filter-tabs/actions/workflows/test.yml)
[![PyPI version](https://img.shields.io/pypi/v/sphinx-filter-tabs.svg)](https://pypi.org/project/sphinx-filter-tabs/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/sphinx-filter-tabs.svg)](https://pypi.org/project/sphinx-filter-tabs/)
[![PyPI - License](https://img.shields.io/pypi/l/sphinx-filter-tabs.svg)](https://github.com/aputtu/sphinx-filter-tabs/blob/main/LICENSE)

A robust Sphinx extension for creating accessible, JavaScript-free, filterable content tabs.

**📖 View extension and documentation at: https://aputtu.github.io/sphinx-filter-tabs/**

This extension provides `filter-tabs` and `tab` directives to create user-friendly, switchable content blocks, ideal for showing code examples in multiple languages or instructions for different platforms.

## Features

- **No JavaScript:** Pure CSS implementation ensures maximum compatibility, speed, and accessibility.
- **WAI-ARIA Compliant:** The generated HTML follows accessibility best practices for keyboard navigation and screen readers.
- **Highly Customizable:** Easily theme colors, fonts, and sizes directly from your `conf.py` using CSS Custom Properties.
- **Graceful Fallback:** Renders content as simple admonitions in non-HTML outputs like PDF/LaTeX.
- **Automated Testing:** CI/CD pipeline tests against multiple Sphinx versions to ensure compatibility.

## Installation

You can install this extension using `pip`:
```bash
pip install sphinx-filter-tabs
```

## Development

1. You can install a local version of the Sphinx with extension using:
```bash
./scripts/setup_dev.sh # Initially cleans previous folders in _docs/build  and venv.
```

Command to enter venv is provided.

2. Once inside virtual environment, you can use following commands:
```bash
pytest # Runs test suite on configured version of Sphinx.
tox # Check across multiple Sphinx versions. Manual install of tox required.
./scripts/export-project.sh # Outputs directory structure and code to txt
./dev.sh [options] # Allows for faster generation for html, pdf, clean up
```
