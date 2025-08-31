# 💰 Support This Research - Please Donate!

**🙏 If this library helps your research or project, please consider donating to support continued development:**

**[💳 DONATE VIA PAYPAL - CLICK HERE](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS)**

[![CI](https://github.com/benedictchen/self-organizing-maps/workflows/CI/badge.svg)](https://github.com/benedictchen/self-organizing-maps/actions)
[![PyPI version](https://badge.fury.io/py/self-organizing-maps.svg)](https://badge.fury.io/py/self-organizing-maps)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Custom%20Non--Commercial-red.svg)](LICENSE)

---

# Self-Organizing Maps

🗺️ Unsupervised learning and visualization

**Kohonen, T. (1982) - "Self-organized formation of topologically correct feature maps"**

## 📦 Installation

```bash
pip install self-organizing-maps
```

## 🚀 Quick Start

```python
import self_organizing_maps
import numpy as np

# Create sample 2D data
data = np.random.randn(500, 3)

# Create SOM
som = self_organizing_maps.SelfOrganizingMap(
    map_size=(10, 10),
    input_dim=3,
    learning_rate=0.5
)

# Train the SOM
som.train(data, epochs=100)

# Find best matching unit for new data
test_point = np.random.randn(3)
winner = som.find_winner(test_point)
print(f"✅ Best matching unit: {winner}")

# Visualize with built-in tools
visualizer = self_organizing_maps.SOMVisualizer(som)
visualizer.plot_map()
```

## 🎓 About the Implementation

Implemented by **Benedict Chen** - bringing foundational AI research to modern Python.

📧 Contact: benedict@benedictchen.com

## 📖 Citation

If you use this implementation in your research, please cite the original paper:

```bibtex
Kohonen, T. (1982) - "Self-organized formation of topologically correct feature maps"
```

## 📜 License

Custom Non-Commercial License with Donation Requirements - See LICENSE file for details.

---

## 💰 Support This Work - Donation Appreciated!

**This implementation represents hundreds of hours of research and development. If you find it valuable, please consider donating:**

**[💳 DONATE VIA PAYPAL - CLICK HERE](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS)**

**Your support helps maintain and expand these research implementations! 🙏**