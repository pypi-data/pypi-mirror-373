# Abstract IDE

[![PyPI version](https://badge.fury.io/py/abstract-ide.svg)](https://badge.fury.io/py/abstract-ide)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/downloads/)

**Abstract IDE** is a modular, extensible Python-based Integrated Development Environment (IDE) toolset designed for developers working with web projects, particularly React/TypeScript applications. It provides a graphical user interface (GUI) built with PyQt for code analysis, import graphing, content searching, build automation, and more. The tool leverages background workers for non-blocking operations and integrates with external utilities for tasks like code searching, API testing, and file management.

This project is part of a larger ecosystem of "abstract" modules (e.g., `abstract_paths`, `abstract_apis`) and is ideal for analyzing large codebases, debugging builds, and automating repetitive development tasks.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Dependencies](#dependencies)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)

## Features

Abstract IDE offers a tabbed GUI interface with the following core functionalities:

- **Runner Tab**: Execute TypeScript compilation (`tsc`) and React builds (`yarn build`) locally or via SSH. Displays errors and warnings with clickable links to open files in VS Code. Supports ANSI stripping, severity filtering, and alternate file extension resolution (e.g., `.ts` ↔ `.tsx`).

- **Functions Map Tab**: Scans the project for import/export graphs, displaying functions as interactive buttons. Filter by name, view exporters/importers, and open files directly. Supports "all" or "reachable" scopes with customizable entry points (e.g., `index.tsx`, `main.tsx`).

![Functions Map Tab](docs/images/functions_map.png)

- **Find Content Tab**: Advanced code search across directories. Supports recursive searches, string matching (partial or exact), file extensions, path filters, and line-specific queries. Results are clickable for editing in VS Code.

![Find Content Tab](docs/images/find_content.png)

- **API Client Tab**: A console for testing APIs with dynamic endpoints, headers, and parameters. Fetches remote endpoints from `/api/endpoints` and supports GET/POST methods.

![API Client Tab](docs/images/api_client.png)

- **ClipIt Tab**: Drag-and-drop file browser with clipboard integration for quick file operations.

![ClipIt Tab](docs/images/clipit.png)

- **Window Manager Tab**: Manages multiple windows and layouts within the IDE.

- **Directory Map Tab**: Generates a visual tree map of the project directory, with filters for extensions, types, and patterns.

![Directory Map Tab](docs/images/directory_map.png)

- **Collect Files Tab**: Collects and lists files based on criteria like extensions and paths, with options to open all in VS Code.

![Collect Files Tab](docs/images/collect_files.png)

- **Extract Python Imports Tab**: Scans Python files for imports and module paths, displaying them in a readable format.

![Extract Python Imports Tab](docs/images/extract_imports.png)

Additional tools (integrated via workers):
- Code execution in a REPL-like environment with pre-installed libraries (e.g., NumPy, SciPy, PyTorch).
- Web browsing, searching, and snippet extraction.
- X (Twitter) post searching (keyword, semantic, user, threads).
- Image/PDF viewing and searching.
- Render components for inline citations.

The IDE uses multi-threading (QThread) for background tasks to keep the UI responsive.

## Installation

### Prerequisites
- Python 3.8+
- Git (for cloning the repository)

### From PyPI
```bash
pip install abstract-ide
```

### From Source
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/abstract-ide.git
   cd abstract-ide
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   (Or use the list from `abstract_ide.egg-info/requires.txt`.)

3. Run the IDE:
   ```bash
   python -m abstract_ide
   ```

## Usage

Launch the application:
```bash
python -m abstract_ide
```

### Basic Workflow
1. **Set Project Path**: In the Runner tab, enter the project directory (e.g., `/path/to/react-app`).
2. **Run Build**: Click "Run" to compile and build. Errors/warnings appear in lists—click to view snippets or open in editor.
3. **Map Functions**: Switch to Functions Map tab, select scope ("all" or "reachable"), and scan. Filter functions and inspect imports/exports.
4. **Search Code**: In Find Content tab, specify directory, strings (comma-separated), extensions, and flags. Results are listed for quick navigation.
5. **Test APIs**: In API Client tab, select base URL, fetch endpoints, add headers/params, and send requests.
6. **Advanced**: Use workers for background tasks like web searches or PDF analysis via function calls (see [Tools](#tools)).

### Keyboard Shortcuts
- Double-click list items: Open in VS Code.
- Filter radios: Toggle error/warning views dynamically.

### Example: Analyzing a React Project
- Load `/var/www/html/clownworld/bolshevid` (as in the sample import graph).
- Scan functions: View exports like `getIps`, `fetchMedia`, and their importers/exporters.
- Search for "useState": Find all occurrences in `.tsx` files recursively.

## Configuration

- **Import Graph**: Generated via `create_import_maps()` and stored as `import-graph.json` and `graph.dot` in `/data/import_tools/`.
- **Custom Entries**: Override entry points (e.g., `index.tsx`) in the Functions Map tab.
- **Extensions**: Configurable via UI inputs (e.g., comma-separated lists).
- **SSH Builds**: Specify `user@host` for remote execution.

Customize via environment variables:
- `BASE_DIRECTORY`: Default project root (e.g., `/var/www/html/clownworld/bolshevid`).

## Dependencies

From `abstract_ide.egg-info/requires.txt`:
- abstract_apis
- PyQt5 (or PyQt6)
- abstract_webtools
- abstract_utilities
- abstract_gui
- pydot
- abstract_clipit
- flask
- abstract_paths

Install via `pip install -r requirements.txt`.

## Project Structure

```
abstract_ide/
├── src/
│   ├── abstract_ide/
│   │   ├── __init__.py
│   │   ├── imports/
│   │   │   ├── __init__.py
│   │   │   ├── imports.py
│   │   │   └── constants.py
│   │   ├── utils/
│   │   │   ├── __init__.py
│   │   │   ├── imports/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── imports/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   └── imports.py
│   │   │   │   └── utils/
│   │   │   │       ├── __init__.py
│   │   │   │       ├── file_utils.py
│   │   │   │       └── utils.py
│   │   │   ├── managers/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── imports/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── imports.py
│   │   │   │   │   └── widget_funcs.py
│   │   │   │   └── utils/
│   │   │   │       ├── __init__.py
│   │   │   │       ├── get_modules.py
│   │   │   │       ├── importGraphWorker.py
│   │   │   │       ├── imports.py
│   │   │   │       ├── worker.py
│   │   │   │       └── mainWindow/
│   │   │   │           ├── __init__.py
│   │   │   │           ├── imports.py
│   │   │   │           ├── mainWindow.py
│   │   │   │           └── functions/
│   │   │   │               ├── __init__.py
│   │   │   │               ├── imports.py
│   │   │   │               ├── clickHandlers/
│   │   │   │               │   ├── __init__.py
│   │   │   │               │   ├── clickHandlers.py
│   │   │   │               │   └── imports.py
│   │   │   │               └── init_tabs/
│   │   │   │                   ├── __init__.py
│   │   │   │                   ├── apigui.py
│   │   │   │                   ├── imports.py
│   │   │   │                   ├── finder/
│   │   │   │                   │   ├── __init__.py
│   │   │   │                   │   ├── clickfinder.py
│   │   │   │                   │   ├── finder.py
│   │   │   │                   │   ├── finder_back.py
│   │   │   │                   │   └── get_diffs.py
│   │   │   │                   ├── functions_page/
│   │   │   │                   │   ├── __init__.py
│   │   │   │                   │   └── functions_page.py
│   │   │   │                   ├── initialize_init/
│   │   │   │                   │   ├── __init__.py
│   │   │   │                   │   └── initialize_init.py
│   │   │   │                   └── runner/
│   │   │   │                       ├── __init__.py
│   │   │   │                       └── runner.py
│   │   │   └── widgets/
│   │   │       ├── __init__.py
│   │   │       ├── imports/
│   │   │       │   ├── __init__.py
│   │   │       │   └── imports.py
│   │   │       └── utils/
│   │   │           ├── __init__.py
│   │   │           ├── kwargs_utils.py
│   │   │           ├── utils.py
│   │   │           └── widgets.py
│   └── abstract_ide.egg-info/
│       ├── PKG-INFO
│       ├── SOURCES.txt
│       ├── dependency_links.txt
│       ├── requires.txt
│       └── top_level.txt
├── README.md
├── pyproject.toml
├── setup.cfg
└── setup.py
```

- **utils/managers**: Core GUI logic and workers.
- **utils/imports**: Import graphing and utilities.
- **utils/widgets**: Reusable Qt widget helpers.

To integrate the provided screenshots into this README:

1. **Save the Screenshots**: Download or capture the screenshots and save them in a dedicated folder, e.g., `docs/images/`. Name them descriptively:
   - `directory_map.png`
   - `find_content.png`
   - `clipit.png`
   - `extract_imports.png`
   - `api_client.png`
   - `functions_map.png`
   - `collect_files.png`

2. **Update the README**: Insert the Markdown image syntax under the relevant feature descriptions, as shown above (e.g., `![Directory Map Tab](docs/images/directory_map.png)`). Ensure the path is relative to the README file.

3. **Commit and Push**: Add the images to your Git repo and push the changes. This will make them visible on GitHub or other hosts.

If the screenshots need processing (e.g., cropping, annotations), use tools like ImageMagick or online editors before adding.

## Contributing

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/new-tool`.
3. Commit changes: `git commit -am 'Add new tool'`.
4. Push: `git push origin feature/new-tool`.
5. Submit a Pull Request.

Report issues via GitHub Issues.

## License

MIT License. See [LICENSE](LICENSE) for details.

## Acknowledgments

- Built with PyQt for cross-platform GUI.
- Integrates with `pydot` for graph visualization.
- Thanks to xAI for inspiration in tool integration.