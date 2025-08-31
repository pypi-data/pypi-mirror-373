# SPDX-FileCopyrightText: 2021-2025 EasyDiffraction Python Library contributors <https://github.com/easyscience/diffraction-lib>
# SPDX-License-Identifier: BSD-3-Clause

import sys

# Ensure UTF-8 output on all platforms (e.g. Windows with cp1252)
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

import typer

import easydiffraction as ed

app = typer.Typer(add_completion=False)


@app.command('version')
def version():
    """Show easydiffraction version."""
    ed.show_version()


@app.command('list-tutorials')
def list_tutorials():
    """List available tutorial notebooks."""
    ed.list_tutorials()


@app.command('fetch-tutorials')
def fetch_tutorials():
    """Download and extract tutorial notebooks."""
    ed.fetch_tutorials()


if __name__ == '__main__':
    app()
