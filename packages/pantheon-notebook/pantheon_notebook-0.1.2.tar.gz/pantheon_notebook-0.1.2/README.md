# Pantheon Notebook

A JupyterLab extension that integrates Pantheon CLI capabilities into Jupyter notebooks through a floating input widget.

## Features

- 🎯 **Floating Input Widget**: A non-intrusive floating panel at the bottom of JupyterLab
- 💬 **Natural Language to Code**: Generate code using natural language descriptions
- ⌨️ **Keyboard Shortcuts**: 
  - `Enter`: Send query
  - `Ctrl/Cmd + Enter`: Send query (alternative)
  - `Shift + Enter`: New line in input
  - `Ctrl + Up/Down`: Navigate query history
- 🔄 **Query History**: Access previous queries easily
- 📝 **Direct Cell Insertion**: Generated code is automatically inserted into notebook cells
- 🎨 **Theme Support**: Adapts to JupyterLab light/dark themes

## Installation

### Development Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/pantheon-notebook.git
cd pantheon-notebook
```

2. Install the package in development mode:
```bash
# Install package dependencies
pip install -e .

# Link your development version of the extension with JupyterLab
jupyter labextension develop . --overwrite

# Rebuild extension TypeScript source after making changes
jlpm build
```

3. Start JupyterLab:
```bash
jupyter lab
```

### Production Installation

```bash
pip install pantheon-notebook
```

## Development

### Setup

```bash
# Install dependencies
jlpm install

# Build TypeScript source
jlpm build

# Build TypeScript source in watch mode
jlpm watch

# Build extension
jlpm build:labextension
```

### Project Structure

```
pantheon-notebook/
├── src/                          # TypeScript source files
│   ├── index.ts                 # Extension entry point
│   └── widget.ts                # Floating input widget implementation
├── style/                       # CSS styles
│   └── index.css               # Widget styles
├── pantheon_notebook/          # Python package
│   └── __init__.py            # Python package initialization
├── package.json                # Node.js package configuration
├── tsconfig.json              # TypeScript configuration
└── pyproject.toml             # Python package configuration
```

## Usage

1. Open JupyterLab
2. The Pantheon floating widget will appear at the bottom of the interface
3. Type your query in natural language (e.g., "Load data.csv and show first 5 rows")
4. Press Enter to generate code
5. The generated code will be inserted as a new cell in your notebook
6. Edit the generated code as needed

## Roadmap

- [ ] Backend integration with Pantheon CLI
- [ ] Streaming code generation
- [ ] Context-aware code generation (analyze existing notebook cells)
- [ ] Support for multiple programming languages (Python, R, Julia)
- [ ] Code execution options (auto-execute, preview mode)
- [ ] Advanced UI features (code preview, syntax highlighting)
- [ ] Export/import query history
- [ ] Collaborative features

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT

http://127.0.0.1:8888/lab?token=b68740cbea579cb06fbaf61e54fa5093efa041674915814