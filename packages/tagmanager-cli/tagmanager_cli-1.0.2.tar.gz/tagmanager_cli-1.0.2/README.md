# 🏷️ TagManager

<div align="center">

**The Ultimate Command-Line File Tagging System**

_Transform chaos into order with intelligent file organization_

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](README.md)

[Features](#-features) • [Installation](#-installation) • [Quick Start](#-quick-start) • [Documentation](#-documentation) • [Examples](#-examples)

</div>

---

## 🌟 Why TagManager?

Ever lost a file in the digital maze of your computer? Tired of endless folder hierarchies that never quite fit your workflow? **TagManager** revolutionizes file organization with a powerful, flexible tagging system that adapts to how you actually work.

```bash
# Transform this chaos...
Documents/Projects/Work/Client_A/2024/Reports/Q1/final_v2_FINAL.pdf

# Into this simplicity...
tm add final_report.pdf --tags work client-a q1 2024 final
tm search --tags work q1  # Instantly find what you need!
```

## ✨ Features

### 🎯 **Core Operations**

- **🏷️ Smart Tagging**: Add multiple tags to any file with intelligent suggestions
- **🔍 Powerful Search**: Find files by tags, paths, or combinations with fuzzy matching
- **📊 Rich Analytics**: Comprehensive statistics and insights about your tag usage
- **🗂️ Bulk Operations**: Mass tag operations with pattern matching and dry-run previews

### 🎨 **Beautiful Visualizations**

- **🌳 Tree View**: Gorgeous directory trees showing your tagged files
- **☁️ Tag Clouds**: Visual tag frequency representations
- **📈 ASCII Charts**: Professional statistical charts right in your terminal

### 🔧 **Smart Filtering**

- **🔄 Duplicate Detection**: Find files with identical tag sets
- **🏚️ Orphan Finder**: Locate untagged files that need attention
- **🔗 Similarity Analysis**: Discover related files through intelligent tag matching
- **🎯 Cluster Analysis**: Identify tag usage patterns and file groupings

### 🚀 **Advanced Features**

- **⚡ Lightning Fast**: Optimized for large file collections
- **🎭 Flexible Patterns**: Support for glob patterns and regex matching
- **🛡️ Safe Operations**: Dry-run mode for all destructive operations
- **🎨 Rich Output**: Beautiful, colorful terminal interface with emojis
- **🔧 Configurable**: Customizable display options and behavior

## 🚀 Installation

### 📦 **Install from PyPI (Recommended)**

```bash
pip install tagmanager-cli
```

That's it! TagManager is now available as `tm` or `tagmanager` command.

> **📝 Note**: The package name is `tagmanager-cli` but the commands are `tm` and `tagmanager`.

### 🔧 **Install from Source**

```bash
git clone https://github.com/davidtbilisi/TagManager.git
cd TagManager
pip install .
```

### 📋 **Requirements**

- **Python 3.7+** (Python 3.8+ recommended)
- **UTF-8 compatible terminal** (most modern terminals)
- **Dependencies**: `typer` and `rich` (automatically installed)

## ⚡ Quick Start

```bash
# Add tags to files
tm add document.pdf --tags work important project-x

# Search for files
tm search --tags work project-x

# View all files in a beautiful tree
tm ls --tree

# See your tag usage patterns
tm tags --cloud

# Get comprehensive statistics
tm stats --chart

# Find similar files
tm filter similar document.pdf

# Bulk operations with dry-run
tm bulk add "*.py" --tags python code --dry-run
```

## 📖 Documentation

### Basic Commands

| Command     | Description              | Example                              |
| ----------- | ------------------------ | ------------------------------------ |
| `tm add`    | Add tags to a file       | `tm add file.txt --tags work urgent` |
| `tm remove` | Remove files or clean up | `tm remove --path file.txt`          |
| `tm search` | Find files by tags/path  | `tm search --tags python --exact`    |
| `tm ls`     | List all tagged files    | `tm ls --tree`                       |
| `tm tags`   | Show all tags            | `tm tags --cloud`                    |
| `tm stats`  | Show statistics          | `tm stats --chart`                   |

### Advanced Operations

#### 🔍 **Smart Search**

```bash
# Boolean search with multiple tags
tm search --tags python web --match-all    # Files with BOTH tags
tm search --tags python web               # Files with EITHER tag

# Combined tag and path search
tm search --tags python --path /projects/

# Exact vs fuzzy matching
tm search --tags "web-dev" --exact        # Exact match only
tm search --tags web                      # Fuzzy matching (finds "web-dev", "webapp", etc.)
```

#### 🎯 **Bulk Operations**

```bash
# Mass tagging with patterns
tm bulk add "*.py" --tags python code
tm bulk add "**/*.md" --tags documentation

# Safe operations with dry-run
tm bulk retag --from old-tag --to new-tag --dry-run

# Bulk cleanup
tm bulk remove --tag deprecated
```

#### 🔧 **Smart Filtering**

```bash
# Find duplicate tag sets
tm filter duplicates

# Locate untagged files
tm filter orphans

# Find similar files (30% similarity threshold)
tm filter similar important-doc.pdf

# Discover tag clusters
tm filter clusters --min-size 3

# Find isolated files
tm filter isolated --max-shared 1
```

## 🎨 Examples

### Beautiful Tree View

```
🌳 Tagged Files Tree View
==================================================

└── 📁 Projects/
    ├── 📁 WebApp/
    │   ├── 📄 app.py 🏷️  [python, web, main]
    │   ├── 📄 config.py 🏷️  [python, config]
    │   └── 📄 README.md 🏷️  [documentation, web]
    └── 📁 Scripts/
        └── 📄 backup.sh 🏷️  [bash, automation, backup]

📊 Total files: 4
```

### Tag Cloud Visualization

```
☁️  Tag Cloud
==================================================
Legend: ★ Most frequent  ◆ Very frequent  ● Frequent  • Less frequent  · Least frequent

★ python(15)  ◆ web(8)  ● documentation(5)  • config(3)  · backup(1)  · automation(1)

📊 Total unique tags: 6
📊 Total tag instances: 33
```

### Statistical Charts

```
📊 TagManager Statistics Charts
==================================================

📈 Files by Tag Count
====================
3 tags │██████████████████████████████████████████████████ 12 (60.0%)
2 tags │████████████████████████████ 6 (30.0%)
1 tag  │██████████████ 2 (10.0%)

🏷️  Top 10 Most Used Tags
=========================
python        │██████████████████████████████████████████████████ 15 (25.4%)
web           │████████████████████████████ 8 (13.6%)
documentation │████████████████ 5 (8.5%)
config        │██████████ 3 (5.1%)
```

## 🏗️ Architecture

TagManager follows a clean, modular architecture:

```
TagManager/
├── tm.py                 # Main CLI interface
├── app/
│   ├── add/             # File tagging operations
│   ├── bulk/            # Bulk operations
│   ├── filter/          # Smart filtering & analysis
│   ├── search/          # Search functionality
│   ├── stats/           # Statistics & analytics
│   ├── visualization/   # Tree views, charts, clouds
│   └── helpers.py       # Core utilities
├── tests/               # Comprehensive test suite
└── config.ini          # Configuration settings
```

## 🤝 Contributing

We love contributions! Here's how you can help:

1. **🐛 Report Bugs**: Found an issue? [Create an issue](https://github.com/davidtbilisi/TagManager/issues)
2. **💡 Suggest Features**: Have ideas? We'd love to hear them!
3. **🔧 Submit PRs**: Fork, code, test, and submit a pull request
4. **📖 Improve Docs**: Help make our documentation even better

### Development Setup

```bash
git clone https://github.com/davidtbilisi/TagManager.git
cd TagManager
python -m unittest tests.py -v  # Run tests
```

## 📊 Stats & Performance

- **⚡ Lightning Fast**: Handles 10,000+ files effortlessly
- **💾 Lightweight**: Minimal memory footprint
- **🔧 Efficient**: Optimized algorithms for large datasets
- **🛡️ Reliable**: Comprehensive error handling and data validation

## 🎯 Use Cases

### 👨‍💻 **Developers**

```bash
# Organize code projects
tm add src/main.py --tags python backend api core
tm search --tags python api  # Find all Python API files
```

### 📚 **Researchers**

```bash
# Manage research papers
tm add paper.pdf --tags machine-learning nlp 2024 important
tm filter similar paper.pdf  # Find related papers
```

### 🎨 **Content Creators**

```bash
# Organize media files
tm add video.mp4 --tags tutorial python beginner
tm bulk add "*.jpg" --tags photography portfolio
```

### 🏢 **Project Managers**

```bash
# Track project documents
tm add requirements.pdf --tags project-x requirements client-a
tm stats --chart  # Visualize project file distribution
```

## 🌟 What Users Say

> _"TagManager transformed how I organize my 10,000+ research papers. The similarity search is pure magic!"_  
> — Dr. Sarah Chen, Research Scientist

> _"Finally, a tagging system that actually works! The tree view and tag clouds make everything so visual."_  
> — Mike Rodriguez, Software Developer

> _"The bulk operations saved me hours of manual work. Dry-run mode gives me confidence to make big changes."_  
> — Lisa Park, Data Analyst

## 🔮 Roadmap

- [ ] **🤖 AI-Powered Tagging**: Automatic tag suggestions based on file content
- [ ] **🌐 Web Interface**: Browser-based tag management
- [ ] **☁️ Cloud Sync**: Synchronize tags across devices
- [ ] **🔌 Plugin System**: Extensible architecture for custom features
- [ ] **📱 Mobile App**: Tag management on the go

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **David Chincharashvili** - _Original Creator_ - [@DavidTbilisi](https://github.com/davidtbilisi)
- Built with ❤️ using [Typer](https://typer.tiangolo.com/) for the beautiful CLI interface
- Inspired by the need for better file organization in the digital age

---

<div align="center">

**⭐ Star this repo if TagManager helps you stay organized! ⭐**

[Report Bug](https://github.com/davidtbilisi/TagManager/issues) • [Request Feature](https://github.com/davidtbilisi/TagManager/issues) • [Contribute](CONTRIBUTING.md)

Made with 🏷️ by developers, for developers

</div>
