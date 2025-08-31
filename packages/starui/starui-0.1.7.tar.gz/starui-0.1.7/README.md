# StarUI

**Python-first UI component library for StarHTML applications**

Modern, type-safe components with shadcn/ui styling and zero-configuration setup.

[![PyPI version](https://badge.fury.io/py/starui.svg)](https://badge.fury.io/py/starui)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Type checked: pyright](https://img.shields.io/badge/type%20checked-pyright-informational.svg)](https://github.com/microsoft/pyright)

## ✨ Features

- 🎨 **shadcn/ui components** - Pixel-perfect implementations with modern design
- ⚡ **Zero configuration** - Works out of the box with sensible defaults  
- 🚯 **StarHTML native** - Built specifically for StarHTML applications
- 📱 **Responsive design** - Mobile-first with Tailwind CSS v4
- 🔒 **Type-safe APIs** - Excellent developer experience with pragmatic typing
- 🚀 **Modern Python** - Python 3.12+ with latest language features

## 🚀 Quick Start

### Installation

```bash
# With pip
pip install starui

# With uv (recommended)
uv add starui
```

### Create Your First Project

```bash
# Initialize a new StarUI project
star init my-app
cd my-app

# Add some components  
star add button
star add card

# Run development server
star dev app.py
```

### Basic Usage

```python
from starhtml import *
from starui import *  # Gets all components automatically

# Create a StarHTML app
app, rt = star_app()

@rt("/")
def home():
    return Card(
        CardHeader(
            CardTitle("Welcome to StarUI")
        ),
        CardContent(
            Button("Get Started", variant="default"),
            Button("Learn More", variant="outline")
        )
    )

if __name__ == "__main__":
    serve()
```

## 📦 Available Components

| Component | Description | Variants |
|-----------|-------------|----------|
| **Button** | Interactive buttons | `default`, `destructive`, `outline`, `secondary`, `ghost`, `link` |
| **Alert** | Important messages | `default`, `destructive` |
| **Badge** | Status indicators | `default`, `secondary`, `destructive`, `outline` |
| **Card** | Content containers | Header, Content, Footer sections |
| **Input** | Form inputs | All HTML input types with validation |
| **Label** | Form labels | Accessible form labeling |

## 🛠 CLI Commands

```bash
# Project initialization
star init <project-name>          # Create new StarUI project

# Component management  
star add <component>              # Add component to project
star list                         # List available components

# Development
star dev <app.py>                 # Development server with hot reload
star build                        # Build production CSS
```

## 🎯 Component API

### Button Example

```python
from starui import Button  # Or: from starui import *

# Basic usage
Button("Click me")

# With variants and props
Button(
    "Submit Form",
    variant="default",
    size="lg", 
    disabled=False,
    type="submit",
    onclick="handleSubmit()"
)
```

### Card Example

```python
from starui import *  # Gets Card, CardHeader, CardTitle, CardContent, Button, etc.

Card(
    CardHeader(
        CardTitle("Product Card")
    ),
    CardContent(
        P("This is the card content with detailed information."),
        Button("Learn More", variant="outline")
    ),
    class_name="max-w-md"
)
```

## ⚙️ Configuration

StarUI works with zero configuration, but you can customize it:

```python
# starui.config.py (optional)
from starui.config import ProjectConfig
from pathlib import Path

config = ProjectConfig(
    project_root=Path.cwd(),
    css_output=Path("static/css/starui.css"),
    component_dir=Path("components/ui")
)
```

## 🔗 StarHTML Integration

StarUI is built specifically for [StarHTML](https://github.com/banditburai/starhtml):

```python
from starhtml import *
from starui import Button, Alert

app, rt = star_app(
    hdrs=(
        Link(rel="stylesheet", href="/static/css/starui.css"),
    )
)

@rt("/")
def home():
    return Div(
        Alert(
            "Welcome to your new StarUI app!",
            variant="default"
        ),
        Button("Get Started", variant="default"),
        cls="p-8 max-w-md mx-auto"
    )
```

## 💻 Development

### Setup

```bash
# Clone the repository
git clone https://github.com/banditburai/starui.git
cd starui

# Install with uv (recommended)
uv sync --all-extras

# Or with pip  
pip install -e ".[dev]"
```

### Quality Checks

```bash
# Run all quality checks
uv run ruff check                 # Linting
uv run ruff format --check        # Formatting  
uv run pyright                    # Type checking
uv run pytest tests/ -v           # Testing
```

### Building

```bash
uv build                          # Build package
uv run star --version             # Test CLI
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-component`)  
3. Make your changes with tests
4. Run quality checks (`uv run ruff check && uv run pyright && uv run pytest`)
5. Submit a Pull Request

## 🙏 Acknowledgments

- [shadcn/ui](https://ui.shadcn.com/) - Design system and component inspiration
- [StarHTML](https://github.com/banditburai/starhtml) - The amazing Python web framework
- [Tailwind CSS](https://tailwindcss.com/) - Utility-first CSS framework
- [FastHTML](https://fastht.ml/) - Inspiration for Python-first web development

---

**Made with ❤️ for the Python web development community**