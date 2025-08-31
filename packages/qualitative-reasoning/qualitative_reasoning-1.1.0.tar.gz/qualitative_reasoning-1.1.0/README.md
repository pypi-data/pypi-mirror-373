# 💰 Support This Research - Please Donate!

**🙏 If this library helps your research or project, please consider donating to support continued development:**

**[💳 DONATE VIA PAYPAL - CLICK HERE](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS)**

[![CI](https://github.com/benedictchen/qualitative-reasoning/workflows/CI/badge.svg)](https://github.com/benedictchen/qualitative-reasoning/actions)
[![PyPI version](https://badge.fury.io/py/qualitative-reasoning.svg)](https://badge.fury.io/py/qualitative-reasoning)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Custom%20Non--Commercial-red.svg)](LICENSE)

---

# Qualitative Reasoning

🤔 Commonsense physics simulation

**Forbus, K. D. (1984) - "Qualitative process theory"**

## 📦 Installation

```bash
pip install qualitative-reasoning
```

## 🚀 Quick Start

```python
import qualitative_reasoning
import numpy as np

# Create qualitative reasoner
reasoner = qualitative_reasoning.QualitativeReasoner()

# Define qualitative variables
temperature = qualitative_reasoning.QualitativeQuantity(
    'temperature', 
    ['cold', 'warm', 'hot']
)

pressure = qualitative_reasoning.QualitativeQuantity(
    'pressure',
    ['low', 'medium', 'high']
)

# Create qualitative state
state = qualitative_reasoning.QualitativeState({
    'temperature': 'warm',
    'pressure': 'medium'
})

# Perform envisionment
env = qualitative_reasoning.QualitativeEnvisionment(reasoner)
transitions = env.generate_transitions(state)

print(f"✅ Possible transitions: {len(transitions)}")
for transition in transitions:
    print(f"   → {transition}")
```

## 🎓 About the Implementation

Implemented by **Benedict Chen** - bringing foundational AI research to modern Python.

📧 Contact: benedict@benedictchen.com

## 📖 Citation

If you use this implementation in your research, please cite the original paper:

```bibtex
Forbus, K. D. (1984) - "Qualitative process theory"
```

## 📜 License

Custom Non-Commercial License with Donation Requirements - See LICENSE file for details.

---

## 💰 Support This Work - Donation Appreciated!

**This implementation represents hundreds of hours of research and development. If you find it valuable, please consider donating:**

**[💳 DONATE VIA PAYPAL - CLICK HERE](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS)**

**Your support helps maintain and expand these research implementations! 🙏**