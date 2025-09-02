.. vim: set fileencoding=utf-8:
.. -*- coding: utf-8 -*-
.. +--------------------------------------------------------------------------+
   |                                                                          |
   | Licensed under the Apache License, Version 2.0 (the "License");          |
   | you may not use this file except in compliance with the License.         |
   | You may obtain a copy of the License at                                  |
   |                                                                          |
   |     http://www.apache.org/licenses/LICENSE-2.0                           |
   |                                                                          |
   | Unless required by applicable law or agreed to in writing, software      |
   | distributed under the License is distributed on an "AS IS" BASIS,        |
   | WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. |
   | See the License for the specific language governing permissions and      |
   | limitations under the License.                                           |
   |                                                                          |
   +--------------------------------------------------------------------------+

*******************************************************************************
                               librovore
*******************************************************************************

.. image:: https://img.shields.io/pypi/v/librovore
   :alt: Package Version
   :target: https://pypi.org/project/librovore/

.. image:: https://img.shields.io/pypi/status/librovore
   :alt: PyPI - Status
   :target: https://pypi.org/project/librovore/

.. image:: https://github.com/emcd/python-librovore/actions/workflows/tester.yaml/badge.svg?branch=master&event=push
   :alt: Tests Status
   :target: https://github.com/emcd/python-librovore/actions/workflows/tester.yaml

.. image:: https://emcd.github.io/python-librovore/coverage.svg
   :alt: Code Coverage Percentage
   :target: https://github.com/emcd/python-librovore/actions/workflows/tester.yaml

.. image:: https://img.shields.io/github/license/emcd/python-librovore
   :alt: Project License
   :target: https://github.com/emcd/python-librovore/blob/master/LICENSE.txt

.. image:: https://img.shields.io/pypi/pyversions/librovore
   :alt: Python Versions
   :target: https://pypi.org/project/librovore/


🐲📚 **Documentation Search Engine** - An intelligent documentation search and
extraction tool that provides both a command-line interface for humans and an
MCP (Model Context Protocol) server for AI agents. Search across Sphinx and
MkDocs sites with fuzzy matching, extract clean markdown content, and integrate
seamlessly with AI development workflows.


Key Features ⭐
===============================================================================

* 🔍 **Universal Search**: Fuzzy, exact, and regex search across documentation inventories and full content
* 🤖 **AI Agent Ready**: Built-in MCP server for seamless integration with Claude Code and other AI tools
* 📖 **Multi-Format Support**: Works with Sphinx (Furo, ReadTheDocs themes) and MkDocs (Material theme) sites
* 🚀 **High Performance**: In-memory caching with sub-second response times for repeated queries
* 🧹 **Clean Output**: High-quality HTML-to-Markdown conversion preserving code blocks and formatting
* 🎯 **Auto-Detection**: Automatically identifies documentation type without manual configuration
* 🔌 **Extensible**: Plugin architecture supports additional documentation formats via extension manager


Installation 📦
===============================================================================

Method: MCP Server Configuration
-------------------------------------------------------------------------------

Add as an MCP server in your AI client configuration. For example, in Claude
Code's MCP configuration:

::

    {
      "mcpServers": {
        "librovore": {
          "command": "uvx",
          "args": [
            "librovore",
            "serve"
          ]
        }
      }
    }

Method: Download Standalone Executable
-------------------------------------------------------------------------------

Download the latest standalone executable for your platform from `GitHub
Releases <https://github.com/emcd/python-librovore/releases>`_. These
executables have no dependencies and work out of the box.

Method: Install Executable Script
-------------------------------------------------------------------------------

Install via the `uv <https://github.com/astral-sh/uv/blob/main/README.md>`_
``tool`` command:

::

    uv tool install librovore

or, run directly with `uvx
<https://github.com/astral-sh/uv/blob/main/README.md>`_:

::

    uvx librovore

Or, install via `pipx <https://pipx.pypa.io/stable/installation/>`_:

::

    pipx install librovore

Method: Install Python Package
-------------------------------------------------------------------------------

Install via `uv <https://github.com/astral-sh/uv/blob/main/README.md>`_ ``pip``
command:

::

    uv pip install librovore

Or, install via ``pip``:

::

    pip install librovore


Examples 💡
===============================================================================

Command-Line Interface
-------------------------------------------------------------------------------

Search Python documentation for 'pathlib':

::

    librovore query-inventory https://docs.python.org/3 pathlib

Search content with fuzzy matching:

::

    librovore query-content https://fastapi.tiangolo.com "dependency injection"

MCP Server for AI Agents
-------------------------------------------------------------------------------

Start the MCP server for AI agent integration:

::

    librovore serve

The server provides tools for AI agents to search documentation object
inventories, search full documentation content with snippets, and get overviews
of available documentation.

Use Cases
===============================================================================

* **AI Development**: Enable Claude Code and other AI agents to search technical documentation
* **Documentation Research**: Quickly find API references and usage examples across multiple sites
* **Development Workflows**: Access documentation programmatically during development
* **Cross-Reference Search**: Find related concepts across different documentation sources


About the Name 📝
===============================================================================

The name "librovore" draws from Latin roots meaning **"book-devourer"** - a
fitting metaphor for a tool that consumes and digests documentation across
multiple formats:

* 📚 Anglicized Latin `libro- <https://en.wiktionary.org/wiki/libro->`_ ("book") + `-vore <https://en.wiktionary.org/wiki/-vore>`_ ("devouring")
* 🐲 The "Book Wyrm" - traditionally "librovore" is a synonym for "bookworm", but Claude's choice of the dragon emoji 🐲 rather than a worm emoji transformed our humble bookworm into a legendary wyrm that devours knowledge and makes it accessible
* 📖 Both "worm" and "wyrm" share the same Old English origins, so the linguistic evolution fits perfectly


Contribution 🤝
===============================================================================

Contribution to this project is welcome! However, it must follow the `code of
conduct
<https://emcd.github.io/python-project-common/stable/sphinx-html/common/conduct.html>`_
for the project.

Please file bug reports and feature requests in the `issue tracker
<https://github.com/emcd/python-librovore/issues>`_ or submit `pull
requests <https://github.com/emcd/python-librovore/pulls>`_ to
improve the source code or documentation.

For development guidance and standards, please see the `development guide
<https://emcd.github.io/python-librovore/stable/sphinx-html/contribution.html#development>`_.


Additional Indicia
===============================================================================

.. image:: https://img.shields.io/github/last-commit/emcd/python-librovore
   :alt: GitHub last commit
   :target: https://github.com/emcd/python-librovore

.. image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/copier-org/copier/master/img/badge/badge-grayscale-inverted-border-orange.json
   :alt: Copier
   :target: https://github.com/copier-org/copier

.. image:: https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg
   :alt: Hatch
   :target: https://github.com/pypa/hatch

.. image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit
   :alt: pre-commit
   :target: https://github.com/pre-commit/pre-commit

.. image:: https://microsoft.github.io/pyright/img/pyright_badge.svg
   :alt: Pyright
   :target: https://microsoft.github.io/pyright

.. image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
   :alt: Ruff
   :target: https://github.com/astral-sh/ruff

.. image:: https://img.shields.io/pypi/implementation/librovore
   :alt: PyPI - Implementation
   :target: https://pypi.org/project/librovore/

.. image:: https://img.shields.io/pypi/wheel/librovore
   :alt: PyPI - Wheel
   :target: https://pypi.org/project/librovore/


Other Projects by This Author 🌟
===============================================================================


* `python-absence <https://github.com/emcd/python-absence>`_ (`absence <https://pypi.org/project/absence/>`_ on PyPI)

  🕳️ A Python library package which provides a **sentinel for absent values** - a falsey, immutable singleton that represents the absence of a value in contexts where ``None`` or ``False`` may be valid values.
* `python-accretive <https://github.com/emcd/python-accretive>`_ (`accretive <https://pypi.org/project/accretive/>`_ on PyPI)

  🌌 A Python library package which provides **accretive data structures** - collections which can grow but never shrink.
* `python-classcore <https://github.com/emcd/python-classcore>`_ (`classcore <https://pypi.org/project/classcore/>`_ on PyPI)

  🏭 A Python library package which provides **foundational class factories and decorators** for providing classes with attributes immutability and concealment and other custom behaviors.
* `python-dynadoc <https://github.com/emcd/python-dynadoc>`_ (`dynadoc <https://pypi.org/project/dynadoc/>`_ on PyPI)

  📝 A Python library package which bridges the gap between **rich annotations** and **automatic documentation generation** with configurable renderers and support for reusable fragments.
* `python-falsifier <https://github.com/emcd/python-falsifier>`_ (`falsifier <https://pypi.org/project/falsifier/>`_ on PyPI)

  🎭 A very simple Python library package which provides a **base class for falsey objects** - objects that evaluate to ``False`` in boolean contexts.
* `python-frigid <https://github.com/emcd/python-frigid>`_ (`frigid <https://pypi.org/project/frigid/>`_ on PyPI)

  🔒 A Python library package which provides **immutable data structures** - collections which cannot be modified after creation.
* `python-icecream-truck <https://github.com/emcd/python-icecream-truck>`_ (`icecream-truck <https://pypi.org/project/icecream-truck/>`_ on PyPI)

  🍦 **Flavorful Debugging** - A Python library which enhances the powerful and well-known ``icecream`` package with flavored traces, configuration hierarchies, customized outputs, ready-made recipes, and more.
* `python-mimeogram <https://github.com/emcd/python-mimeogram>`_ (`mimeogram <https://pypi.org/project/mimeogram/>`_ on PyPI)

  📨 A command-line tool for **exchanging collections of files with Large Language Models** - bundle multiple files into a single clipboard-ready document while preserving directory structure and metadata... good for code reviews, project sharing, and LLM interactions.
