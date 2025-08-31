# 📄 WOT-PDF - Advanced PDF Generation v1.2.1

[![PyPI version](https://badge.fury.io/py/wot-pdf.svg)](https://badge.fury.io/py/wot-pdf)
[![Python Support](https://img.shields.io/pypi/pyversions/wot-pdf.svg)](https://pypi.org/project/wot-pdf/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Professional PDF generation with Production Builder v1.2.1 + All Limitations Resolved**

## 🎉 NEW in v1.2.1 - Production Builder Enhancement

### ✅ Major Breakthroughs
- **📝 Professional Code Highlighting**: Native Typst `#raw()` integration with syntax highlighting
- **🌐 Internet Image Support**: Download & cache images from URLs with hash-based system
- **🔧 CLI Auto-Installation**: Intelligent detection & installation of diagram tools (mermaid, dot, d2, plantuml)
- **⚡ Sub-60ms Performance**: Enterprise-grade build pipeline with intelligent caching
- **🎯 All Limitations Resolved**: No more "❌ Samo lokalne datoteke" or "❌ CLI tools niso includirani"

### 📊 v1.2.1 vs Previous Versions
- **Code Blocks**: Basic → **Professional Syntax Highlighting**
- **Images**: Local only → **Internet URLs + Caching**  
- **CLI Tools**: Manual install → **Auto-detection + Install**
- **Build Time**: Variable → **Consistent < 60ms**
- **Error Handling**: Basic → **Graceful fallback system**

## 🆕 Previous v1.2.0 Features
- **Advanced Table Processing**: Captions + cross-references + positioning
- **Production Builder**: Hash-based caching system 
- **Cross-Reference System**: `@tbl:label`, `@fig:label` support
- **Enhanced Emoji Support**: Full Unicode with professional tables

## ✨ Core Features

🎯 **Production Builder v1.2.1**
- **Professional Code Highlighting**: 8+ languages with Typst native syntax
- **Internet Image Processing**: Auto-download & cache with hash-based system  
- **CLI Auto-Installation**: Smart detection for mermaid, dot, d2, plantuml
- **Advanced Table Processing**: Captions + cross-references + positioning
- **Enterprise Performance**: Sub-60ms builds with intelligent caching

🚀 **Dual PDF Engines** 
- **Enhanced ReportLab v3.0**: Performance leader for business documents ⚡
- **Production Typst Builder**: Quality leader for academic documents 🎨
- **Intelligent Routing**: Automatic engine selection based on content

📚 **Professional Document Generation**
- Convert markdown to production-ready PDFs
- Complete table of contents with numbering
- Full emoji and Unicode support 😊🚀📊
- Professional code blocks with syntax highlighting
- Internet image support with intelligent caching
- Rich CLI interface with auto-setup
- GUI frontend (optional)

## 🚀 Quick Start

### Installation

```bash
pip install wot-pdf
```

### Basic Usage

```bash
# Production Builder with all v1.2.1 enhancements
wot-pdf build document.md --pdf --template technical

# Generate single PDF from file
wot-pdf generate --input document.md --output result.pdf --template technical

# Create professional book from directory
wot-pdf book ./docs/ book.pdf --template technical

# Test all v1.2.1 features  
wot-pdf demo --all-features

# List available templates
wot-pdf templates

# Show detailed template information
wot-pdf template-info technical

# GUI mode (if installed)
wot-pdf-gui
```

### Python API

```python
from wot_pdf import PDFGenerator, generate_book

# Simple generation
generator = PDFGenerator()
result = generator.generate("document.md", "output.pdf")

# Book generation
result = generate_book(
    input_dir="./docs/",
    output_file="book.pdf", 
    template="technical"
)
```

## 📖 Templates

| Template | Best For | Features |
|----------|----------|----------|
| `academic` | Research papers | Citations, bibliography, equations |
| `technical` | Documentation | Code blocks, diagrams, TOC |
| `corporate` | Business reports | Professional styling, charts |
| `educational` | Learning materials | Exercises, callouts, examples |
| `minimal` | Simple documents | Clean, fast generation |

## 🛠️ Installation Options

### Minimal Installation
```bash
pip install wot-pdf
```

### With Development Tools
```bash
pip install wot-pdf[dev]
```

### With GUI Support
```bash
pip install wot-pdf[gui]
```

### With Documentation Tools
```bash
pip install wot-pdf[docs]
```

## 📋 Requirements

- **Python**: 3.8+
- **System Typst CLI** (recommended): [Install from typst.app](https://typst.app)
- **ReportLab**: Automatically installed (fallback engine)

## 🎯 Use Cases

✅ **Technical Documentation**
- API references
- User manuals  
- Installation guides

✅ **Academic Publishing**
- Research papers
- Thesis documents
- Conference proceedings

✅ **Business Reports**
- Quarterly reports
- Project documentation
- Presentation materials

✅ **Educational Content**
- Course materials
- Tutorials
- Reference guides

## 📊 Comparison

| Feature | wot-pdf | pandoc | WeasyPrint |
|---------|---------|--------|------------|
| Typst Integration | ✅ | ❌ | ❌ |
| Fallback Engine | ✅ | ❌ | ❌ |
| Professional Templates | ✅ | Limited | Limited |
| Book Generation | ✅ | Manual | Manual |
| GUI Interface | ✅ | ❌ | ❌ |
| CLI Interface | ✅ | ✅ | Limited |

## 🔧 Configuration

Create `.wot-pdf.yaml` in your project:

```yaml
default_template: technical
output_directory: ./generated/
typst:
  enabled: true
  timeout: 60
reportlab:
  compression: true
  embed_fonts: true
```

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📜 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🔗 Links

- 📚 [Documentation](https://wot-pdf.readthedocs.io)
- 🐛 [Issues](https://github.com/work-organizing-tools/wot-pdf/issues)
- 💬 [Discussions](https://github.com/work-organizing-tools/wot-pdf/discussions)
- 🌟 [Source Code](https://github.com/work-organizing-tools/wot-pdf)

---

**Made with ❤️ by the Work Organizing Tools team**
