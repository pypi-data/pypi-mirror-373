# 🌿 ivybloom CLI

> **Command-line interface for ivy biosciences' computational biology and drug discovery platform**

[![PyPI version](https://badge.fury.io/py/ivybloom.svg)](https://badge.fury.io/py/ivybloom)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation](https://img.shields.io/badge/docs-latest-brightgreen.svg)](https://docs.ivybiosciences.com/cli)

Accelerate your computational biology research with powerful command-line tools for protein structure prediction, drug discovery, ADMET analysis, and workflow automation.

## 🚀 Quick Start

### Installation
```bash
pip install ivybloom
```

### Authentication
```bash
# Browser-based login (recommended)
ivybloom auth login --browser
```

### Your First Job
```bash
# Predict protein structure
ivybloom run esmfold protein_sequence=MKLLVLGLVGFGVGFGVGFGVGFGVGFGVGFG

# Monitor progress
ivybloom jobs list
```

## ✨ Key Features

### 🧬 **Computational Biology Tools**
- **Protein Structure Prediction**: ESMFold, AlphaFold integration
- **Drug Discovery**: REINVENT, fragment-based design
- **ADMET Analysis**: Comprehensive property prediction
- **Molecular Analysis**: Solubility, toxicity, bioavailability

### 🔗 **Advanced Workflows**
- **Job Chaining**: Link multiple analyses seamlessly
- **Parallel Execution**: Run multiple optimizations simultaneously  
- **Parameter Passing**: Results flow between pipeline stages
- **YAML Workflows**: Define complex multi-step processes

### 🎨 **Beautiful Interface**
- **Earth-Tone Design**: Professional, biology-inspired color scheme
- **Rich Formatting**: Progress bars, tables, status indicators
- **Multiple Formats**: JSON, YAML, CSV, table output
- **Real-Time Monitoring**: Live job progress tracking

### 🔐 **Enterprise Authentication**
- **Browser OAuth**: "Click here to login" experience
- **Device Flow**: Perfect for headless environments
- **API Keys**: Traditional authentication for automation
- **Secure Storage**: System keyring integration

## 📊 Platform Integration

The IvyBloom CLI seamlessly integrates with your existing workflow:
- **Shared Database**: Jobs appear in both CLI and web interface
- **Project Access**: Full project management capabilities
- **Account Management**: Usage tracking and limits
- **Cross-Platform**: macOS, Linux, Windows support

## 🔬 Research Use Cases

### Drug Discovery Pipeline
```bash
ivybloom workflows run protein_to_drug_pipeline.yaml \
    --input protein_sequence=MKLLVL... \
    --project-id drug-discovery-project
```

### Fragment-Based Design
```bash
ivybloom workflows run fragment_based_discovery.yaml \
    --input target_protein=structure.pdb \
    --parallel
```

### High-Throughput Screening
```bash
ivybloom workflows run virtual_screening.yaml \
    --input compound_library=compounds.sdf \
    --batch-size 10000
```

## 📚 Documentation

- **[Complete Documentation](docs/cli/README.md)** - Full feature guide
- **[Authentication Guide](docs/cli/guides/authentication.md)** - Setup and security
- **[Workflow Examples](docs/cli/examples/)** - Real-world pipelines
- **[API Reference](https://docs.ivybiosciences.com/api)** - Backend integration

## 🛠 Development

### Local Installation
```bash
git clone https://github.com/ivybiosciences/ivybloom-cli.git
cd ivybloom-cli
pip install -e .
```

### Testing
```bash
pip install -e ".[dev]"
pytest tests/
```

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

## 🆘 Support

- **Documentation**: [docs.ivybiosciences.com/cli](https://docs.ivybiosciences.com/cli)
- **Issues**: [GitHub Issues](https://github.com/ivybiosciences/ivybloom-cli/issues)
- **Email**: [support@ivybiosciences.com](mailto:support@ivybiosciences.com)

---

**🌿 Computational Biology & Drug Discovery at Your Fingertips**

*Built with ❤️ by [Ivy Biosciences](https://ivybiosciences.com)*
