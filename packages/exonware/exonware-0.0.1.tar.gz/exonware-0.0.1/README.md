# eXonware - Complete Python Ecosystem

> **🏢 Enterprise-grade Python ecosystem: 6 powerful libraries in one simple install**

[![PyPI version](https://badge.fury.io/py/exonware.svg)](https://badge.fury.io/py/exonware)
[![Python versions](https://img.shields.io/pypi/pyversions/exonware.svg)](https://pypi.org/project/exonware/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Company](https://img.shields.io/badge/Company-eXonware.com-blue.svg)](https://exonware.com)

## 🌟 One Install, Six Powerful Libraries

eXonware is the complete Python ecosystem that replaces dozens of dependencies with 6 enterprise-grade libraries. Install once, get everything you need for production applications.

```bash
pip install exonware
```

## 🚀 The Complete Library Suite

### 🏗️ xSystem - Enterprise Framework
**`exonware-xsystem`** | [GitHub](https://github.com/exonware/xsystem) | [PyPI](https://pypi.org/project/exonware-xsystem/)

> *Enterprise-grade Python framework with AI-powered optimization, military-grade security, 17+ serialization formats, circuit breakers, and production monitoring.*

- 🔒 Military-grade security & encryption
- 📊 17+ serialization formats (JSON, YAML, TOML, BSON, MessagePack, etc.)
- 🧠 AI-powered performance optimization
- 🔄 Circuit breakers & automatic recovery
- 📈 Production monitoring & metrics

### 🌐 xNode - Node-Based Processing
**`exonware-xnode`** | [GitHub](https://github.com/Exonware/xNode) | [PyPI](https://pypi.org/project/exonware-xnode/)

> *Format-agnostic node-based data processing library for complex data transformations and workflows.*

- 🔄 Node-based data processing pipelines
- 📊 Format-agnostic data handling
- ⚡ High-performance transformations
- 🔗 Chain complex operations
- 🎯 Visual workflow representation

### 📊 xData - Data Manipulation
**`exonware-xdata`** | [GitHub](https://github.com/exonware/xdata) | [PyPI](https://pypi.org/project/exonware-xdata/)

> *Advanced data manipulation and processing library with powerful transformation capabilities.*

- 🔄 Advanced data transformations
- 📈 Statistical operations
- 🔍 Data analysis tools
- 💾 Multiple format support
- ⚡ Optimized performance

### 📋 xSchema - Schema Validation
**`exonware-xschema`** | [GitHub](https://github.com/exonware/xschema) | [PyPI](https://pypi.org/project/exonware-xschema/)

> *Schema validation and data structure definition library for robust data validation.*

- ✅ Comprehensive schema validation
- 🏗️ Data structure definitions
- 🔄 Type checking & conversion
- 📊 Multiple schema formats
- 🛡️ Input sanitization

### ⚡ xAction - Workflow Automation
**`exonware-xaction`** | [GitHub](https://github.com/Exonware/xaction) | [PyPI](https://pypi.org/project/exonware-xaction/)

> *Action-based workflow and automation library for intelligent process orchestration.*

- 🔄 Workflow orchestration
- ⚡ Action-based automation
- 🎯 Task scheduling
- 🔗 Process chaining
- 📊 Execution monitoring

### 🏛️ xEntity - Entity Management
**`exonware-xentity`** | [GitHub](https://github.com/Exonware/xentity) | [PyPI](https://pypi.org/project/exonware-xentity/)

> *Entity management and relationship modeling library for complex data relationships.*

- 🏛️ Entity relationship modeling
- 🔗 Relationship management
- 📊 Data modeling tools
- 💾 Persistence layer
- 🔍 Query capabilities

---

## 🎯 Installation Options

### Option 1: Complete Ecosystem (Recommended)
```bash
# Install all 6 libraries at once
pip install exonware
```

### Option 2: Individual Libraries
```bash
# Install specific libraries only
pip install exonware-xsystem exonware-xdata
```

### Option 3: Development Setup
```bash
# Install with development tools
pip install exonware[dev]
```

## 🏆 Why Choose eXonware?

### ✅ **Instead of This:**
```bash
pip install requests pydantic redis celery prometheus-client
pip install cryptography pyyaml msgpack bson toml lxml
pip install sqlalchemy pandas numpy scipy matplotlib
pip install jsonschema cerberus marshmallow voluptuous
# ... 50+ more dependencies
```

### ✅ **Just Use This:**
```bash
pip install exonware
```

## 🛠️ Quick Start

```python
# Import the entire ecosystem
import exonware

# Or import specific libraries
from exonware import xsystem, xdata, xschema, xaction, xentity, xnode

# Enterprise framework
app = xsystem.XSystem()

# Data processing pipeline
pipeline = xnode.create_pipeline()

# Data manipulation
processor = xdata.DataProcessor()

# Schema validation
validator = xschema.SchemaValidator()

# Workflow automation
workflow = xaction.WorkflowEngine()

# Entity management
entities = xentity.EntityManager()
```

## 🏢 Enterprise Ready

All eXonware libraries are designed for enterprise production:

- ✅ **Battle-Tested**: Production-proven in high-traffic applications
- ✅ **Zero Dependencies Conflict**: Carefully managed dependency tree
- ✅ **Monitoring Built-In**: Comprehensive metrics and observability
- ✅ **Security First**: Military-grade security by default
- ✅ **Performance Optimized**: AI-powered optimization
- ✅ **Compliance Ready**: Enterprise security standards

## 📚 Documentation

- **[Complete Documentation](https://github.com/exonware/exonware/tree/main/docs)** - Full ecosystem guide
- **[Individual Library Docs](https://github.com/exonware)** - Per-library documentation
- **[API Reference](https://github.com/exonware/exonware/wiki)** - Complete API documentation
- **[Examples](https://github.com/exonware/exonware/tree/main/examples)** - Practical usage examples

## 🤝 Support & Community

- 🌐 **Company**: [eXonware.com](https://exonware.com)
- 📧 **Contact**: [connect@exonware.com](mailto:connect@exonware.com)
- 🐛 **Issues**: [GitHub Issues](https://github.com/exonware/exonware/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/exonware/exonware/discussions)

## 📦 What's Included

When you `pip install exonware`, you automatically get:

| Library | Purpose | Version |
|---------|---------|---------|
| **xsystem** | Enterprise framework | >=0.0.1 |
| **xnode** | Node-based processing | >=0.0.1 |
| **xdata** | Data manipulation | >=0.0.1 |
| **xschema** | Schema validation | >=0.0.1 |
| **xaction** | Workflow automation | >=0.0.1 |
| **xentity** | Entity management | >=0.0.1 |

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

<div align="center">

**Built with ❤️ by [eXonware.com](https://exonware.com)**

*The complete Python ecosystem for enterprise applications*

**🚀 One install. Six libraries. Infinite possibilities.**

</div>